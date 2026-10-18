param([int]$Port=9244)
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
 $out=Join-Path (Get-Location) 'verification/playback-chat-20261016';$shots=Join-Path $out 'screenshots';New-Item -ItemType Directory -Force -Path $shots|Out-Null
 $evaluate=[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'visual-corrections-eval.js'))
 function Load($route){Cdp 'Page.navigate' @{url=('http://127.0.0.1:8765/'+$route)}|Out-Null;$expression='(async()=>{for(let i=0;i<240;i++){if(location.pathname.endsWith('+($route|ConvertTo-Json -Compress)+')&&document.readyState==="complete"&&window.paperTrailUI){localStorage.setItem("paper-trail-language","en");const s=document.querySelector("#language");if(s){s.value="en";s.dispatchEvent(new Event("change"))}document.documentElement.style.scrollBehavior="auto";await document.fonts.ready;document.querySelectorAll("img").forEach(i=>i.loading="eager");await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));return true}await new Promise(r=>setTimeout(r,50))}throw Error("Page not ready")})()';$r=Cdp 'Runtime.evaluate' @{expression=$expression;awaitPromise=$true;returnByValue=$true};if($r.exceptionDetails){throw ($r.exceptionDetails|ConvertTo-Json -Depth 3)}}
 function Shot($name){$shot=Cdp 'Page.captureScreenshot' @{format='png';captureBeyondViewport=$false};[IO.File]::WriteAllBytes((Join-Path $shots ($name+'.png')),[Convert]::FromBase64String($shot.data))}


 Cdp 'Network.setCacheDisabled' @{cacheDisabled=$true}|Out-Null
 $injected='(()=>{window.videoLoadSamples=[];window.videoLoadShifts=[];try{new PerformanceObserver(l=>l.getEntries().forEach(e=>{if(!e.hadRecentInput)window.videoLoadShifts.push(e.value)})).observe({type:"layout-shift",buffered:true})}catch{}const start=performance.now();function frame(){const v=document.querySelector("video");if(v){const r=v.parentElement.getBoundingClientRect();window.videoLoadSamples.push({t:performance.now(),x:r.x,y:r.y,w:r.width,h:r.height,ready:v.readyState,playing:!v.paused})}if(performance.now()-start<4000)requestAnimationFrame(frame)}requestAnimationFrame(frame)})();'
 Cdp 'Page.addScriptToEvaluateOnNewDocument' @{source=$injected}|Out-Null
 $cold=@()
 foreach($width in @(390,834,1440)){
 Cdp 'Emulation.setDeviceMetricsOverride' @{width=$width;height=1000;deviceScaleFactor=1;mobile=($width -lt 600)}|Out-Null
 foreach($scheme in @('http','file')){
 foreach($route in @('index.html','about.html','paper-trail-services.html','paper-trail-monthly-bookkeeping.html')){
 $url=if($scheme -eq 'http'){'http://127.0.0.1:8765/'+$route}else{([uri](Join-Path (Get-Location) $route)).AbsoluteUri}
 Cdp 'Page.navigate' @{url=$url}|Out-Null
 Start-Sleep -Milliseconds 4500
 $r=Cdp 'Runtime.evaluate' @{expression='({samples:window.videoLoadSamples,shifts:window.videoLoadShifts})';returnByValue=$true}
 $cold+=@{page=$route;width=$width;scheme=$scheme;state=$r.result.value}
 }
 }
 }
 $cold|ConvertTo-Json -Depth 10|Set-Content (Join-Path $out 'cold-load-checks.json') -Encoding UTF8
 Load 'index.html'
 Cdp 'Runtime.evaluate' @{expression='document.querySelector("[data-open-chat]").click();document.querySelector("#chat-reply").blur();true'}|Out-Null
 Shot 'chat-unfocused-border'
 Cdp 'Browser.close'|Out-Null
}finally{if($socket){$socket.Dispose()}}
