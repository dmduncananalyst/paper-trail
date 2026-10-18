param([int]$Port=9235)
$ErrorActionPreference='Stop'
$folder=Join-Path (Get-Location) 'verification/phase-a/reference-review'
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
 $jobs=@(@('https://startweb7.com/','start-home',1440,1000),@('https://dommydom.com/','dom-home',1440,1000),@('https://paradigmjanitorial.net/','paradigm-home',1440,1000),@('https://startweb7.com/blog.html','start-blog',1440,1000),@('https://dommydom.com/blog.html','dom-blog',1440,1000),@('https://paradigmjanitorial.net/blog.html','paradigm-blog',1440,1000),@('https://startweb7.com/how-craigslist-kept-its-1990s-look-and-outlived-prettier-rivals.html','start-reading',1440,1100),@('https://dommydom.com/blog-lake-balboa-park-japanese-garden-fall-guide.html','dom-reading',1440,1100),@('https://paradigmjanitorial.net/blog-warehouse-break-room-cleaning-2026.html','paradigm-reading',1440,1100))
 foreach($job in $jobs){
  $name=$job[0];$query='';if($name.Contains('?')){$name=$name.Split('?')[0];$query='?menu'}
  $url=$name
  Cdp 'Emulation.setDeviceMetricsOverride' @{width=[int]$job[2];height=[int]$job[3];deviceScaleFactor=1;mobile=($job[2]-lt 600)}|Out-Null
  Cdp 'Page.navigate' @{url=$url}|Out-Null
  Start-Sleep -Milliseconds 1300
  $ready='(async()=>{await Promise.race([document.fonts.ready,new Promise(r=>setTimeout(r,3000))]);document.querySelectorAll("img").forEach(i=>i.loading="eager");await Promise.race([Promise.all([...document.images].map(i=>i.decode().catch(()=>{}))),new Promise(r=>setTimeout(r,5000))]);document.querySelectorAll("video").forEach(v=>{v.pause();v.currentTime=0});await new Promise(r=>setTimeout(r,300));return {width:innerWidth,scrollWidth:document.documentElement.scrollWidth,h1:[...document.querySelectorAll("h1")].map(x=>x.textContent),images:[...document.images].map(i=>({src:i.getAttribute("src"),width:i.naturalWidth,complete:i.complete})),menuOpen:document.querySelector(".pt-menu")?.getAttribute("aria-expanded")}})()'
  $state=Cdp 'Runtime.evaluate' @{expression=$ready;awaitPromise=$true;returnByValue=$true}
  $report+=@{page=$job[1];state=$state.result.value}
  $shot=Cdp 'Page.captureScreenshot' @{format='png';captureBeyondViewport=$false}
  [IO.File]::WriteAllBytes((Join-Path $folder ($job[1]+'.png')),[Convert]::FromBase64String($shot.data))
  Write-Output ($job[1]+' '+($state.result.value|ConvertTo-Json -Depth 4 -Compress))
 }
 $report|ConvertTo-Json -Depth 10|Set-Content (Join-Path $folder 'browser-validation.json') -Encoding UTF8
 Cdp 'Browser.close'|Out-Null
}finally{if($socket){$socket.Dispose()}}
