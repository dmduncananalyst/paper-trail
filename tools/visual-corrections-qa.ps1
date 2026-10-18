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
 $out=Join-Path (Get-Location) 'verification/visual-corrections';$shots=Join-Path $out 'screenshots';New-Item -ItemType Directory -Force -Path $shots|Out-Null
 $evaluate=[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'visual-corrections-eval.js'))
 function Load($route){Cdp 'Page.navigate' @{url=('http://127.0.0.1:8765/'+$route)}|Out-Null;$expression='(async()=>{for(let i=0;i<240;i++){if(location.pathname.endsWith('+($route|ConvertTo-Json -Compress)+')&&document.readyState==="complete"&&window.paperTrailUI){localStorage.setItem("paper-trail-language","en");const s=document.querySelector("#language");if(s){s.value="en";s.dispatchEvent(new Event("change"))}document.documentElement.style.scrollBehavior="auto";await document.fonts.ready;document.querySelectorAll("img").forEach(i=>i.loading="eager");await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));return true}await new Promise(r=>setTimeout(r,50))}throw Error("Page not ready")})()';$r=Cdp 'Runtime.evaluate' @{expression=$expression;awaitPromise=$true;returnByValue=$true};if($r.exceptionDetails){throw ($r.exceptionDetails|ConvertTo-Json -Depth 3)}}
 function Shot($name){$shot=Cdp 'Page.captureScreenshot' @{format='png';captureBeyondViewport=$false};[IO.File]::WriteAllBytes((Join-Path $shots ($name+'.png')),[Convert]::FromBase64String($shot.data))}
 $jobs=@(@('index.html','home'),@('about.html','about'),@('paper-trail-services.html','repair-video'),@('paper-trail-monthly-bookkeeping.html','monthly-video'),@('balancing-corrections.html','balances'),@('transaction-categorization.html','notes-cards'),@('nationwide-bookkeeping.html','nationwide'),@('blog.html','blog'),@('notes.html','notes-english'),@('accounts-payable-receivable.html','payment-responsibilities'),@('services.html','services'),@('past-due-bookkeeping.html','past-due-bookkeeping'),@('year-end-bookkeeping.html','year-end-bookkeeping'),@('tax-ready-bookkeeping.html','tax-ready-bookkeeping'),@('income-expense-tracking.html','income-expense-tracking'),@('bank-credit-card-balancing.html','bank-credit-card-balancing'),@('monthly-financial-reports.html','monthly-financial-reports'),@('monthly-bookkeeping-review.html','monthly-bookkeeping-review'),@('catch-up-bookkeeping-overdue-books.html','catch-up-bookkeeping-overdue-books'),@('profit-vs-cash-flow-business-money.html','profit-vs-cash-flow-business-money'),@('tax-ready-bookkeeping-records.html','tax-ready-bookkeeping-records'),@('state-records/alabama.html','state-alabama'),@('state-records/alaska.html','state-alaska'),@('state-records/arizona.html','state-arizona'),@('state-records/arkansas.html','state-arkansas'),@('state-records/california.html','state-california'),@('state-records/colorado.html','state-colorado'),@('state-records/connecticut.html','state-connecticut'),@('state-records/delaware.html','state-delaware'),@('state-records/florida.html','state-florida'),@('state-records/georgia.html','state-georgia'),@('state-records/hawaii.html','state-hawaii'),@('state-records/idaho.html','state-idaho'),@('state-records/illinois.html','state-illinois'),@('state-records/indiana.html','state-indiana'),@('state-records/iowa.html','state-iowa'),@('state-records/kansas.html','state-kansas'),@('state-records/kentucky.html','state-kentucky'),@('state-records/louisiana.html','state-louisiana'),@('state-records/maine.html','state-maine'),@('state-records/maryland.html','state-maryland'),@('state-records/massachusetts.html','state-massachusetts'),@('state-records/michigan.html','state-michigan'),@('state-records/minnesota.html','state-minnesota'),@('state-records/mississippi.html','state-mississippi'),@('state-records/missouri.html','state-missouri'),@('state-records/montana.html','state-montana'),@('state-records/nebraska.html','state-nebraska'),@('state-records/nevada.html','state-nevada'),@('state-records/new-hampshire.html','state-new-hampshire'),@('state-records/new-jersey.html','state-new-jersey'),@('state-records/new-mexico.html','state-new-mexico'),@('state-records/new-york.html','state-new-york'),@('state-records/north-carolina.html','state-north-carolina'),@('state-records/north-dakota.html','state-north-dakota'),@('state-records/ohio.html','state-ohio'),@('state-records/oklahoma.html','state-oklahoma'),@('state-records/oregon.html','state-oregon'),@('state-records/pennsylvania.html','state-pennsylvania'),@('state-records/rhode-island.html','state-rhode-island'),@('state-records/south-carolina.html','state-south-carolina'),@('state-records/south-dakota.html','state-south-dakota'),@('state-records/tennessee.html','state-tennessee'),@('state-records/texas.html','state-texas'),@('state-records/utah.html','state-utah'),@('state-records/vermont.html','state-vermont'),@('state-records/virginia.html','state-virginia'),@('state-records/washington.html','state-washington'),@('state-records/west-virginia.html','state-west-virginia'),@('state-records/wisconsin.html','state-wisconsin'),@('state-records/wyoming.html','state-wyoming'))
 $report=@()
 foreach($width in @(1440,834,390)){
  Cdp 'Emulation.setDeviceMetricsOverride' @{width=$width;height=1100;deviceScaleFactor=1;mobile=($width -lt 600)}|Out-Null
  foreach($job in $jobs){
   Load $job[0]
   $state=Cdp 'Runtime.evaluate' @{expression=$evaluate;returnByValue=$true};$report+=@{page=$job[0];viewport=$width;state=$state.result.value}
   Shot ($job[1]+'-'+$width)
   if($job[1] -eq 'payment-responsibilities'){Cdp 'Runtime.evaluate' @{expression='[...document.querySelectorAll(".work-card")].find(e=>e.querySelector("h3")?.textContent==="Payment Responsibilities").scrollIntoView({block:"start",behavior:"instant"});true'}|Out-Null;Shot ('payment-card-'+$width)}
   if($job[1] -eq 'home'){Cdp 'Runtime.evaluate' @{expression='document.querySelector(".home-notes").scrollIntoView({block:"start",behavior:"instant"});true'}|Out-Null;Shot ('home-notes-'+$width)}
   if($job[1] -eq 'balances'){Cdp 'Runtime.evaluate' @{expression='document.querySelector(".work-board").scrollIntoView({block:"start",behavior:"instant"});true'}|Out-Null;Shot ('balances-cards-'+$width)}
   if($job[1] -eq 'notes-cards'){Cdp 'Runtime.evaluate' @{expression='document.querySelector(".service-notes").scrollIntoView({block:"start",behavior:"instant"});true'}|Out-Null;Shot ('notes-cards-detail-'+$width)}
   if($job[1] -eq 'about'){Cdp 'Runtime.evaluate' @{expression='document.querySelector(".about-process-cards").scrollIntoView({block:"start",behavior:"instant"});true'}|Out-Null;Shot ('about-folios-'+$width)}
  }
  'Checked '+$jobs.Count+' pages at '+$width+'px'
 }
 $languageTests=@()
 foreach($testWidth in @(1440,834,390)){
 Cdp 'Emulation.setDeviceMetricsOverride' @{width=$testWidth;height=1100;deviceScaleFactor=1;mobile=($testWidth -lt 600)}|Out-Null
 foreach($route in @('index.html','blog.html')){
  Load $route
  foreach($code in @('en','es','fa','hy','zh-CN','ko','tl','te','ru','ar')){
   $r=Cdp 'Runtime.evaluate' @{expression=('(async()=>{const s=document.querySelector("#language");s.value='+($code|ConvertTo-Json -Compress)+';s.dispatchEvent(new Event("change"));await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));return '+$evaluate+'})()');awaitPromise=$true;returnByValue=$true}
   $languageTests+=@{page=$route;viewport=$testWidth;language=$code;state=$r.result.value}
   if($code -eq 'es' -or $code -eq 'fa'){Shot ($route.Replace('.html','')+'-'+$code+'-'+$testWidth)}
  }
 }
 }
 # Verify selection persists Home to Blog, but Notes and all other routes stay English.
 Load 'index.html';Cdp 'Runtime.evaluate' @{expression='const s=document.querySelector("#language");s.value="fa";s.dispatchEvent(new Event("change"));true'}|Out-Null
 Cdp 'Page.navigate' @{url='http://127.0.0.1:8765/blog.html'}|Out-Null;Start-Sleep -Milliseconds 800
 $persist=Cdp 'Runtime.evaluate' @{expression='({language:document.documentElement.lang,selection:document.querySelector("#language")?.value})';returnByValue=$true}
 Cdp 'Page.navigate' @{url='http://127.0.0.1:8765/notes.html'}|Out-Null;Start-Sleep -Milliseconds 500
 $english=Cdp 'Runtime.evaluate' @{expression='({language:document.documentElement.lang,selector:!!document.querySelector("#language"),headerPanels:document.querySelectorAll(".pt-header>.nav-panel").length})';returnByValue=$true}
 # Approved dropdown relocation/focus still runs without a language control.
 Cdp 'Runtime.evaluate' @{expression='document.querySelector(".nav-family>a").focus();true'}|Out-Null
 $menu=Cdp 'Runtime.evaluate' @{expression='({expanded:document.querySelector(".nav-family>a").getAttribute("aria-expanded"),shown:[...document.querySelectorAll(".pt-header>.nav-panel")].filter(e=>!e.hidden).length})';returnByValue=$true}
 Shot 'menu-restored-390'
 $translations=@($script:requests|Where-Object {$_ -match 'https?://(?:translation|translate)\.googleapis\.com'})
 $final=@{pageChecks=$report;languageChecks=$languageTests;persistHomeToBlog=$persist.result.value;notesEnglish=$english.result.value;approvedMenu=$menu.result.value;translationRequests=$translations;uncaughtExceptions=$script:exceptions;checkedAt='2026-10-16'}
 $final|ConvertTo-Json -Depth 20|Set-Content (Join-Path $out 'browser-checks.json') -Encoding UTF8
 [pscustomobject]@{pageChecks=$report.Count;languageChecks=$languageTests.Count;layoutFailures=@($report|Where-Object {$_.state.overflow.Count -gt 0 -or $_.state.scrollWidth -gt $_.state.clientWidth+2}).Count;translationRequests=$translations.Count;uncaughtExceptions=$script:exceptions.Count;menu=$menu.result.value}|ConvertTo-Json -Depth 4
 Cdp 'Browser.close'|Out-Null
}finally{if($socket){$socket.Dispose()}}
