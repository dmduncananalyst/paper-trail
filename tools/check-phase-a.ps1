param([int]$Port=9235)
$ErrorActionPreference='Stop'
$folder=Join-Path (Get-Location) 'verification/phase-a'
$browserProfile=Join-Path $env:TEMP ('paper-trail-preview-'+$Port)
if (!(Test-NetConnection 127.0.0.1 -Port $Port -InformationLevel Quiet -WarningAction SilentlyContinue)) { $browser=Start-Process -FilePath 'C:/Program Files/Google/Chrome/Application/chrome.exe' -ArgumentList @('--headless=new','--disable-gpu','--no-first-run','--no-default-browser-check',"--remote-debugging-port=$Port",('--user-data-dir="'+$browserProfile+'"'),'about:blank') -WindowStyle Hidden -PassThru }
try {
 $target=$null
 for($i=0;$i -lt 40;$i++){try{$targets=Invoke-RestMethod "http://127.0.0.1:$Port/json" -TimeoutSec 2;$target=$targets|Where-Object type -EQ 'page'|Select-Object -First 1;if($target){break}}catch{};Start-Sleep -Milliseconds 250}
 if(!$target){throw 'Local browser debugging endpoint unavailable'}
 $socket=[Net.WebSockets.ClientWebSocket]::new();$socket.ConnectAsync([uri]$target.webSocketDebuggerUrl,[Threading.CancellationToken]::None).GetAwaiter().GetResult()
 $script:requestId=0
 function Cdp($method,$params=@{}) {
  $script:requestId++;$id=$script:requestId
  $msg=@{id=$id;method=$method;params=$params}|ConvertTo-Json -Depth 15 -Compress
  $bytes=[Text.Encoding]::UTF8.GetBytes($msg)
  $socket.SendAsync([ArraySegment[byte]]::new($bytes),[Net.WebSockets.WebSocketMessageType]::Text,$true,[Threading.CancellationToken]::None).GetAwaiter().GetResult()
  while($true){$stream=[IO.MemoryStream]::new();do{$buffer=New-Object byte[] 65536;$read=$socket.ReceiveAsync([ArraySegment[byte]]::new($buffer),[Threading.CancellationToken]::None).GetAwaiter().GetResult();$stream.Write($buffer,0,$read.Count)}while(!$read.EndOfMessage);$reply=[Text.Encoding]::UTF8.GetString($stream.ToArray())|ConvertFrom-Json;$stream.Dispose();if($reply.id -eq $id){if($reply.error){throw ($reply.error|ConvertTo-Json -Compress)};return $reply.result}}
 }
 Cdp 'Page.enable'|Out-Null
 $report=@()
 $checks=@{}
 Cdp 'Emulation.setDeviceMetricsOverride' @{width=390;height=1100;deviceScaleFactor=1;mobile=$true}|Out-Null
 Cdp 'Page.navigate' @{url=([uri](Join-Path $folder 'notes.html')).AbsoluteUri}|Out-Null
 Start-Sleep -Milliseconds 600
 $checks.menu=(Cdp 'Runtime.evaluate' @{expression='(()=>{const b=document.querySelector("#navigation-toggle"),p=document.querySelector("#navigation-panel");b.click();const opened=!p.hidden&&b.getAttribute("aria-expanded")==="true";document.dispatchEvent(new KeyboardEvent("keydown",{key:"Escape",bubbles:true}));return {clickOpens:opened,escapeCloses:p.hidden,focusRestored:document.activeElement===b,cards:[...document.querySelectorAll(".glow-card")].map(x=>({width:x.clientWidth,height:x.clientHeight})),uniqueIcons:new Set([...document.querySelectorAll(".topic-icon")].map(x=>x.innerHTML)).size}})()';returnByValue=$true}).result.value
 Cdp 'Page.navigate' @{url=([uri](Join-Path $folder '../../index.html')).AbsoluteUri}|Out-Null
 Start-Sleep -Milliseconds 600
 $checks.existingChat=(Cdp 'Runtime.evaluate' @{expression='(()=>{document.querySelector("[data-open-chat]").click();const d=document.querySelector("#conversation-dialog");const opened=d.open;const prompts=document.querySelector(".chat-options").children.length;document.querySelector(".chat-close").click();return {opens:opened,choices:prompts,closes:!d.open,noSubmissionAttempted:true}})()';returnByValue=$true}).result.value
 Cdp 'Page.navigate' @{url=([uri](Join-Path $folder 'video-audit.html')).AbsoluteUri}|Out-Null
 Start-Sleep -Milliseconds 800
 $checks.videos=(Cdp 'Runtime.evaluate' @{expression='(async()=>{return await Promise.all([...document.querySelectorAll("video")].map(async v=>{if(v.readyState<1)await new Promise((r,j)=>{v.onloadedmetadata=r;v.onerror=j});v.currentTime=2;await new Promise(r=>v.onseeked=r);await v.play();await new Promise(r=>setTimeout(r,150));const playing=!v.paused&&v.currentTime>2;v.pause();return {src:v.getAttribute("src"),duration:v.duration,width:v.videoWidth,height:v.videoHeight,playing,paused:v.paused,error:v.error?.message||null}}))})()';awaitPromise=$true;returnByValue=$true}).result.value
 Cdp 'Emulation.setDeviceMetricsOverride' @{width=1440;height=1100;deviceScaleFactor=1;mobile=$false}|Out-Null
 $shot=Cdp 'Page.captureScreenshot' @{format='png';captureBeyondViewport=$false};[IO.File]::WriteAllBytes((Join-Path $folder 'video-audit.png'),[Convert]::FromBase64String($shot.data))
 Cdp 'Page.navigate' @{url=([uri](Join-Path $folder 'preview-board.html')).AbsoluteUri}|Out-Null
 Start-Sleep -Milliseconds 500
 Cdp 'Runtime.evaluate' @{expression='Promise.all([...document.images].map(i=>i.decode()))';awaitPromise=$true}|Out-Null
 $shot=Cdp 'Page.captureScreenshot' @{format='png';captureBeyondViewport=$false};[IO.File]::WriteAllBytes((Join-Path $folder 'preview-board.png'),[Convert]::FromBase64String($shot.data))
 $checks|ConvertTo-Json -Depth 8|Set-Content (Join-Path $folder 'interaction-validation.json') -Encoding UTF8
 $checks|ConvertTo-Json -Depth 8
 Cdp 'Browser.close'|Out-Null
}finally{if($socket){$socket.Dispose()}}