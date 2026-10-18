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
 foreach($width in @(1440,390,320)){
 Cdp 'Emulation.setDeviceMetricsOverride' @{width=$width;height=950;deviceScaleFactor=1;mobile=($width -lt 600)}|Out-Null
 Cdp 'Page.navigate' @{url='http://127.0.0.1:8765/verification/phase-a/home.html?update=footer'}|Out-Null
 Start-Sleep -Milliseconds 700
 $state=(Cdp 'Runtime.evaluate' @{expression='(async()=>{await document.fonts.ready;document.querySelectorAll("img").forEach(i=>i.loading="eager");await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));const s=document.querySelector("#language");s.value="en";s.dispatchEvent(new Event("change"));await new Promise(r=>setTimeout(r,150));const f=document.querySelector(".pt-footer");f.scrollIntoView({block:"start",behavior:"instant"});await new Promise(r=>setTimeout(r,700));f.scrollIntoView({block:"start",behavior:"instant"});const cities=[...f.querySelectorAll(".footer-cities a")];const center=e=>{const r=e.getBoundingClientRect();return r.x+r.width/2};return {width:innerWidth,scrollWidth:document.documentElement.scrollWidth,allFooterLinksUnderlined:[...f.querySelectorAll("a,button[data-email]")].every(e=>getComputedStyle(e).textDecorationLine.includes("underline")),clickableCount:f.querySelectorAll("a,button[data-email]").length,cityCount:cities.length,citiesUnderlined:cities.every(a=>getComputedStyle(a).textDecorationLine.includes("underline")),cityTargets:cities.map(a=>({text:a.textContent,href:a.getAttribute("href")})),footerTextAlign:getComputedStyle(f).textAlign,contentCenters:[...f.querySelectorAll(".footer-location,.footer-contact>a,.footer-contact>button,.footer-bottom>*")].map(e=>({label:e.textContent,center:center(e),difference:Math.abs(center(e)-center(f))})),footerNavigation:getComputedStyle(f.querySelector("nav")).justifyContent}})()';awaitPromise=$true;returnByValue=$true}).result.value
 $report+=$state
 Start-Sleep -Milliseconds 200
 $shot=Cdp 'Page.captureScreenshot' @{format='png';captureBeyondViewport=$false}
 [IO.File]::WriteAllBytes((Join-Path $folder ('footer-centered-'+$width+'.png')),[Convert]::FromBase64String($shot.data))
 }
 $report|ConvertTo-Json -Depth 8|Set-Content -LiteralPath (Join-Path $folder 'footer-validation.json') -Encoding UTF8
 $report|ForEach-Object{[pscustomobject]@{width=$_.width;allFooterLinksUnderlined=$_.allFooterLinksUnderlined;clickableCount=$_.clickableCount;cityCount=$_.cityCount;citiesUnderlined=$_.citiesUnderlined;footerTextAlign=$_.footerTextAlign;overflow=($_.scrollWidth -gt $_.width);maxCenterDifference=($_.contentCenters.difference|Measure-Object -Maximum).Maximum}}|ConvertTo-Json
 Cdp 'Browser.close'|Out-Null
}finally{if($socket){$socket.Dispose()}}