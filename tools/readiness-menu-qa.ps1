param([int]$Port=9253)
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
  $socket.SendAsync([ArraySegment[byte]]::new($bytes),[Net.WebSockets.WebSocketMessageType]::Text,$true,[Threading.CancellationToken]::None).GetAwaiter().GetResult()|Out-Null
  while($true){$stream=[IO.MemoryStream]::new();do{$buffer=New-Object byte[] 65536;$read=$socket.ReceiveAsync([ArraySegment[byte]]::new($buffer),[Threading.CancellationToken]::None).GetAwaiter().GetResult();$stream.Write($buffer,0,$read.Count)}while(!$read.EndOfMessage);$reply=[Text.Encoding]::UTF8.GetString($stream.ToArray())|ConvertFrom-Json;$stream.Dispose();if($reply.method -eq 'Network.requestWillBeSent'){$script:requests+=$reply.params.request.url};if($reply.method -eq 'Runtime.exceptionThrown'){$script:exceptions+=$reply.params.exceptionDetails};if($reply.id -eq $id){if($reply.error){throw ($reply.error|ConvertTo-Json -Compress)};return $reply.result}}
 }
 Cdp 'Page.enable'|Out-Null
 Cdp 'Network.enable'|Out-Null
 Cdp 'Runtime.enable'|Out-Null
 Cdp 'Network.setBlockedURLs' @{urls=@('*cloudtranslation*','*translation.googleapis.com/*','*translate.googleapis.com/*','https://api.hsforms.com/*','*/api/chat','*/api/inquiry')}|Out-Null
 Cdp 'Emulation.setFocusEmulationEnabled' @{enabled=$true}|Out-Null
 $out=Join-Path (Get-Location) 'verification/dns-readiness-20261016';$shots=Join-Path $out 'screenshots';New-Item -ItemType Directory -Force -Path $shots|Out-Null
 $evaluate=[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'visual-corrections-eval.js'))
 function Load($route){
 Cdp 'Runtime.evaluate' @{expression='try{localStorage.setItem("paper-trail-language","en")}catch{};true'}|Out-Null
 Cdp 'Page.navigate' @{url=('http://127.0.0.1:8765/'+$route)}|Out-Null
 $expression='(async()=>{for(let i=0;i<300;i++){if(location.pathname.endsWith('+($route|ConvertTo-Json -Compress)+')&&document.readyState==="complete"&&window.paperTrailUI){document.documentElement.style.scrollBehavior="auto";await document.fonts.ready;document.querySelectorAll("img").forEach(i=>i.loading="eager");await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));return true}await new Promise(r=>setTimeout(r,50))}throw Error("Page not ready")})()'
 $r=Cdp 'Runtime.evaluate' @{expression=$expression;awaitPromise=$true;returnByValue=$true};if($r.exceptionDetails){throw ($r.exceptionDetails|ConvertTo-Json -Depth 4)}
 }
 function Shot($name){$shot=Cdp 'Page.captureScreenshot' @{format='png';captureBeyondViewport=$false};[IO.File]::WriteAllBytes((Join-Path $shots ($name+'.png')),[Convert]::FromBase64String($shot.data))}




 $menus=@();$persistence=@()
 foreach($width in @(390,834,1440)){
 Cdp 'Emulation.setDeviceMetricsOverride' @{width=$width;height=1100;deviceScaleFactor=1;mobile=($width -lt 600)}|Out-Null
 foreach($language in @('en','es','fa','hy','zh-CN','ko','tl','te','ru','ar')){
 $route=if($language -eq 'en'){'index.html'}else{$language+'/index.html'};Load $route
 foreach($family in @(0,1)){
 $expression='(async()=>{const g=document.querySelectorAll(".nav-family")['+$family+'],a=g.querySelector(":scope>a");a.dispatchEvent(new MouseEvent(innerWidth<=650?"click":"mouseenter",{bubbles:true,cancelable:true}));if(innerWidth>650)g.dispatchEvent(new MouseEvent("mouseenter",{bubbles:true}));await new Promise(r=>setTimeout(r,300));const p=document.getElementById(a.getAttribute("aria-controls")),s=getComputedStyle(p),r=p.getBoundingClientRect(),h=document.querySelector(".pt-header").getBoundingClientRect();return {open:!p.hidden,scrollbar:(["auto","scroll"].includes(s.overflowY)&&p.scrollHeight>p.clientHeight+1)||(["auto","scroll"].includes(s.overflowX)&&p.scrollWidth>p.clientWidth+1),bodyClear:innerWidth>650||h.bottom>=r.bottom,overflow:document.documentElement.scrollWidth>innerWidth+2,links:p.querySelectorAll("a").length}})()'
 $r=Cdp 'Runtime.evaluate' @{expression=$expression;awaitPromise=$true;returnByValue=$true};$menus+=@{width=$width;language=$language;family=$family;result=$r.result.value;error=$r.exceptionDetails}
 if($language -eq 'es' -and $family -eq 1){Shot ('menu-'+$width)}
 if($width -eq 390){Cdp 'Runtime.evaluate' @{expression='document.querySelectorAll(".nav-family> a")['+$family+'].click();true'}|Out-Null}
 }
 }
 }
 Cdp 'Emulation.setDeviceMetricsOverride' @{width=390;height=1100;deviceScaleFactor=1;mobile=$true}|Out-Null
 Load 'es/index.html'
 Cdp 'Runtime.evaluate' @{expression='sessionStorage.clear();document.querySelector("[data-open-chat]").click();document.querySelector(".chat-reset").click();document.querySelector(".chat input").value="ORIGINAL \u00f1 \u0645\u0631\u062d\u0628\u0627";document.querySelector(".send-message").click();true'}|Out-Null
 Load 'hy/index.html'
 $r=Cdp 'Runtime.evaluate' @{expression='document.querySelector("[data-open-chat]").click();({originalKept:[...document.querySelectorAll(".bubble.user")].some(p=>p.textContent==="ORIGINAL \u00f1 \u0645\u0631\u062d\u0628\u0627"),currentQuestionLocalized:document.querySelector(".chat-question").textContent===window.PAPER_TRAIL_CHAT_LOCALES.hy["What about your books needs attention?"],oneQuestion:document.querySelectorAll(".chat-question").length===1})';returnByValue=$true};$persistence+=@{scenario='language navigation preserves original answer';result=$r.result.value}
 Load 'hy/index.html'
 $r=Cdp 'Runtime.evaluate' @{expression='document.querySelector("[data-open-chat]").click();({originalKept:[...document.querySelectorAll(".bubble.user")].some(p=>p.textContent==="ORIGINAL \u00f1 \u0645\u0631\u062d\u0628\u0627"),currentQuestionLocalized:document.querySelector(".chat-question").textContent===window.PAPER_TRAIL_CHAT_LOCALES.hy["What about your books needs attention?"],oneQuestion:document.querySelectorAll(".chat-question").length===1})';returnByValue=$true};$persistence+=@{scenario='reload preserves chat answers and current step';result=$r.result.value};Shot 'hy-chat-restored'
 Cdp 'Runtime.evaluate' @{expression='true';returnByValue=$true}|Out-Null
 @{menus=$menus;persistence=$persistence;exceptions=$script:exceptions;requests=$script:requests}|ConvertTo-Json -Depth 15|Set-Content (Join-Path $out 'menu-persistence-checks.json') -Encoding UTF8
 Cdp 'Browser.close'|Out-Null
}finally{if($socket){$socket.Dispose()}}
