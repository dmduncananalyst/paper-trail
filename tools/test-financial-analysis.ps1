param([int]$Port=9293,[int]$SitePort=8793,[string]$Output=(Join-Path $env:TEMP ('paper-trail-financial-browser-'+[guid]::NewGuid().ToString('N'))))
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot
$out=[IO.Path]::GetFullPath($Output)
if($out.StartsWith($root+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Browser output must stay outside the repository'}
New-Item -ItemType Directory -Path $out -Force | Out-Null
Write-Output ('Temporary browser results: '+$out)
$profile=Join-Path $out 'disposable-profile'
$browser=Start-Process -FilePath 'C:/Program Files/Google/Chrome/Application/chrome.exe' -ArgumentList @('--headless=new','--disable-gpu','--no-first-run','--no-default-browser-check',"--remote-debugging-port=$Port",('--user-data-dir="'+$profile+'"'),'about:blank') -WindowStyle Hidden -PassThru
$results=[Collections.Generic.List[object]]::new()
try{
 $target=$null
 for($i=0;$i -lt 60;$i++){try{$targets=Invoke-RestMethod "http://127.0.0.1:$Port/json" -TimeoutSec 2;$target=$targets | Where-Object type -EQ 'page' | Select-Object -First 1;if($target){break}}catch{};Start-Sleep -Milliseconds 250}
 if(!$target){throw 'Disposable headless browser unavailable'}
 $socket=[Net.WebSockets.ClientWebSocket]::new()
 $socket.ConnectAsync([uri]$target.webSocketDebuggerUrl,[Threading.CancellationToken]::None).GetAwaiter().GetResult()
 $script:requestId=0;$script:exceptions=@();$script:requests=@()
 function Cdp($method,$params=@{}){
  $script:requestId++;$id=$script:requestId
  $bytes=[Text.Encoding]::UTF8.GetBytes((@{id=$id;method=$method;params=$params}|ConvertTo-Json -Depth 20 -Compress))
  $socket.SendAsync([ArraySegment[byte]]::new($bytes),[Net.WebSockets.WebSocketMessageType]::Text,$true,[Threading.CancellationToken]::None).GetAwaiter().GetResult()
  while($true){
   $stream=[IO.MemoryStream]::new()
   do{$buffer=New-Object byte[] 65536;$read=$socket.ReceiveAsync([ArraySegment[byte]]::new($buffer),[Threading.CancellationToken]::None).GetAwaiter().GetResult();$stream.Write($buffer,0,$read.Count)}while(!$read.EndOfMessage)
   $reply=[Text.Encoding]::UTF8.GetString($stream.ToArray())|ConvertFrom-Json;$stream.Dispose()
   if($reply.method -eq 'Runtime.exceptionThrown'){$script:exceptions+=$reply.params.exceptionDetails.text}
   if($reply.method -eq 'Network.requestWillBeSent'){$script:requests+=@{url=$reply.params.request.url;method=$reply.params.request.method}}
   if($reply.id -eq $id){if($reply.error){throw ($reply.error|ConvertTo-Json -Compress)};return $reply.result}
  }
 }
 function Eval($expression){$r=Cdp 'Runtime.evaluate' @{expression=$expression;awaitPromise=$true;returnByValue=$true};if($r.exceptionDetails){throw ($r.exceptionDetails|ConvertTo-Json -Depth 6)};return $r.result.value}
 function Assert($condition,$message){if(!$condition){throw $message}}
 function Wait($condition){for($attempt=0;$attempt -lt 120;$attempt++){try{if(Eval $condition){return}}catch{};Start-Sleep -Milliseconds 100};throw ('Browser condition timed out: '+$condition)}
 function Load($route){
  Cdp 'Page.navigate' @{url="http://127.0.0.1:$SitePort/$route"}|Out-Null
  $expected=('/'+$route.Split('#')[0])|ConvertTo-Json -Compress
  Wait ('location.pathname+location.search==='+$expected+'&&document.readyState==="complete"&&!!document.querySelector(".pt-nav #navigation-services")')
  Eval '(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>{i.loading="eager";return i.decode().catch(()=>{})}));return true})()'|Out-Null
 }
 Cdp 'Page.enable'|Out-Null;Cdp 'Runtime.enable'|Out-Null;Cdp 'Network.enable'|Out-Null
 Cdp 'Network.setBlockedURLs' @{urls=@('https://*')}|Out-Null
 Load 'financial-analysis.html'
 foreach($savedLanguage in @('es','ar')){
  Eval ('localStorage.setItem("paper-trail-language","'+$savedLanguage+'")')|Out-Null
  Cdp 'Page.navigate' @{url="http://127.0.0.1:$SitePort/request-a-custom-quote.html?service=financial-analysis"}|Out-Null
  Wait ('location.pathname==="/'+$savedLanguage+'/request-a-custom-quote.html"&&location.search==="?service=financial-analysis"&&document.readyState==="complete"')
  Assert (Eval ('(()=>{const form=document.querySelector("#quote-questionnaire");return document.documentElement.dataset.staticLocale==="'+$savedLanguage+'"&&form?.dataset.serviceKey==="financial-analysis"&&!form.hidden})()')) 'Saved language or Financial Analysis preselection did not survive navigation'
 }
 Eval 'localStorage.removeItem("paper-trail-language")'|Out-Null
 foreach($width in @(1440,768,390)){
  Write-Output ('Checking page, consultation and quote interactions at '+$width+'px')
  Cdp 'Emulation.setDeviceMetricsOverride' @{width=$width;height=1000;deviceScaleFactor=1;mobile=($width -lt 600)}|Out-Null
  foreach($route in @('financial-analysis.html','financial-analysis-packages.html','request-a-custom-quote.html','request-a-custom-quote.html?service=financial-analysis#quote-questionnaire')){
   Load $route
   $layout=Eval '(()=>{const nav=[...document.querySelectorAll("#navigation-services>a")].filter(a=>a.pathname==="/financial-analysis.html");return {overflow:document.documentElement.scrollWidth>innerWidth+2,brokenImages:[...document.images].filter(i=>!i.naturalWidth).map(i=>i.getAttribute("src")),navCount:nav.length,plainLink:!nav[0]?.hasAttribute("aria-haspopup"),destination:nav[0]?.pathname}})()'
   Assert (!$layout.overflow) "Horizontal overflow: $width $route"
   Assert ($layout.brokenImages.Count -eq 0) "Broken image: $width $route"
   Assert ($layout.navCount -eq 1 -and $layout.plainLink -and $layout.destination -eq '/financial-analysis.html') "Invalid Services menu destination: $width $route"
   $results.Add(@{width=$width;route=$route;layout=$layout})
   if($route -in @('financial-analysis.html','financial-analysis-packages.html')){
    $scope=if($route -eq 'financial-analysis.html'){'.two-primary-actions'}else{'main'}
    $expectedQuotes=if($route -eq 'financial-analysis.html'){1}else{4}
    $cta=Eval ('(()=>{const s=document.querySelector("'+$scope+'"),controls=s.querySelectorAll("details.package-consultation"),d=controls[0];const closed=!d.open;d.querySelector("summary").click();return {closed,open:d.open,choices:[...d.querySelectorAll("a")].map(a=>a.href),consultations:controls.length,quotes:[...s.querySelectorAll("a")].filter(a=>new URL(a.href).searchParams.get("service")==="financial-analysis").length}})()')
    Assert ($cta.closed -and $cta.open -and $cta.choices.Count -eq 2 -and $cta.consultations -eq 1 -and $cta.quotes -eq $expectedQuotes) "Consultation reveal or CTA count failed: $width $route"
    Assert ($cta.choices[0] -eq 'https://calendar.app.google/CFU1yh6iQrCjEUZ2A' -and $cta.choices[1] -eq 'https://calendar.app.google/RuynVGfwUfYNiDnp9') 'Existing consultation destinations changed'
    $results.Add(@{width=$width;route=$route;cta=$cta})
    Eval ('document.querySelector("'+$scope+' details").open=false')|Out-Null
    $shot=Cdp 'Page.captureScreenshot' @{format='png';captureBeyondViewport=$true}
    [IO.File]::WriteAllBytes((Join-Path $out ($route.Replace('.html','')+'-'+$width+'.png')),[Convert]::FromBase64String($shot.data))
    # Follow the actual CTA to confirm preselection, then reload that URL.
    Eval ('document.querySelector("'+$scope+' a[href*=\"service=financial-analysis\"]").click()')|Out-Null
    Wait 'location.search==="?service=financial-analysis"&&document.readyState==="complete"&&!!document.querySelector("#quote-questionnaire")&&!document.querySelector("#quote-questionnaire").hidden'
    Assert (Eval 'location.search==="?service=financial-analysis"&&!document.querySelector("#quote-questionnaire").hidden') 'Quote CTA did not preselect Financial Analysis'
   }
  }
  Load 'request-a-custom-quote.html?service=financial-analysis#quote-questionnaire'
  $integration=Eval @'
(()=>{
 const q=document.querySelector('#quote-questionnaire'),p=document.querySelector('#financial-bookkeeping-package');
 const config=window.PAPER_TRAIL_QUOTE_CONFIG;
 window.__quoteWrites=[];
 window.HubSpotFormsV4={getFormFromEvent:()=>({getInstanceId:()=>'local-financial-test',setFieldValue:(name,value)=>__quoteWrites.push({name,value})})};
 const emit=(type,instanceId='local-financial-test')=>dispatchEvent(new CustomEvent(type,{detail:{formId:config.formId,instanceId}}));
 emit('hs-form-event:on-ready');
 const packages=[...p.options].slice(1).map(o=>o.value),mapped=[];
 for(const value of packages){p.value=value;p.dispatchEvent(new Event('change',{bubbles:true}));const last=__quoteWrites.at(-1);mapped.push(last.name==='0-1/message'&&last.value.includes('Selected service: Financial Analysis')&&last.value.includes('Existing bookkeeping package')&&last.value.includes('Answer: '+value))}
 emit('hs-form-event:on-submission:failed');
 const failed=!q.hidden&&!document.querySelector('#quote-submission-feedback').hidden&&p.value===packages.at(-1);
 emit('hs-form-event:on-submission:success','unrelated-instance');
 const isolated=!q.hidden;
 emit('hs-form-event:on-submission:success');
 const success=q.hidden&&q.inert&&!document.querySelector('#quote-success').hidden&&document.activeElement.id==='quote-success';
 return {packages,mapped,failed,isolated,success,portal:config.portalId,form:config.formId};
})()
'@
  Assert ($integration.packages.Count -eq 6 -and @($integration.mapped | Where-Object {!$_}).Count -eq 0 -and $integration.failed -and $integration.isolated -and $integration.success) 'Existing native form event integration failed'
  $results.Add(@{width=$width;mockedNativeIntegration=$integration})
  Load 'request-a-custom-quote.html?service=financial-analysis'
  Assert (Eval '!document.querySelector("#quote-questionnaire").hidden&&document.querySelector("#quote-questionnaire").dataset.service==="Financial Analysis"') 'Financial Analysis selection did not survive loading'
  Load 'request-a-custom-quote.html'
  Assert (Eval '(()=>{const cards=[...document.querySelectorAll(".selection-card")];return document.querySelector("#quote-questionnaire").hidden&&cards.length===6&&cards.some(card=>card.querySelector("a")?.pathname==="/payroll-custom-quote.html")})()') 'Existing service choices not preserved'
  foreach($key in @('monthly','billing','repair','weekly')){
   Load 'request-a-custom-quote.html'
   Eval ('document.querySelector("[data-quote-select='+$key+']").click()')|Out-Null
   Wait ('document.readyState==="complete"&&document.querySelector("#quote-questionnaire")?.dataset.serviceKey==="'+$key+'"')
   Assert (Eval ('document.querySelector("#quote-questionnaire")?.dataset.serviceKey==="'+$key+'"')) "Existing quote route failed: $key"
  }
 }
 foreach($route in @('index.html','accounts-billing.html','paper-trail-services.html','paper-trail-monthly-bookkeeping.html','state-records/california.html','es/index.html','tl/index.html','ar/index.html')){
  foreach($width in @(1440,1152,768,390)){
   Write-Output ('Checking shared navigation: '+$width+'px '+$route)
   Cdp 'Emulation.setDeviceMetricsOverride' @{width=$width;height=1000;deviceScaleFactor=1;mobile=($width -lt 600)}|Out-Null
   Load $route
   Assert (Eval 'document.documentElement.scrollWidth<=innerWidth+2') "Shared navigation overflow: $width $route"
   Assert (Eval '(()=>{const locale=document.documentElement.dataset.staticLocale||"en",target=(locale==="en"?"":"/"+locale)+"/financial-analysis.html";const links=[...document.querySelectorAll("#navigation-services>a")].filter(a=>a.pathname===target);return links.length===1&&!links[0].hasAttribute("aria-haspopup")})()') "Wrong localized service destination: $route"
   $results.Add(@{width=$width;route=$route;sharedNavigation='passed'})
  }
 }
 Assert ($script:exceptions.Count -eq 0) 'Uncaught browser JavaScript exception'
 Assert (@($script:requests | Where-Object {$_.method -notin @('GET','HEAD','OPTIONS')}).Count -eq 0) 'Unexpected submission request'
 @{results=$results.ToArray();exceptions=$script:exceptions;submissionRequests=0;nativeForm='Mocked events only; HTTPS dependencies blocked; no live HubSpot submission';output=$out}|ConvertTo-Json -Depth 12|Set-Content (Join-Path $out 'results.json') -Encoding UTF8
 Write-Output ('PASS: '+$results.Count+' browser checks. Screenshots and results: '+$out)
}finally{
 if($socket){$socket.Dispose()}
 if($browser -and !$browser.HasExited){Stop-Process -Id $browser.Id -ErrorAction SilentlyContinue}
}
