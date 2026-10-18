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
 Cdp 'Emulation.setDeviceMetricsOverride' @{width=1440;height=1100;deviceScaleFactor=1;mobile=$false}|Out-Null
 foreach($page in @('home','notes')){
 Cdp 'Page.navigate' @{url=('http://127.0.0.1:8765/verification/phase-a/'+$page+'.html?update=gray-hover')}|Out-Null
 Start-Sleep -Milliseconds 500
 $selector=if($page -eq 'home'){'.home-note'}else{'.topic-row'}
 $ready='(async()=>{await document.fonts.ready;document.querySelector("#language").value="en";document.querySelector("#language").dispatchEvent(new Event("change"));document.querySelectorAll("img").forEach(i=>i.loading="eager");await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));document.querySelector("'+$selector+'").scrollIntoView({block:"center",behavior:"instant"});return true})()'
 Cdp 'Runtime.evaluate' @{expression=$ready;awaitPromise=$true;returnByValue=$true}|Out-Null
 foreach($target in @('h3,h2','.action')){
 $pos=(Cdp 'Runtime.evaluate' @{expression=('(()=>{const e=document.querySelector("'+$selector+'").querySelector("'+$target+'"),r=e.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()');returnByValue=$true}).result.value
 Cdp 'Input.dispatchMouseEvent' @{type='mouseMoved';x=$pos.x;y=$pos.y}|Out-Null
 Start-Sleep -Milliseconds 150
 $state=(Cdp 'Runtime.evaluate' @{expression=('(()=>{const c=document.querySelector("'+$selector+'"),t=c.querySelector("h3,h2"),b=c.querySelector(".action");return {cardBackground:getComputedStyle(c).backgroundColor,titleDecoration:getComputedStyle(t).textDecorationLine,buttonBackground:getComputedStyle(b).backgroundColor,buttonText:getComputedStyle(b).color,overflow:document.documentElement.scrollWidth>innerWidth}})()');returnByValue=$true}).result.value
 $report+=@{page=$page;target=$target;state=$state}
 $shot=Cdp 'Page.captureScreenshot' @{format='png';captureBeyondViewport=$false}
 $name=if($target -eq '.action'){'button'}else{'card'}
 [IO.File]::WriteAllBytes((Join-Path $folder ('gray-hover-'+$page+'-'+$name+'.png')),[Convert]::FromBase64String($shot.data))
 }
 }
 $report|ConvertTo-Json -Depth 6|Set-Content -LiteralPath (Join-Path $folder 'gray-hover-validation.json') -Encoding UTF8
 $report|ConvertTo-Json -Depth 5
 Cdp 'Browser.close'|Out-Null
}finally{if($socket){$socket.Dispose()}}