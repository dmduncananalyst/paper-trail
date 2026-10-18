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
 Cdp 'Emulation.setDeviceMetricsOverride' @{width=1440;height=1000;deviceScaleFactor=1;mobile=$false}|Out-Null
 Cdp 'Page.navigate' @{url='http://127.0.0.1:8765/verification/phase-a/home.html?update=submenu-hover'}|Out-Null
 Start-Sleep -Milliseconds 700
 $pos=(Cdp 'Runtime.evaluate' @{expression='(()=>{const r=document.querySelectorAll(".nav-family>a")[1].getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()';returnByValue=$true}).result.value
 Cdp 'Input.dispatchMouseEvent' @{type='mouseMoved';x=$pos.x;y=$pos.y}|Out-Null
 Start-Sleep -Milliseconds 150
 $before=(Cdp 'Runtime.evaluate' @{expression='(()=>{const primary=document.querySelectorAll(".nav-family>a")[1],panel=document.querySelector("#service-strip-1");return {topBackground:getComputedStyle(primary).backgroundColor,open:!panel.hidden,overviewBackground:getComputedStyle(panel.querySelector("a")).backgroundColor}})()';returnByValue=$true}).result.value
 $pos=(Cdp 'Runtime.evaluate' @{expression='(()=>{const r=document.querySelector("#service-strip-1 a[href=\"accounts-payable-receivable.html\"]").getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()';returnByValue=$true}).result.value
 Cdp 'Input.dispatchMouseEvent' @{type='mouseMoved';x=$pos.x;y=$pos.y}|Out-Null
 $after=(Cdp 'Runtime.evaluate' @{expression='(()=>{const p=document.querySelector("#service-strip-1"),a=p.querySelector("a[href=\"accounts-payable-receivable.html\"]");return {highlightBackground:getComputedStyle(a).backgroundColor,textColor:getComputedStyle(a).color,onlyOneHighlighted:[...p.querySelectorAll("a")].filter(e=>getComputedStyle(e).backgroundColor==="rgb(104, 104, 104)").length}})()';returnByValue=$true}).result.value
 $report=@{before=$before;after=$after}
 $report|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $folder 'submenu-hover-validation.json') -Encoding UTF8
 $report|ConvertTo-Json -Depth 5
 $shot=Cdp 'Page.captureScreenshot' @{format='png';captureBeyondViewport=$false}
 [IO.File]::WriteAllBytes((Join-Path $folder 'submenu-hover-desktop.png'),[Convert]::FromBase64String($shot.data))
 Cdp 'Browser.close'|Out-Null
}finally{if($socket){$socket.Dispose()}}