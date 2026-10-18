param([int]$Port=9251)
$ErrorActionPreference='Stop'
$folder=Join-Path $env:TEMP 'paper-trail-audit5-20261016'
$browserProfile=Join-Path $env:TEMP ('paper-trail-preview-'+$Port)
if (!(Test-NetConnection 127.0.0.1 -Port $Port -InformationLevel Quiet -WarningAction SilentlyContinue)) { $browser=Start-Process -FilePath 'C:/Program Files/Google/Chrome/Application/chrome.exe' -ArgumentList @('--headless=new','--disable-gpu','--no-first-run','--no-default-browser-check',"--remote-debugging-port=$Port",('--user-data-dir="'+$browserProfile+'"'),'about:blank') -WindowStyle Hidden -PassThru }
try {
 $target=$null
 for($i=0;$i -lt 40;$i++){try{$targets=Invoke-RestMethod "http://127.0.0.1:$Port/json" -TimeoutSec 2;$target=$targets|Where-Object type -EQ 'page'|Select-Object -First 1;if($target){break}}catch{};Start-Sleep -Milliseconds 250}
 if(!$target){throw 'Local browser debugging endpoint unavailable'}
 $socket=[Net.WebSockets.ClientWebSocket]::new();$socket.ConnectAsync([uri]$target.webSocketDebuggerUrl,[Threading.CancellationToken]::None).GetAwaiter().GetResult()
 $script:requestId=0;$script:requests=@();$script:exceptions=@()
 function Cdp($method,$params=@{}) {
  $script:requestId++;$id=$script:requestId
  $msg=@{id=$id;method=$method;params=$params}|ConvertTo-Json -Depth 15 -Compress
  $bytes=[Text.Encoding]::UTF8.GetBytes($msg)
  $socket.SendAsync([ArraySegment[byte]]::new($bytes),[Net.WebSockets.WebSocketMessageType]::Text,$true,[Threading.CancellationToken]::None).GetAwaiter().GetResult()
  while($true){$stream=[IO.MemoryStream]::new();do{$buffer=New-Object byte[] 65536;$read=$socket.ReceiveAsync([ArraySegment[byte]]::new($buffer),[Threading.CancellationToken]::None).GetAwaiter().GetResult();$stream.Write($buffer,0,$read.Count)}while(!$read.EndOfMessage);$reply=[Text.Encoding]::UTF8.GetString($stream.ToArray())|ConvertFrom-Json;$stream.Dispose();if($reply.method -eq 'Network.requestWillBeSent'){$script:requests+=$reply.params.request.url};if($reply.method -eq 'Runtime.exceptionThrown'){$script:exceptions+=$reply.params.exceptionDetails};if($reply.id -eq $id){if($reply.error){throw ($reply.error|ConvertTo-Json -Compress)};return $reply.result}}
 }
 Cdp 'Page.enable'|Out-Null
 Cdp 'Network.enable'|Out-Null
 Cdp 'Runtime.enable'|Out-Null
 Cdp 'Network.setBlockedURLs' @{urls=@('*cloudtranslation*','*translation.googleapis.com/*','*translate.googleapis.com/*','https://api.hsforms.com/*','*/api/chat','*/api/inquiry')}|Out-Null
 Cdp 'Emulation.setFocusEmulationEnabled' @{enabled=$true}|Out-Null
 $out=Join-Path (Get-Location) 'verification/google-translation-20261016';$shots=Join-Path $out 'screenshots';New-Item -ItemType Directory -Force -Path $shots|Out-Null
 $evaluate=[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'visual-corrections-eval.js'))
 function Load($route){
 Cdp 'Runtime.evaluate' @{expression='try{localStorage.setItem("paper-trail-language","en")}catch{};true'}|Out-Null
 Cdp 'Page.navigate' @{url=('http://127.0.0.1:8765/'+$route)}|Out-Null
 $expression='(async()=>{for(let i=0;i<300;i++){if(location.pathname.endsWith('+($route|ConvertTo-Json -Compress)+')&&document.readyState==="complete"&&window.paperTrailUI){document.documentElement.style.scrollBehavior="auto";await document.fonts.ready;document.querySelectorAll("img").forEach(i=>i.loading="eager");await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));return true}await new Promise(r=>setTimeout(r,50))}throw Error("Page not ready")})()'
 $r=Cdp 'Runtime.evaluate' @{expression=$expression;awaitPromise=$true;returnByValue=$true};if($r.exceptionDetails){throw ($r.exceptionDetails|ConvertTo-Json -Depth 4)}
 }
 function Shot($name){$shot=Cdp 'Page.captureScreenshot' @{format='png';captureBeyondViewport=$false};[IO.File]::WriteAllBytes((Join-Path $shots ($name+'.png')),[Convert]::FromBase64String($shot.data))}


 $layout=@();$chatChecks=@()
 foreach($width in @(390,834,1440)){
 Cdp 'Emulation.setDeviceMetricsOverride' @{width=$width;height=1100;deviceScaleFactor=1;mobile=($width -lt 600)}|Out-Null
 foreach($language in @('es','fa','hy','zh-CN')){
 foreach($page in @('index.html','blog.html','about.html','monthly-financial-reports.html','state-records/california.html')){
 $route=$language+'/'+$page;Load $route
 $r=Cdp 'Runtime.evaluate' @{expression='(()=>{const c=document.querySelector(".translation-credit"),r=c.getBoundingClientRect(),last=document.querySelector("main").lastElementChild;return {language:document.documentElement.lang,staticLocale:document.documentElement.dataset.staticLocale,overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+2,images:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src),h1:document.querySelector("h1").textContent,selectors:document.querySelectorAll("#language").length,creditAtBottom:c===last,creditWidth:r.width,canonical:document.querySelector("link[rel=canonical]").href,noticeCount:document.querySelectorAll(".translation-notice,.article-language").length}})()';returnByValue=$true};if($r.exceptionDetails){throw ($r.exceptionDetails|ConvertTo-Json -Depth 4)};$layout+=@{page=$page;language=$language;width=$width;result=$r.result.value}
 if($language -in @('es','fa','hy') -and $page -in @('index.html','monthly-financial-reports.html','state-records/california.html')){Shot ($language+'-'+$page.Replace('/','-').Replace('.html','')+'-'+$width)}
 if($page -eq 'blog.html'){
 Cdp 'Runtime.evaluate' @{expression='document.querySelector(".translation-credit").scrollIntoView({block:"end",behavior:"instant"});true'}|Out-Null;Shot ($language+'-credit-'+$width)
 }
 }
 }
 'Checked translated layouts '+$width
 }
 Cdp 'Emulation.setDeviceMetricsOverride' @{width=390;height=1100;deviceScaleFactor=1;mobile=$true}|Out-Null
 foreach($language in @('es','fa','hy','zh-CN')){
 foreach($page in @('index.html','blog.html','monthly-financial-reports.html')){
 Load ($language+'/'+$page)
 $r=Cdp 'Runtime.evaluate' @{expression='(()=>{document.querySelector("[data-open-chat]").click();const q=document.querySelector(".chat-question").textContent,dictionary=window.PAPER_TRAIL_CHAT_LOCALES[document.documentElement.dataset.staticLocale];return {question:q,expected:dictionary["What state are you located in?"],notice:document.querySelectorAll(".chat-language-note").length,dir:document.querySelector(".chat").dir}})()';returnByValue=$true};$chatChecks+=@{language=$language;page=$page;result=$r.result.value};if($page -eq 'index.html'){Shot ($language+'-chat')}
 }
 }
 @{layouts=$layout;chats=$chatChecks;exceptions=$script:exceptions;requests=$script:requests}|ConvertTo-Json -Depth 14|Set-Content (Join-Path $out 'browser-preview-checks.json') -Encoding UTF8
 Cdp 'Browser.close'|Out-Null
}finally{if($socket){$socket.Dispose()}}
