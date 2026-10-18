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
 Cdp 'Emulation.setDeviceMetricsOverride' @{width=1440;height=1050;deviceScaleFactor=1;mobile=$false}|Out-Null
 Cdp 'Page.navigate' @{url='http://127.0.0.1:8765/verification/phase-a/review.html?color=emerald&update=rich-colors-4'}|Out-Null
 Start-Sleep -Milliseconds 1000
 foreach($color in @('emerald','teal','terracotta')){
 $js='(async()=>{const color="'+$color+'";for(let i=0;i<40&&!document.querySelector("iframe").contentDocument?.querySelector(".pt-header");i++)await new Promise(r=>setTimeout(r,100));document.querySelector("[data-color="+color+"]").click();await new Promise(r=>setTimeout(r,150));const d=document.querySelector("iframe").contentDocument;return {color,actual:d.documentElement.dataset.colorDirection,header:d.defaultView.getComputedStyle(d.querySelector(".pt-header")).backgroundColor,body:d.defaultView.getComputedStyle(d.body).backgroundColor,pressed:document.querySelector("[data-color="+color+"]").getAttribute("aria-pressed")}})()'
 $report+=(Cdp 'Runtime.evaluate' @{expression=$js;awaitPromise=$true;returnByValue=$true}).result.value
 $shot=Cdp 'Page.captureScreenshot' @{format='png';captureBeyondViewport=$false}
 [IO.File]::WriteAllBytes((Join-Path $folder ('color-option-'+$color+'.png')),[Convert]::FromBase64String($shot.data))
 }
 Cdp 'Runtime.evaluate' @{expression='document.querySelector("[data-color=emerald]").click()'}|Out-Null
 Cdp 'Emulation.setDeviceMetricsOverride' @{width=390;height=1100;deviceScaleFactor=1;mobile=$true}|Out-Null
 Cdp 'Page.navigate' @{url='http://127.0.0.1:8765/verification/phase-a/home.html?update=centered-mobile'}|Out-Null
 Start-Sleep -Milliseconds 600
 $state=(Cdp 'Runtime.evaluate' @{expression='(async()=>{await document.fonts.ready;const s=document.querySelector("#language");s.value="en";s.dispatchEvent(new Event("change"));document.querySelectorAll("img").forEach(i=>i.loading="eager");await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));document.querySelector("#home-notes").scrollIntoView({behavior:"instant"});await new Promise(r=>setTimeout(r,200));return {page:"mobile-home",width:innerWidth,scrollWidth:document.documentElement.scrollWidth,notes:[...document.querySelectorAll(".home-note-copy")].map(c=>{const center=e=>{const r=e.getBoundingClientRect();return r.x+r.width/2};return {iconOffset:Math.abs(center(c.querySelector("svg"))-center(c)),titleOffset:Math.abs(center(c.querySelector("h3"))-center(c)),alignment:getComputedStyle(c).textAlign}})}})()';awaitPromise=$true;returnByValue=$true}).result.value
 $report+=$state
 $shot=Cdp 'Page.captureScreenshot' @{format='png';captureBeyondViewport=$false}
 [IO.File]::WriteAllBytes((Join-Path $folder 'centered-mobile-notes.png'),[Convert]::FromBase64String($shot.data))
 $report|ConvertTo-Json -Depth 8|Set-Content -LiteralPath (Join-Path $folder 'color-options-validation.json') -Encoding UTF8
 $report|ConvertTo-Json -Depth 7
 Cdp 'Browser.close'|Out-Null
}finally{if($socket){$socket.Dispose()}}