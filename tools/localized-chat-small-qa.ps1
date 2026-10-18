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
 $checks=@();$flow=[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'localized-chat-eval.js'))
 Cdp 'Emulation.setDeviceMetricsOverride' @{width=320;height=1100;deviceScaleFactor=1;mobile=$true}|Out-Null
 foreach($route in @('index.html','blog.html')){
 Load $route
 foreach($code in @('en','es','fa','hy','zh-CN','ko','tl','te','ru','ar')){
 Cdp 'Runtime.evaluate' @{expression=('(()=>{const dialog=document.querySelector("#conversation-dialog");if(dialog.open)dialog.close();const select=document.querySelector("#language");select.value='+($code|ConvertTo-Json -Compress)+';select.dispatchEvent(new Event("change"));document.querySelector("'+$(if($route -eq 'index.html'){'.home-conversation [data-open-chat]'}else{'.mobile-support [data-open-chat]'})+'").click();document.querySelector(".chat-reset").click();return true})()')}|Out-Null
 $r=Cdp 'Runtime.evaluate' @{expression=$flow;awaitPromise=$true;returnByValue=$true};$checks+=@{page=$route;language=$code;state=$r.result.value}
 }
 }
 $checks|ConvertTo-Json -Depth 15|Set-Content (Join-Path $out 'small-phone-chat-checks.json') -Encoding UTF8
 Cdp 'Emulation.setDeviceMetricsOverride' @{width=390;height=1100;deviceScaleFactor=1;mobile=$true}|Out-Null
 Load 'index.html'
 $r=Cdp 'Runtime.evaluate' @{expression='(async()=>{const s=document.querySelector("#language");s.value="es";s.dispatchEvent(new Event("change"));document.querySelector(".home-conversation button").click();document.querySelector(".chat input").value="California";document.querySelector(".send-message").click();document.querySelector(".chat-options button").click();s.value="hy";s.dispatchEvent(new Event("change"));const d=window.PAPER_TRAIL_CHAT_LOCALES.hy;const switched=document.querySelector(".chat-question").textContent===d["Which period needs attention?"];const preserved=[...document.querySelectorAll(".bubble.user")].map(e=>e.textContent);document.querySelector(".chat-mode").click();const prompt=document.querySelector(".chat-question").textContent;document.querySelector(".chat input").value="Example question";document.querySelector(".send-message").click();await new Promise(r=>setTimeout(r,50));return {switched,preserved,helpPromptTranslated:prompt===d["What would you like to understand about this part of your bookkeeping?"],helpReplyTranslated:[...document.querySelectorAll(".bubble")].some(e=>e.textContent===d["Please include your bookkeeping question in your message so Paper Trail can follow up."])}})()';awaitPromise=$true;returnByValue=$true};$r.result.value|ConvertTo-Json -Depth 8|Set-Content (Join-Path $out 'language-switch-and-help-checks.json') -Encoding UTF8
 Cdp 'Runtime.evaluate' @{expression='document.querySelector(".chat-close").click();document.querySelector(".home-notes").scrollIntoView({block:"start",behavior:"instant"});true'}|Out-Null;Shot 'home-notes-heading-hy-390'
 Load 'index.html';Cdp 'Runtime.evaluate' @{expression='document.querySelector(".home-notes").scrollIntoView({block:"start",behavior:"instant"});true'}|Out-Null;Shot 'home-notes-heading-en-390'
 @{exceptions=$script:exceptions;requests=$script:requests}|ConvertTo-Json -Depth 10|Set-Content (Join-Path $out 'supplementary-runtime-checks.json') -Encoding UTF8
 Cdp 'Browser.close'|Out-Null
}finally{if($socket){$socket.Dispose()}}
