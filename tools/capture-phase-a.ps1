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
 $jobs=@(@('notes.html','notes-desktop',1440,1120),@('notes.html','notes-mobile',390,1100),@('article.html','article-desktop',1440,1600),@('article.html','article-mobile',390,1100),@('home.html','home-desktop',1440,1600),@('home.html','home-mobile',390,1100),@('notes.html?menu','menu-desktop',1440,1120),@('notes.html?menu','menu-mobile',390,1100),@('../../index.html','existing-home-desktop',1440,1600),@('../../notes.html','existing-notes-desktop',1440,1120))
 foreach($job in $jobs){
  $name=$job[0];$query='';if($name.Contains('?')){$name=$name.Split('?')[0];$query='?menu'}
  $url=([uri](Join-Path $folder $name)).AbsoluteUri+$query
  Cdp 'Emulation.setDeviceMetricsOverride' @{width=[int]$job[2];height=[int]$job[3];deviceScaleFactor=1;mobile=($job[2]-lt 600)}|Out-Null
  Cdp 'Page.navigate' @{url=$url}|Out-Null
  Start-Sleep -Milliseconds 500
  $ready='(async()=>{await document.fonts.ready;document.querySelectorAll("img").forEach(i=>i.loading="eager");await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));document.querySelectorAll("video").forEach(v=>{v.pause();v.currentTime=0});await new Promise(r=>setTimeout(r,300));return {width:innerWidth,scrollWidth:document.documentElement.scrollWidth,h1:[...document.querySelectorAll("h1")].map(x=>x.textContent),images:[...document.images].map(i=>({src:i.getAttribute("src"),width:i.naturalWidth,complete:i.complete})),menuOpen:document.querySelector(".pt-menu")?.getAttribute("aria-expanded")}})()'
  $state=Cdp 'Runtime.evaluate' @{expression=$ready;awaitPromise=$true;returnByValue=$true}
  $report+=@{page=$job[1];state=$state.result.value}
  $shot=Cdp 'Page.captureScreenshot' @{format='png';captureBeyondViewport=$false}
  [IO.File]::WriteAllBytes((Join-Path $folder ($job[1]+'.png')),[Convert]::FromBase64String($shot.data))
  Write-Output ($job[1]+' '+($state.result.value|ConvertTo-Json -Depth 4 -Compress))
 }
 $report|ConvertTo-Json -Depth 10|Set-Content (Join-Path $folder 'browser-validation.json') -Encoding UTF8
 Cdp 'Browser.close'|Out-Null
}finally{if($socket){$socket.Dispose()}}
