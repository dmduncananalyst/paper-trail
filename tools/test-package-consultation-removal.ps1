param([int]$Port=0,[int]$SitePort=8795,[switch]$Live,[string]$Output=(Join-Path $env:TEMP ('paper-trail-consultation-removal-browser-'+[guid]::NewGuid().ToString('N'))))
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot
$out=[IO.Path]::GetFullPath($Output)
if($out.StartsWith($root+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Browser output must stay outside the repository'}
New-Item -ItemType Directory -Path $out -Force | Out-Null
Write-Output ('Temporary browser results: '+$out)
$profile=Join-Path $out 'disposable-profile'
if(!$Port){$probe=[Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback,0);$probe.Start();$Port=$probe.LocalEndpoint.Port;$probe.Stop()}
$browser=Start-Process -FilePath 'C:/Program Files/Google/Chrome/Application/chrome.exe' -ArgumentList @('--headless=new','--disable-gpu','--no-first-run','--no-default-browser-check',"--remote-debugging-port=$Port",('--user-data-dir="'+$profile+'"'),'about:blank') -WindowStyle Hidden -PassThru
$origin=if($Live){'https://www.papertrailusa.com'}else{"http://127.0.0.1:$SitePort"}
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
  Cdp 'Page.navigate' @{url="$origin/$route"}|Out-Null
  $expected=('/'+$route.Split('#')[0])|ConvertTo-Json -Compress
  Wait ('location.pathname+location.search==='+$expected+'&&document.readyState==="complete"&&!!document.querySelector(".pt-nav[data-organized-navigation]")')
  Eval '(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>{i.loading="eager";return i.decode().catch(()=>{})}));return true})()'|Out-Null
 }
 Cdp 'Page.enable'|Out-Null;Cdp 'Runtime.enable'|Out-Null;Cdp 'Network.enable'|Out-Null
 $blocked=if($Live){@('https://*.googletagmanager.com/*','https://*.google-analytics.com/*','https://*.clarity.ms/*','https://*.hsforms.net/*','https://*.hsforms.com/*','https://*.hubspot.com/*','https://*.hubspot.net/*','https://*.googleapis.com/*','https://*.gstatic.com/*')}else{@('https://*')}
 Cdp 'Network.setBlockedURLs' @{urls=@($blocked)}|Out-Null
 $languages=@('','es/','fa/','hy/','zh-CN/','ko/','tl/','te/','ru/','ar/')
 $kinds=@('weekly-bookkeeping','monthly-bookkeeping','bookkeeping-repair','accounts-billing','financial-analysis','payroll')
 $widths=if($Live){@(1440,390)}else{@(1440,834,390)}
 foreach($width in $widths){
  Cdp 'Emulation.setDeviceMetricsOverride' @{width=$width;height=844;deviceScaleFactor=1;mobile=($width -lt 600)}|Out-Null
  foreach($language in $languages){
   Write-Output ('Checking package consultation removal: '+$width+' '+$(if($language){$language}else{'en'}))
   Eval '(()=>{try{localStorage.removeItem("paper-trail-language")}catch{}return true})()'|Out-Null
   foreach($kind in $kinds){
    Load ($language+$kind+'-packages.html')
    $state=Eval @'
(()=>{
 const cards=[...document.querySelectorAll('main .package-plan,main .repair-package')];
 const extra=[...document.querySelectorAll('main .pricing-category details.package-consultation')].filter(d=>!d.closest('.package-plan,.package-enterprise,.repair-package')&&!d.classList.contains('inline-consultation'));
 const retained=[...document.querySelectorAll('main .page-conversation details.package-consultation')];
 const quoteLinks=cards.flatMap(c=>[...c.querySelectorAll('a')]).map(a=>a.getAttribute('href'));
 const consult=retained[0];let consultationWorks=false;
 if(consult){consult.querySelector('summary').click();consultationWorks=consult.open&&consult.querySelectorAll('a').length===2;consult.open=false}
 return {extras:extra.length,cards:cards.length,quotes:quoteLinks.length,quoteLinks,retained:retained.length,consultationWorks,overflow:document.documentElement.scrollWidth>innerWidth+2,brokenImages:[...document.images].filter(i=>!i.naturalWidth).length};
})()
'@
    Assert ($state.extras -eq 0) ('Redundant standalone control remains: '+$language+$kind)
    Assert ($state.cards -eq 4 -and $state.retained -eq 1 -and $state.consultationWorks) ('Existing cards or shared consultation controls failed: '+$language+$kind)
    Assert (!$state.overflow -and !$state.brokenImages) ('Layout failure: '+$language+$kind)
    if($kind -in @('monthly-bookkeeping','accounts-billing')){Assert ($state.quotes -eq 1) 'Enterprise quote button changed'}
    if($kind -in @('financial-analysis','payroll')){Assert ($state.quotes -eq 4) 'Pricing-card quote buttons changed'}
    $results.Add(@{width=$width;route=$language+$kind+'-packages.html';state=$state})
    if($kind -eq 'accounts-billing' -and $language -eq '' -and $width -in @(1440,390)){
     $shot=Cdp 'Page.captureScreenshot' @{format='png';captureBeyondViewport=$true}
     [IO.File]::WriteAllBytes((Join-Path $out ('accounts-billing-'+$width+'.png')),[Convert]::FromBase64String($shot.data))
    }
   }
  }
 }
 Assert ($script:exceptions.Count -eq 0) ('JavaScript exceptions: '+($script:exceptions -join ', '))
 Assert (@($script:requests|Where-Object {$_.method -notin @('GET','HEAD','OPTIONS')}).Count -eq 0) 'Unexpected write request'
 @{page_viewport_checks=$results.Count;languages=10;widths=$widths;live=[bool]$Live;javascript_errors=$script:exceptions;forms_submitted=0;checks=$results}|ConvertTo-Json -Depth 10|Set-Content -LiteralPath (Join-Path $out 'results.json') -Encoding UTF8
 Write-Output ('PASS: '+$results.Count+' package-page checks. Results: '+$out)
}finally{
 if($socket){$socket.Dispose()}
 if($browser -and !$browser.HasExited){Stop-Process -Id $browser.Id -ErrorAction SilentlyContinue}
}
