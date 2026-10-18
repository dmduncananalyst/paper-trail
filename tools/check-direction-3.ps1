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
 $checks=@{}
 Cdp 'Emulation.setDeviceMetricsOverride' @{width=1440;height=1100;deviceScaleFactor=1;mobile=$false}|Out-Null
 Cdp 'Page.navigate' @{url='http://127.0.0.1:8765/verification/phase-a/review.html'}|Out-Null
 Start-Sleep -Milliseconds 800
 Cdp 'Page.navigate' @{url='http://127.0.0.1:8765/verification/phase-a/home.html'}|Out-Null
 Start-Sleep -Milliseconds 600
 $checks.home=(Cdp 'Runtime.evaluate' @{expression='(async()=>{const v=document.querySelector("video"),b=document.querySelector(".video-toggle");await v.play();const t=v.currentTime;await new Promise(r=>setTimeout(r,220));const playing=!v.paused&&v.currentTime>t;b.click();const pauses=v.paused;b.click();await new Promise(r=>setTimeout(r,100));const resumes=!v.paused;const menu=document.querySelector(".pt-services-toggle");menu.click();const opens=!document.querySelector(".pt-directory").hidden;document.dispatchEvent(new KeyboardEvent("keydown",{key:"Escape",bubbles:true}));const closes=document.querySelector(".pt-directory").hidden;document.querySelector("[data-open-chat]").click();const chat=document.querySelector("#conversation-dialog").open;document.querySelector(".chat-close").click();document.querySelector("[data-email]").click();const emailDialog=document.querySelector(".email-dialog");const emailOpens=emailDialog.open;const emailChoices=[...emailDialog.querySelectorAll(".email-options a,.email-options button")].map(x=>x.textContent);emailDialog.close();const allIcons=[...document.querySelectorAll("[data-icon-id]")].map(x=>x.dataset.iconId);return {emailOpens,emailChoices,uniqueIcons:allIcons.length===new Set(allIcons).size,footerLogos:document.querySelectorAll(".pt-footer img").length,videoSrc:v.currentSrc,playing,pauseControlWorks:pauses,resumeControlWorks:resumes,videoWidth:v.videoWidth,icons:[...document.querySelectorAll("[data-icon-id]")].map(x=>x.dataset.iconId),serviceCards:document.querySelectorAll(".service-card").length,notesCards:document.querySelectorAll(".note-card").length,menuClickOpens:opens,escapeCloses:closes,chatOpens:chat,chatCloses:!document.querySelector("#conversation-dialog").open}})()';awaitPromise=$true;returnByValue=$true}).result.value
 $checks|ConvertTo-Json -Depth 10|Set-Content (Join-Path $folder 'revision-validation.json') -Encoding UTF8
 $checks|ConvertTo-Json -Depth 10
 Cdp 'Browser.close'|Out-Null
}finally{if($socket){$socket.Dispose()}}