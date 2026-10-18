param([int]$Port=9248)
$ErrorActionPreference='Stop'
$folder=Join-Path $env:TEMP 'paper-trail-audit5-20261016'
$browserProfile=Join-Path $env:TEMP ('paper-trail-preview-'+$Port)
if (!(Test-NetConnection 127.0.0.1 -Port $Port -InformationLevel Quiet -WarningAction SilentlyContinue)) { $browser=Start-Process -FilePath 'C:/Program Files/Google/Chrome/Application/chrome.exe' -ArgumentList @('--headless=new','--disable-gpu','--no-first-run','--no-default-browser-check',"--remote-debugging-port=$Port",('--user-data-dir="'+$browserProfile+'"'),'about:blank') -WindowStyle Hidden -PassThru }
try {
 $target=$null
 for($i=0;$i -lt 40;$i++){try{$targets=Invoke-RestMethod "http://127.0.0.1:$Port/json" -TimeoutSec 2;$target=$targets|Where-Object type -EQ 'page'|Select-Object -First 1;if($target){break}}catch{};Start-Sleep -Milliseconds 250}
 if(!$target){throw 'Local browser debugging endpoint unavailable'}
 $socket=[Net.WebSockets.ClientWebSocket]::new();$socket.ConnectAsync([uri]$target.webSocketDebuggerUrl,[Threading.CancellationToken]::None).GetAwaiter().GetResult()
 $script:requestId=0;$script:requests=@();$script:exceptions=@()
 function Cdp($method,$params=@{}) {
  $script:requestId++;$id=$script:requestId
  $msg=@{id=$id;method=$method;params=$params}|ConvertTo-Json -Depth 15 -Compress
  $bytes=[Text.Encoding]::UTF8.GetBytes($msg)
  $socket.SendAsync([ArraySegment[byte]]::new($bytes),[Net.WebSockets.WebSocketMessageType]::Text,$true,[Threading.CancellationToken]::None).GetAwaiter().GetResult()
  while($true){$stream=[IO.MemoryStream]::new();do{$buffer=New-Object byte[] 65536;$read=$socket.ReceiveAsync([ArraySegment[byte]]::new($buffer),[Threading.CancellationToken]::None).GetAwaiter().GetResult();$stream.Write($buffer,0,$read.Count)}while(!$read.EndOfMessage);$reply=[Text.Encoding]::UTF8.GetString($stream.ToArray())|ConvertFrom-Json;$stream.Dispose();if($reply.method -eq 'Network.requestWillBeSent'){$script:requests+=$reply.params.request.url};if($reply.method -eq 'Runtime.exceptionThrown'){$script:exceptions+=$reply.params.exceptionDetails};if($reply.id -eq $id){if($reply.error){throw ($reply.error|ConvertTo-Json -Compress)};return $reply.result}}
 }
 Cdp 'Page.enable'|Out-Null
 Cdp 'Network.enable'|Out-Null
 Cdp 'Runtime.enable'|Out-Null
 Cdp 'Network.setBlockedURLs' @{urls=@('*cloudtranslation*','*translation.googleapis.com/*','*translate.googleapis.com/*','https://api.hsforms.com/*','*/api/chat','*/api/inquiry')}|Out-Null
 Cdp 'Emulation.setFocusEmulationEnabled' @{enabled=$true}|Out-Null
 $out=Join-Path (Get-Location) 'verification/state-content-replacement-20261016';$shots=Join-Path $out 'screenshots';New-Item -ItemType Directory -Force -Path $shots|Out-Null
 $evaluate=[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'visual-corrections-eval.js'))
 function Load($route){Cdp 'Page.navigate' @{url=('http://127.0.0.1:8765/'+$route)}|Out-Null;$expression='(async()=>{for(let i=0;i<240;i++){if(location.pathname.endsWith('+($route|ConvertTo-Json -Compress)+')&&document.readyState==="complete"&&window.paperTrailUI){localStorage.setItem("paper-trail-language","en");const s=document.querySelector("#language");if(s){s.value="en";s.dispatchEvent(new Event("change"))}document.documentElement.style.scrollBehavior="auto";await document.fonts.ready;document.querySelectorAll("img").forEach(i=>i.loading="eager");await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));return true}await new Promise(r=>setTimeout(r,50))}throw Error("Page not ready")})()';$r=Cdp 'Runtime.evaluate' @{expression=$expression;awaitPromise=$true;returnByValue=$true};if($r.exceptionDetails){throw ($r.exceptionDetails|ConvertTo-Json -Depth 3)}}
 function Shot($name){$shot=Cdp 'Page.captureScreenshot' @{format='png';captureBeyondViewport=$false};[IO.File]::WriteAllBytes((Join-Path $shots ($name+'.png')),[Convert]::FromBase64String($shot.data))}


 $stateChecks=@();$languageChecks=@();$menuChecks=@()
 $states=Get-Content (Join-Path $out 'mapping.json') -Raw|ConvertFrom-Json
 foreach($width in @(390,834,1440)){
 Cdp 'Emulation.setDeviceMetricsOverride' @{width=$width;height=1100;deviceScaleFactor=1;mobile=($width -lt 600)}|Out-Null
 foreach($state in $states){
 Load $state.page
 $r=Cdp 'Runtime.evaluate' @{expression='(()=>{const box=e=>{const r=e.getBoundingClientRect();return {w:r.width,h:r.height,x:r.x}};const paragraphs=[...document.querySelectorAll(".state-resource-body p")];return {h1:[...document.querySelectorAll("h1")].map(e=>e.textContent),h2:document.querySelectorAll(".state-resource-body h2").length,paragraphs:paragraphs.length,overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+2,brokenImages:[...document.images].filter(e=>!e.complete||!e.naturalWidth).map(e=>e.src),canonical:document.querySelector("link[rel=canonical]").href,body:box(document.querySelector(".state-resource-body")),textSize:getComputedStyle(paragraphs[0]).fontSize,links:[...document.querySelectorAll(".state-related a")].map(e=>e.getAttribute("href"))}})()';returnByValue=$true};if($r.exceptionDetails){throw ($r.exceptionDetails|ConvertTo-Json -Depth 5)}
 $stateChecks+=@{state=$state.state;width=$width;result=$r.result.value}
 if($state.state -in @('California','Connecticut','New Jersey','Texas','Wyoming')){Shot ($state.state.Replace(' ','-')+'-'+$width)}
 }
 foreach($route in @('index.html','blog.html')){
 Load $route
 foreach($code in @('en','es','fa','hy','zh-CN','ko','tl','te','ru','ar')){
 $r=Cdp 'Runtime.evaluate' @{expression=('(async()=>{const s=document.querySelector("#language");s.value='+($code|ConvertTo-Json -Compress)+';s.dispatchEvent(new Event("change"));await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));const e=document.querySelector(".translation-notice"),cs=getComputedStyle(e);return {fontSize:cs.fontSize,textAlign:cs.textAlign,hidden:e.hidden,overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+2,text:e.textContent}})()');awaitPromise=$true;returnByValue=$true};$languageChecks+=@{page=$route;language=$code;width=$width;result=$r.result.value}
 if($route -eq 'index.html' -and $code -in @('es','hy')){Shot ('notice-'+$code+'-'+$width)}
 }
 }
 Load 'index.html'
 $r=Cdp 'Runtime.evaluate' @{expression='(()=>{const a=document.querySelector(".nav-family>a"),r=a.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2,header:document.querySelector(".pt-header").getBoundingClientRect().height,main:document.querySelector("main").getBoundingClientRect().top}})()';returnByValue=$true};$before=$r.result.value
 if($width -gt 650){Cdp 'Input.dispatchMouseEvent' @{type='mouseMoved';x=$before.x;y=$before.y}|Out-Null}else{Cdp 'Runtime.evaluate' @{expression='document.querySelector(".nav-family>a").click();true'}|Out-Null}
 Start-Sleep -Milliseconds 150
 $r=Cdp 'Runtime.evaluate' @{expression='({header:document.querySelector(".pt-header").getBoundingClientRect().height,main:document.querySelector("main").getBoundingClientRect().top,open:document.querySelector(".nav-family>a").getAttribute("aria-expanded"),panelTop:document.querySelector(".pt-header>.nav-panel:not([hidden])")?.getBoundingClientRect().top})';returnByValue=$true};$menuChecks+=@{width=$width;before=$before;after=$r.result.value};Shot ('menu-after-'+$width)
 Cdp 'Input.dispatchMouseEvent' @{type='mouseMoved';x=5;y=5}|Out-Null
 'Checked '+$width
 }
 @{states=$stateChecks;languages=$languageChecks;menus=$menuChecks;exceptions=$script:exceptions}|ConvertTo-Json -Depth 14|Set-Content (Join-Path $out 'browser-checks.json') -Encoding UTF8
 Cdp 'Browser.close'|Out-Null
}finally{if($socket){$socket.Dispose()}}
