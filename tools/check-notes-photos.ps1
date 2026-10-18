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
 foreach($width in @(1440,1180,390)){
  $height=1100
  Cdp 'Emulation.setDeviceMetricsOverride' @{width=$width;height=$height;deviceScaleFactor=1;mobile=($width -lt 600)}|Out-Null
  Cdp 'Page.navigate' @{url='http://127.0.0.1:8765/verification/phase-a/home.html'}|Out-Null
  Start-Sleep -Milliseconds 700
  $state=(Cdp 'Runtime.evaluate' @{expression='(async()=>{await document.fonts.ready;for(let i=0;i<20&&!window.paperTrailPreview;i++)await new Promise(r=>setTimeout(r,100));const select=document.querySelector("#language");select.value="en";select.dispatchEvent(new Event("change"));document.querySelectorAll("img").forEach(i=>i.loading="eager");await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));const sizes=s=>[...document.querySelectorAll(s)].map(i=>{const r=i.getBoundingClientRect();return {src:i.getAttribute("src"),width:r.width,height:r.height,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight,fit:getComputedStyle(i).objectFit,ratioError:Math.abs(r.width/r.height-i.naturalWidth/i.naturalHeight)}});const service=sizes(".service-tile>img"),notes=sizes(".home-note>img");document.querySelector("#home-notes").scrollIntoView();return {width:innerWidth,scrollWidth:document.documentElement.scrollWidth,serviceImages:service,noteImages:notes,notesAtLeastServiceSize:notes.every(n=>n.width>=service[0].width&&n.height>=service[0].height),noAddedCropping:notes.every(n=>n.ratioError<0.01),labels:[...document.querySelectorAll(".hero-service-action")].map(x=>x.textContent)}})()';awaitPromise=$true;returnByValue=$true}).result.value
  $report+=@{page='home';width=$width;state=$state}
  Start-Sleep -Milliseconds 350
  $shot=Cdp 'Page.captureScreenshot' @{format='png';captureBeyondViewport=$false}
  [IO.File]::WriteAllBytes((Join-Path $folder ('home-notes-'+$width+'.png')),[Convert]::FromBase64String($shot.data))
  if($width -eq 1440){Cdp 'Runtime.evaluate' @{expression='document.querySelectorAll(".home-note")[2].scrollIntoView()'}|Out-Null;Start-Sleep -Milliseconds 300;$shot=Cdp 'Page.captureScreenshot' @{format='png';captureBeyondViewport=$false};[IO.File]::WriteAllBytes((Join-Path $folder 'home-notes-expenses-desktop.png'),[Convert]::FromBase64String($shot.data))}
  Cdp 'Page.navigate' @{url='http://127.0.0.1:8765/verification/phase-a/notes.html'}|Out-Null
  Start-Sleep -Milliseconds 700
  $state=(Cdp 'Runtime.evaluate' @{expression='(async()=>{await document.fonts.ready;document.querySelectorAll("img").forEach(i=>i.loading="eager");await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));return {width:innerWidth,scrollWidth:document.documentElement.scrollWidth,photos:[...document.querySelectorAll(".topic-row>img")].map(i=>({src:i.getAttribute("src"),width:i.getBoundingClientRect().width,height:i.getBoundingClientRect().height,ratioError:Math.abs(i.getBoundingClientRect().width/i.getBoundingClientRect().height-i.naturalWidth/i.naturalHeight)}))}})()';awaitPromise=$true;returnByValue=$true}).result.value
  $report+=@{page='notes';width=$width;state=$state}
  $shot=Cdp 'Page.captureScreenshot' @{format='png';captureBeyondViewport=$false}
  [IO.File]::WriteAllBytes((Join-Path $folder ('notes-photos-'+$width+'.png')),[Convert]::FromBase64String($shot.data))
 }
 $locales=(Cdp 'Runtime.evaluate' @{expression='window.PAPER_TRAIL_LOCALES';returnByValue=$true}).result.value
 foreach($locale in $locales.PSObject.Properties){$locale.Value|ConvertTo-Json -Depth 6|Set-Content -LiteralPath (Join-Path $folder ('locales/'+$locale.Name+'.draft.json')) -Encoding UTF8}
 $report|ConvertTo-Json -Depth 10|Set-Content -LiteralPath (Join-Path $folder 'notes-photo-validation.json') -Encoding UTF8
 $report|Where-Object page -EQ 'home'|ForEach-Object { [pscustomobject]@{page=$_.page;width=$_.width;scrollWidth=$_.state.scrollWidth;serviceWidth=$_.state.serviceImages[0].width;noteWidth=$_.state.noteImages[0].width;notesAtLeastServiceSize=$_.state.notesAtLeastServiceSize;noAddedCropping=$_.state.noAddedCropping} }|ConvertTo-Json
 Cdp 'Browser.close'|Out-Null
}finally{if($socket){$socket.Dispose()}}