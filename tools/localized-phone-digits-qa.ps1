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
 $results=@()
 Cdp 'Emulation.setDeviceMetricsOverride' @{width=390;height=1100;deviceScaleFactor=1;mobile=$true}|Out-Null
 Load 'blog.html'
 foreach($code in @('fa','ar','te','zh-CN')){
 Cdp 'Runtime.evaluate' @{expression=('(()=>{const d=document.querySelector("#conversation-dialog");if(d.open)d.close();const s=document.querySelector("#language");s.value='+($code|ConvertTo-Json -Compress)+';s.dispatchEvent(new Event("change"));document.querySelector(".mobile-support button").click();document.querySelector(".chat-reset").click();return true})()')}|Out-Null
 $offset=switch($code){'fa'{1776}'ar'{1632}'te'{3174}'zh-CN'{65296}}
 $flow=[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'localized-chat-eval.js')).Replace("answer('8185550123')",("answer(String.fromCharCode(...[8,1,8,5,5,5,0,1,2,3].map(n=>"+$offset+"+n)))"))
 $r=Cdp 'Runtime.evaluate' @{expression=$flow;awaitPromise=$true;returnByValue=$true};$review=$r.result.value
 $r=Cdp 'Runtime.evaluate' @{expression=([IO.File]::ReadAllText((Join-Path $PSScriptRoot 'localized-chat-confirmation-eval.js')));awaitPromise=$true;returnByValue=$true};$results+=@{language=$code;review=$review;confirmation=$r.result.value}
 }
 $results|ConvertTo-Json -Depth 15|Set-Content (Join-Path $out 'native-phone-digit-checks.json') -Encoding UTF8
 @{exceptions=$script:exceptions;requests=$script:requests}|ConvertTo-Json -Depth 8|Set-Content (Join-Path $out 'native-phone-runtime.json') -Encoding UTF8
 Cdp 'Browser.close'|Out-Null
}finally{if($socket){$socket.Dispose()}}
