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
 Cdp 'Emulation.setDeviceMetricsOverride' @{width=1440;height=1100;deviceScaleFactor=1;mobile=$false}|Out-Null
 Cdp 'Page.navigate' @{url='http://127.0.0.1:8765/verification/phase-a/home.html?update=hero-hover-padding'}|Out-Null
 Start-Sleep -Milliseconds 700
 $state=(Cdp 'Runtime.evaluate' @{expression='(async()=>{await document.fonts.ready;return [...document.querySelectorAll(".hero-service-links>a")].map(a=>{const r=a.getBoundingClientRect(),i=a.querySelector("svg").getBoundingClientRect(),v=a.querySelector(".hero-service-action").getBoundingClientRect();return {label:a.textContent.trim(),spaceAboveIcon:i.top-r.top,spaceBelowAction:r.bottom-v.bottom,x:r.x+r.width/2,y:r.y+r.height/2}})})()';awaitPromise=$true;returnByValue=$true}).result.value
 $state|ConvertTo-Json
 foreach($item in $state){Cdp 'Input.dispatchMouseEvent' @{type='mouseMoved';x=$item.x;y=$item.y}|Out-Null;Start-Sleep -Milliseconds 100;$shot=Cdp 'Page.captureScreenshot' @{format='png';captureBeyondViewport=$false};$suffix=if($item.label.Contains('View Repair')){'repair'}else{'monthly'};[IO.File]::WriteAllBytes((Join-Path $folder ('hero-hover-padded-'+$suffix+'.png')),[Convert]::FromBase64String($shot.data))}
 Cdp 'Browser.close'|Out-Null
}finally{if($socket){$socket.Dispose()}}