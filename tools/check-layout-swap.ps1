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
 foreach($width in @(1440,1180,768,390)){
  Cdp 'Emulation.setDeviceMetricsOverride' @{width=$width;height=1100;deviceScaleFactor=1;mobile=($width -lt 600)}|Out-Null
  Cdp 'Page.navigate' @{url='http://127.0.0.1:8765/verification/phase-a/home.html?layout=swap'}|Out-Null
  Start-Sleep -Milliseconds 700
  $state=(Cdp 'Runtime.evaluate' @{expression='(async()=>{await document.fonts.ready;const s=document.querySelector("#language");s.value="en";s.dispatchEvent(new Event("change"));document.querySelectorAll("img").forEach(i=>i.loading="eager");await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));const size=e=>{const r=e.getBoundingClientRect();return {width:r.width,height:r.height}};const images=[...document.querySelectorAll(".service-tile>img,.home-note>img")];const icons=[...document.querySelectorAll("main .pt-icon")];return {width:innerWidth,scrollWidth:document.documentElement.scrollWidth,services:[...document.querySelectorAll(".service-tile")].map(e=>({card:size(e),image:size(e.querySelector("img")),icon:size(e.querySelector("svg"))})),notes:[...document.querySelectorAll(".home-note")].map(e=>({card:size(e),image:size(e.querySelector("img")),icon:size(e.querySelector("svg"))})),photosFillCards:[...document.querySelectorAll(".home-note")].every(c=>Math.abs(c.querySelector("img").getBoundingClientRect().height-(c.getBoundingClientRect().height-2))<2),servicesCentered:[...document.querySelectorAll(".service-copy")].every(c=>{const centers=[...c.children].map(e=>{const r=e.getBoundingClientRect();return r.x+r.width/2});return Math.max(...centers)-Math.min(...centers)<1}),uniqueIcons:new Set(icons.map(i=>i.innerHTML)).size===icons.length,uniqueIconIds:new Set(icons.map(i=>i.dataset.iconId)).size===icons.length,allIconsDrawn:icons.every(i=>i.children.length>0),video:document.querySelector("video source")?.getAttribute("src")||document.querySelector("video")?.getAttribute("src")}})()';awaitPromise=$true;returnByValue=$true}).result.value
  $report+=@{width=$width;state=$state}
  foreach($section in @('services','notes')){
   Cdp 'Runtime.evaluate' @{expression=('document.querySelector("#home-'+$section+'").scrollIntoView()')}|Out-Null
   Start-Sleep -Milliseconds 200
   $shot=Cdp 'Page.captureScreenshot' @{format='png';captureBeyondViewport=$false}
   [IO.File]::WriteAllBytes((Join-Path $folder ('swap-'+$section+'-'+$width+'.png')),[Convert]::FromBase64String($shot.data))
  }
  if($width -in @(1440,390)){
   $rtl=(Cdp 'Runtime.evaluate' @{expression='(async()=>{const s=document.querySelector("#language");s.value="ar";s.dispatchEvent(new Event("change"));await new Promise(r=>setTimeout(r,150));return {width:innerWidth,scrollWidth:document.documentElement.scrollWidth,dir:document.documentElement.dir}})()';awaitPromise=$true;returnByValue=$true}).result.value
   $report+=@{width=$width;rtl=$rtl}
  }
 }
 $report|ConvertTo-Json -Depth 10|Set-Content -LiteralPath (Join-Path $folder 'layout-swap-validation.json') -Encoding UTF8
 $report|ConvertTo-Json -Depth 7
 Cdp 'Browser.close'|Out-Null
}finally{if($socket){$socket.Dispose()}}