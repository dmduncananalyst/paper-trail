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
 Cdp 'Page.navigate' @{url='http://127.0.0.1:8765/verification/phase-a/review.html'}|Out-Null
 Start-Sleep -Milliseconds 1200
 $state=Cdp 'Runtime.evaluate' @{expression='(async()=>{const frame=document.querySelector("#design-frame");const ready=async test=>{for(let i=0;i<60;i++){try{if(test())return true}catch{}await new Promise(r=>setTimeout(r,100))}return false};const home=await ready(()=>frame.contentDocument?.querySelector(".home-hero"));document.querySelector("[data-width=mobile]").click();await new Promise(r=>setTimeout(r,400));const heightBefore=frame.getBoundingClientRect().height;document.querySelector("[data-page=contact]").click();const contact=await ready(()=>frame.contentDocument?.querySelector(".contact-main"));await new Promise(r=>setTimeout(r,700));const bodyHeight=frame.contentDocument.body.getBoundingClientRect().height,frameHeight=frame.getBoundingClientRect().height;return {homeLoaded:home,contactLoaded:contact,heightBefore,bodyHeight,frameHeight,extraSpace:frameHeight-bodyHeight,shrinks:frameHeight<heightBefore,width:frame.contentWindow.innerWidth}})()';awaitPromise=$true;returnByValue=$true}
 $state.result.value|ConvertTo-Json -Depth 6|Set-Content -LiteralPath (Join-Path $folder 'review-frame-validation.json') -Encoding UTF8
 $state|ConvertTo-Json -Depth 8
 Cdp 'Browser.close'|Out-Null
}finally{if($socket){$socket.Dispose()}}