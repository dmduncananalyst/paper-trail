param([int]$Port=9235)
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
 $out=Join-Path (Get-Location) 'verification/mobile-refinements-20261016';$shots=Join-Path $out 'screenshots';New-Item -ItemType Directory -Force -Path $shots|Out-Null
 $evaluate=[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'visual-corrections-eval.js'))
 function Load($route){Cdp 'Page.navigate' @{url=('http://127.0.0.1:8765/'+$route)}|Out-Null;$expression='(async()=>{for(let i=0;i<240;i++){if(location.pathname.endsWith('+($route|ConvertTo-Json -Compress)+')&&document.readyState==="complete"&&window.paperTrailUI){localStorage.setItem("paper-trail-language","en");const s=document.querySelector("#language");if(s){s.value="en";s.dispatchEvent(new Event("change"))}document.documentElement.style.scrollBehavior="auto";await document.fonts.ready;document.querySelectorAll("img").forEach(i=>i.loading="eager");await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));return true}await new Promise(r=>setTimeout(r,50))}throw Error("Page not ready")})()';$r=Cdp 'Runtime.evaluate' @{expression=$expression;awaitPromise=$true;returnByValue=$true};if($r.exceptionDetails){throw ($r.exceptionDetails|ConvertTo-Json -Depth 3)}}
 function Shot($name){$shot=Cdp 'Page.captureScreenshot' @{format='png';captureBeyondViewport=$false};[IO.File]::WriteAllBytes((Join-Path $shots ($name+'.png')),[Convert]::FromBase64String($shot.data))}
 $results=@();$desktop=@()
 $routes=@('index.html','about.html','transaction-categorization.html','areas-we-serve.html','year-end-bookkeeping-questions.html','blog.html','monthly-financial-reports.html','notes.html')
 foreach($width in @(1440,834,390,320,430)) {
 Cdp 'Emulation.setDeviceMetricsOverride' @{width=$width;height=1100;deviceScaleFactor=1;mobile=($width -lt 600)}|Out-Null
 $jobs=if($width -eq 390){@((Get-ChildItem -File *.html).Name)+@((Get-ChildItem -File state-records/*.html|ForEach-Object {'state-records/'+$_.Name}))}else{$routes}
 foreach($route in $jobs){
 Load $route
 $r=Cdp 'Runtime.evaluate' @{expression='(()=>{const box=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height}};return {width:innerWidth,scrollWidth:document.documentElement.scrollWidth,clientWidth:document.documentElement.clientWidth,menu:[...document.querySelectorAll(".pt-nav>a,.nav-family>a")].map(e=>({text:e.textContent,rect:box(e)})),bottom:[...document.querySelectorAll(".conversation-invitation .action")].map(e=>({label:e.textContent,rect:box(e),parent:box(e.parentElement)})),cards:[...document.querySelectorAll(".service-notes .photo-card,.pt-about .about-service-choices>a")].map(e=>({card:box(e),image:box(e.querySelector("img")),naturalWidth:e.querySelector("img").naturalWidth})),dates:[...document.querySelectorAll(".publication-date")].map(e=>getComputedStyle(e).textAlign),topicTitles:[...document.querySelectorAll(".pt-topic .blog-story h2")].map(e=>getComputedStyle(e).textAlign),contactTitle:document.querySelector(".contact-main>h1")?box(document.querySelector(".contact-main>h1")):null,location:document.querySelector(".footer-location")?.textContent,missing:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src)}})()';returnByValue=$true};$results+=@{page=$route;viewport=$width;state=$r.result.value}
 if($width -eq 1440){$r=Cdp 'Runtime.evaluate' @{expression='[...document.querySelectorAll("main *, .pt-header *, .pt-footer *")].filter(e=>!e.closest("svg")&&e.getClientRects().length).map(e=>{const r=e.getBoundingClientRect();return {tag:e.tagName,cls:e.className,text:e.children.length?null:e.textContent.trim(),x:r.x,y:r.y,w:r.width,h:r.height}})';returnByValue=$true};$desktop+=@{page=$route;elements=$r.result.value}}
 if($route -in $routes){Shot ($route.Replace('.html','')+'-'+$width)
 if($route -eq 'index.html'){Cdp 'Runtime.evaluate' @{expression='document.querySelector(".home-notes").scrollIntoView({block:"start",behavior:"instant"});true'}|Out-Null;Shot ('home-notes-'+$width)}
 if($route -eq 'transaction-categorization.html' -or $route -eq 'monthly-financial-reports.html'){Cdp 'Runtime.evaluate' @{expression='document.querySelector(".service-notes").scrollIntoView({block:"start",behavior:"instant"});true'}|Out-Null;Shot ($route.Replace('.html','')+'-cards-'+$width);Cdp 'Runtime.evaluate' @{expression='document.querySelector(".conversation-section").scrollIntoView({block:"start",behavior:"instant"});true'}|Out-Null;Shot ($route.Replace('.html','')+'-bottom-'+$width)}
 if($route -eq 'about.html'){Cdp 'Runtime.evaluate' @{expression='document.querySelector(".about-services").scrollIntoView({block:"start",behavior:"instant"});true'}|Out-Null;Shot ('about-cards-'+$width)}
 }
 }
 'Checked '+$jobs.Count+' pages at '+$width
 }
 $results|ConvertTo-Json -Depth 14|Set-Content (Join-Path $out 'browser-checks.json') -Encoding UTF8
 $desktop|ConvertTo-Json -Depth 10|Set-Content (Join-Path $out 'desktop-after.json') -Encoding UTF8
 $script:exceptions|ConvertTo-Json -Depth 8|Set-Content (Join-Path $out 'runtime-exceptions.json') -Encoding UTF8
 Cdp 'Browser.close'|Out-Null
}finally{if($socket){$socket.Dispose()}}
