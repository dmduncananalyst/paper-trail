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
 foreach($page in @('home','notes','blog')){
 Cdp 'Page.navigate' @{url=('http://127.0.0.1:8765/verification/phase-a/'+$page+'.html?update=icons')}|Out-Null
 Start-Sleep -Milliseconds 600
 $state=(Cdp 'Runtime.evaluate' @{expression='(async()=>{await document.fonts.ready;const s=document.querySelector("#language");s.value="en";s.dispatchEvent(new Event("change"));document.querySelectorAll("img").forEach(i=>i.loading="eager");await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));const icons=[...document.querySelectorAll("main .pt-icon")];const rows=[...document.querySelectorAll(".topic-row")];const phone=document.querySelector(".header-tools a[href^=tel]");const blogActions=[...document.querySelectorAll(".blog-story .action")];return {backgrounds:["body",".pt-header",".pt-footer",".hero-service-links"].map(s=>{const e=document.querySelector(s);return e?{selector:s,color:getComputedStyle(e).backgroundColor}:null}).filter(Boolean),logoFilter:getComputedStyle(document.querySelector(".brand-lettering")).filter,allPhotosLoaded:[...document.querySelectorAll(".topic-row img,.home-note img")].every(i=>i.complete&&i.naturalWidth>0),phoneHref:phone.getAttribute("href"),phoneUnderlined:getComputedStyle(phone).textDecorationLine.includes("underline"),blogActions:blogActions.map(e=>{const r=e.getBoundingClientRect(),p=e.parentElement.getBoundingClientRect();return {centerOffset:Math.abs(r.x+r.width/2-p.x-p.width/2)}}),width:innerWidth,scrollWidth:document.documentElement.scrollWidth,titleIconAlignment:rows.map(r=>{const a=r.querySelector(".topic-emblem").getBoundingClientRect(),b=r.querySelector("h2").getBoundingClientRect();return Math.abs((a.y+a.height/2)-(b.y+b.height/2))}),creditPlain:getComputedStyle(document.querySelector("[data-i18n=credit]")).textDecorationLine,creditBrandUnderlined:getComputedStyle(document.querySelector(".credit-brand")).textDecorationLine,readActions:[...document.querySelectorAll(".home-note .action,.topic-row>.action")].map(e=>{const r=e.getBoundingClientRect(),c=e.closest(".topic-row,.home-note"),title=c.querySelector("h2,h3").getBoundingClientRect();return {font:getComputedStyle(e).fontSize,height:r.height,border:getComputedStyle(e).borderTopWidth,marginTop:getComputedStyle(e).marginTop,centerOffset:Math.abs(r.x+r.width/2-title.x-title.width/2)}}),topicRows:rows.length,rowsInsideGrid:document.querySelectorAll(".topic-index>.topic-row").length,allRowsInsideMain:rows.every(r=>r.closest("main")),homeNotes:document.querySelectorAll(".home-note").length,uniqueIcons:new Set(icons.map(i=>i.innerHTML)).size===icons.length,iconsDrawn:icons.every(i=>i.children.length),footerPresent:!!document.querySelector(".pt-footer")}})()';awaitPromise=$true;returnByValue=$true}).result.value
 $report+=@{page=$page;width=$width;state=$state}
 $shot=Cdp 'Page.captureScreenshot' @{format='png';captureBeyondViewport=$false}
 [IO.File]::WriteAllBytes((Join-Path $folder ('restored-'+$page+'-'+$width+'.png')),[Convert]::FromBase64String($shot.data))
 }
 }
 $report|ConvertTo-Json -Depth 7|Set-Content -LiteralPath (Join-Path $folder 'notes-restoration-validation.json') -Encoding UTF8
 $report|ConvertTo-Json -Depth 5
 Cdp 'Browser.close'|Out-Null
}finally{if($socket){$socket.Dispose()}}