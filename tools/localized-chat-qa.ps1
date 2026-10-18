param([int]$Port=9235)
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
 $out=Join-Path (Get-Location) 'verification/localized-chat-20261016';$shots=Join-Path $out 'screenshots';New-Item -ItemType Directory -Force -Path $shots|Out-Null
 $evaluate=[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'visual-corrections-eval.js'))
 function Load($route){Cdp 'Page.navigate' @{url=('http://127.0.0.1:8765/'+$route)}|Out-Null;$expression='(async()=>{for(let i=0;i<240;i++){if(location.pathname.endsWith('+($route|ConvertTo-Json -Compress)+')&&document.readyState==="complete"&&window.paperTrailUI){localStorage.setItem("paper-trail-language","en");const s=document.querySelector("#language");if(s){s.value="en";s.dispatchEvent(new Event("change"))}document.documentElement.style.scrollBehavior="auto";await document.fonts.ready;document.querySelectorAll("img").forEach(i=>i.loading="eager");await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));return true}await new Promise(r=>setTimeout(r,50))}throw Error("Page not ready")})()';$r=Cdp 'Runtime.evaluate' @{expression=$expression;awaitPromise=$true;returnByValue=$true};if($r.exceptionDetails){throw ($r.exceptionDetails|ConvertTo-Json -Depth 3)}}
 function Shot($name){$shot=Cdp 'Page.captureScreenshot' @{format='png';captureBeyondViewport=$false};[IO.File]::WriteAllBytes((Join-Path $shots ($name+'.png')),[Convert]::FromBase64String($shot.data))}
 $chatTests=@();$cardTests=@();$layoutTests=@();$confirmationTests=@()
 $flow=[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'localized-chat-eval.js'))
 Cdp 'Emulation.setDeviceMetricsOverride' @{width=390;height=1100;deviceScaleFactor=1;mobile=$true}|Out-Null
 foreach($route in @('index.html','blog.html')){
 Load $route
 foreach($code in @('en','es','fa','hy','zh-CN','ko','tl','te','ru','ar')){
 $r=Cdp 'Runtime.evaluate' @{expression=('(()=>{const dialog=document.querySelector("#conversation-dialog");if(dialog.open)dialog.close();const s=document.querySelector("#language");s.value='+($code|ConvertTo-Json -Compress)+';s.dispatchEvent(new Event("change"));document.querySelector("'+$(if($route -eq 'index.html'){'.home-conversation [data-open-chat]'}else{'.mobile-support [data-open-chat]'})+'").click();document.querySelector(".chat-reset").click();return {question:document.querySelector(".chat-question").textContent,language:document.documentElement.lang}})()');returnByValue=$true}
 Shot ($route.Replace('.html','')+'-'+$code+'-question')
 $r=Cdp 'Runtime.evaluate' @{expression=$flow;awaitPromise=$true;returnByValue=$true};if($r.exceptionDetails){throw ($r.exceptionDetails|ConvertTo-Json -Depth 5)};$chatTests+=@{page=$route;language=$code;state=$r.result.value}
 if($code -in @('es','hy','fa','ar','en')){Shot ($route.Replace('.html','')+'-'+$code+'-review')}
 $r=Cdp 'Runtime.evaluate' @{expression=([IO.File]::ReadAllText((Join-Path $PSScriptRoot 'localized-chat-confirmation-eval.js')));awaitPromise=$true;returnByValue=$true};$confirmationTests+=@{page=$route;language=$code;state=$r.result.value}

 }
 }
 $confirmationTests|ConvertTo-Json -Depth 15|Set-Content (Join-Path $out 'confirmation-checks.json') -Encoding UTF8
 $chatTests|ConvertTo-Json -Depth 15|Set-Content (Join-Path $out 'chat-checks.json') -Encoding UTF8
 $inventory=Get-Content (Join-Path $out 'service-card-inventory.json') -Raw|ConvertFrom-Json
 foreach($width in @(320,390,430,834,1440)){
 Cdp 'Emulation.setDeviceMetricsOverride' @{width=$width;height=1100;deviceScaleFactor=1;mobile=($width -lt 600)}|Out-Null
 foreach($entry in $inventory){Load $entry.page;$r=Cdp 'Runtime.evaluate' @{expression='(()=>{const box=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height}};return {overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+2,cards:[...document.querySelectorAll(".service-notes .photo-card")].map(c=>({card:box(c),photo:box(c.querySelector("img")),title:getComputedStyle(c.querySelector("h3")).textAlign,columns:getComputedStyle(c).gridTemplateColumns}))}})()';returnByValue=$true};$cardTests+=@{page=$entry.page;width=$width;state=$r.result.value};if($entry.page -in @('balancing-corrections.html','tax-ready-bookkeeping.html','bank-credit-card-balancing.html')){Cdp 'Runtime.evaluate' @{expression='document.querySelector(".service-notes").scrollIntoView({block:"start",behavior:"instant"});true'}|Out-Null;Shot ($entry.page.Replace('.html','')+'-'+$width)}}
 foreach($route in @('index.html','notes.html','blog.html')){Load $route;Cdp 'Runtime.evaluate' @{expression='(document.querySelector(".home-notes")||document.querySelector(".page-conversation")||document.querySelector(".mobile-support")).scrollIntoView({block:"center",behavior:"instant"});true'}|Out-Null;Shot ($route.Replace('.html','')+'-layout-'+$width)}
 'Checked cards at '+$width
 }
 $cardTests|ConvertTo-Json -Depth 12|Set-Content (Join-Path $out 'card-checks.json') -Encoding UTF8
 @{exceptions=$script:exceptions;requests=$script:requests}|ConvertTo-Json -Depth 10|Set-Content (Join-Path $out 'runtime-checks.json') -Encoding UTF8
 Cdp 'Browser.close'|Out-Null
}finally{if($socket){$socket.Dispose()}}
