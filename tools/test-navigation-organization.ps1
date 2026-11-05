param([int]$Port=9293,[int]$SitePort=8793,[switch]$InteractionsOnly,[string]$Output=(Join-Path $env:TEMP ('paper-trail-navigation-browser-'+[guid]::NewGuid().ToString('N'))))
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
  Wait ('location.pathname+location.search==='+$expected+'&&document.readyState==="complete"&&!!document.querySelector(".pt-nav[data-organized-navigation]")')
  Eval '(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>{i.loading="eager";return i.decode().catch(()=>{})}));return true})()'|Out-Null
 }
 Cdp 'Page.enable'|Out-Null;Cdp 'Runtime.enable'|Out-Null;Cdp 'Network.enable'|Out-Null
 Cdp 'Network.setBlockedURLs' @{urls=@('https://*')}|Out-Null
 $languages=@('','es/','fa/','hy/','zh-CN/','ko/','tl/','te/','ru/','ar/')
 $kinds=@('weekly-bookkeeping','monthly-bookkeeping','bookkeeping-repair','accounts-billing','financial-analysis','payroll')
 $pages=@('all-services.html','packages.html')+@($kinds|ForEach-Object {$_+'-packages.html'})
 function Point($selector){Eval ('(()=>{const r=document.querySelector('+($selector|ConvertTo-Json -Compress)+').getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()')}
 function Mouse($selector){$point=Point $selector;Cdp 'Input.dispatchMouseEvent' @{type='mouseMoved';x=$point.x;y=$point.y}|Out-Null}
 function Tap($selector){$point=Point $selector;Cdp 'Input.dispatchTouchEvent' @{type='touchStart';touchPoints=@(@{x=$point.x;y=$point.y})}|Out-Null;Cdp 'Input.dispatchTouchEvent' @{type='touchEnd';touchPoints=@()}|Out-Null}
 if(!$InteractionsOnly){foreach($width in @(1440,1024,834,390)){
  Cdp 'Emulation.setDeviceMetricsOverride' @{width=$width;height=1000;deviceScaleFactor=1;mobile=($width -lt 600)}|Out-Null
  Cdp 'Emulation.setTouchEmulationEnabled' @{enabled=($width -le 834)}|Out-Null
  foreach($language in $languages){
   Write-Output ('Checking navigation and pages: '+$width+' '+$(if($language){$language}else{'en'}))
   Eval '(()=>{try{localStorage.removeItem("paper-trail-language")}catch{}return true})()'|Out-Null
   Load ($language+'all-services.html')
   $menu=Eval @'
(()=>{const nav=document.querySelector('.pt-nav'),items=[...nav.children],families=[...nav.querySelectorAll('.nav-family')];return {count:items.length,rows:new Set(items.map(i=>Math.round(i.getBoundingClientRect().top))).size,groups:families.length,nested:!!nav.querySelector('.nav-panel .nav-panel'),services:[...families[0].querySelectorAll('.nav-panel a')].map(a=>a.pathname),packages:[...families[1].querySelectorAll('.nav-panel a')].map(a=>a.pathname),arrows:[...nav.querySelectorAll('a')].some(a=>['before','after'].some(p=>!['none','normal','""'].includes(getComputedStyle(a,'::'+p).content)))}})()
'@
   Assert ($menu.count -eq 8 -and $menu.groups -eq 2 -and !$menu.nested -and !$menu.arrows) 'Invalid navigation structure or arrow indicator'
   if($width -ge 981){Assert ($menu.rows -eq 1) ('Desktop menu wrapped: '+$language+' '+$width)}
   Assert ($menu.services[0] -eq ('/'+$language+'all-services.html')) 'All Services route incorrect'
   Assert ($menu.packages[0] -eq ('/'+$language+'packages.html')) 'All Packages route incorrect'
   for($i=0;$i -lt 6;$i++){Assert ($menu.packages[$i+1] -eq ('/'+$language+$kinds[$i]+'-packages.html')) 'Package points to wrong route'}
   if($width -ge 981){
    Mouse '.pt-nav>.nav-family>a'
    Assert (Eval '!document.querySelector("#navigation-services").hidden') 'Hover did not open Services'
    Mouse '#navigation-services>a:nth-child(2)'
    Assert (Eval '!document.querySelector("#navigation-services").hidden') 'Services hover bridge failed'
    Mouse '.pt-nav>.nav-family:nth-of-type(2)>a'
    Assert (Eval '!document.querySelector("#navigation-packages").hidden') 'Hover did not open Packages'
    Mouse '#navigation-packages>a:nth-child(2)'
    Assert (Eval '!document.querySelector("#navigation-packages").hidden') 'Packages hover bridge failed'
    Eval 'document.querySelector(".pt-nav>.nav-family>a").click()'|Out-Null
    Wait ('location.pathname==="/'+$language+'all-services.html"&&document.readyState==="complete"')
   }else{
    Tap '.pt-nav>.nav-family>a'
    Assert (Eval '!document.querySelector("#navigation-services").hidden') 'Touch did not open Services'
    Tap '#navigation-services>a:first-child'
    Wait ('location.pathname==="/'+$language+'all-services.html"&&document.readyState==="complete"')
    Wait '!!document.querySelector(".pt-nav[data-organized-navigation]")'
    Tap '.pt-nav>.nav-family:nth-of-type(2)>a'
    Assert (Eval '!document.querySelector("#navigation-packages").hidden') 'Touch did not open Packages'
    Tap '#navigation-packages>a:nth-child(2)'
    Wait ('location.pathname==="/'+$language+'weekly-bookkeeping-packages.html"&&document.readyState==="complete"')
   }
   foreach($name in $pages){
    Load ($language+$name)
    $layout=Eval '({overflow:document.documentElement.scrollWidth>innerWidth+2,brokenImages:[...document.images].filter(i=>!i.naturalWidth).length,h1:document.querySelectorAll("main h1").length})'
    Assert (!$layout.overflow -and !$layout.brokenImages -and $layout.h1 -eq 1) ('Layout failure: '+$language+$name+' '+$width+' '+($layout|ConvertTo-Json -Compress))
    if($name -eq 'all-services.html'){
     Assert (Eval 'document.querySelectorAll(".service-overview-card").length===6&&document.querySelectorAll(".service-overview-card>.action").length===6&&!document.querySelector("main .package-plan")') 'Service cards failed'
    }
    if($name -eq 'packages.html'){
     Assert (Eval 'document.querySelectorAll(".category-overview-card").length===7&&document.querySelector(".category-overview-card:last-child").id==="bundle-save"&&!document.querySelector("main img,main .package-checklist")') 'Package overview cards failed'
    }
    $results.Add(@{width=$width;route=$language+$name;layout=$layout;menu=$menu})
   }
   if($language -in @('','ar/','hy/') -and $width -in @(1440,390)){
    foreach($name in @('all-services.html','monthly-bookkeeping-packages.html')){
     Load ($language+$name)
     $shot=Cdp 'Page.captureScreenshot' @{format='png';captureBeyondViewport=$true}
     [IO.File]::WriteAllBytes((Join-Path $out (($language.Replace('/','')+$name.Replace('.html','')+'-'+$width)+'.png')),[Convert]::FromBase64String($shot.data))
    }
   }
  }
 }
 }
 Cdp 'Emulation.setDeviceMetricsOverride' @{width=1440;height=1000;deviceScaleFactor=1;mobile=$false}|Out-Null
 Cdp 'Emulation.setTouchEmulationEnabled' @{enabled=$false}|Out-Null
 $serviceRoutes=@('weekly-bookkeeping.html','paper-trail-monthly-bookkeeping.html','paper-trail-services.html','accounts-billing.html','financial-analysis.html','payroll.html')
 foreach($language in $languages){
  Write-Output ('Checking selectors, keyboard and actual card navigation: '+$(if($language){$language}else{'en'}))
  Load ($language+'all-services.html')
  Eval 'document.querySelector(".pt-nav>.nav-family>a").focus()'|Out-Null
  Cdp 'Input.dispatchKeyEvent' @{type='keyDown';key='ArrowDown';code='ArrowDown';windowsVirtualKeyCode=40}|Out-Null
  Assert (Eval '!document.querySelector("#navigation-services").hidden&&document.activeElement===document.querySelector("#navigation-services>a")') 'Keyboard cannot enter Services dropdown'
  Cdp 'Input.dispatchKeyEvent' @{type='keyDown';key='Escape';code='Escape';windowsVirtualKeyCode=27}|Out-Null
  Assert (Eval 'document.querySelector("#navigation-services").hidden') 'Escape did not close dropdown'
  for($i=0;$i -lt 6;$i++){
   Load ($language+'all-services.html')
   Eval ('document.querySelectorAll(".service-overview-card>.action")['+$i+'].click()')|Out-Null
   Wait ('location.pathname==="/'+$language+$serviceRoutes[$i]+'"&&document.readyState==="complete"')
   Wait '!!document.querySelector(".pt-nav[data-organized-navigation]")'
   Assert (Eval 'document.querySelectorAll(".pt-nav>.nav-family").length===2') 'Existing service page navigation failed'
   Load ($language+'packages.html')
   Eval ('document.querySelectorAll(".category-overview-card>.action")['+$i+'].click()')|Out-Null
   Wait ('location.pathname==="/'+$language+$kinds[$i]+'-packages.html"&&document.readyState==="complete"')
  }
  Load ($language+'packages.html')
  Eval 'document.querySelector(".category-overview-card:last-child>.action").click()'|Out-Null
  Wait ('location.pathname==="/'+$language+'all-bundles.html"&&document.readyState==="complete"')
  Load ($language+'all-services.html')
  Eval 'document.querySelector(".pt-nav>.nav-family:nth-of-type(2)>a").click()'|Out-Null
  Wait ('location.pathname==="/'+$language+'packages.html"&&document.readyState==="complete"')
  foreach($name in @('all-services.html','monthly-bookkeeping-packages.html')){
   Load ($language+$name)
   $next=if($language){'en'}else{'es'}
   Eval ('(()=>{const s=document.querySelector("#language");s.value="'+$next+'";s.dispatchEvent(new Event("change",{bubbles:true}));return true})()')|Out-Null
   $nextPrefix=if($next -eq 'en'){''}else{$next+'/'}
   Wait ('location.pathname==="/'+$nextPrefix+$name+'"&&document.readyState==="complete"')
   Eval 'localStorage.removeItem("paper-trail-language")'|Out-Null
  }
 }
 Assert ($script:exceptions.Count -eq 0) ('JavaScript exceptions: '+($script:exceptions -join ', '))
 Assert (@($script:requests|Where-Object {$_.method -notin @('GET','HEAD','OPTIONS')}).Count -eq 0) 'Unexpected write request'
 @{page_viewport_checks=$results.Count;card_main_label_and_language_switch_checks=160;keyboard_dropdown_checks=10;languages=10;widths=@(1440,1024,834,390);javascript_errors=$script:exceptions;external_requests_blocked=$true;forms_submitted=0;checks=$results}|ConvertTo-Json -Depth 10|Set-Content -LiteralPath (Join-Path $out 'results.json') -Encoding UTF8
 Write-Output ('PASS: '+$results.Count+' page/viewport checks, 160 actual navigations, 10 keyboard dropdown checks. Results: '+$out)
}finally{
 if($socket){$socket.Dispose()}
 if($browser -and !$browser.HasExited){Stop-Process -Id $browser.Id -ErrorAction SilentlyContinue}
}
