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
 $out=Join-Path (Get-Location) 'verification/follow-up-20261016';$shots=Join-Path $out 'screenshots';New-Item -ItemType Directory -Force -Path $shots|Out-Null
 $evaluate=[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'visual-corrections-eval.js'))
 function Load($route){Cdp 'Page.navigate' @{url=('http://127.0.0.1:8765/'+$route)}|Out-Null;$expression='(async()=>{for(let i=0;i<240;i++){if(location.pathname.endsWith('+($route|ConvertTo-Json -Compress)+')&&document.readyState==="complete"&&window.paperTrailUI){localStorage.setItem("paper-trail-language","en");const s=document.querySelector("#language");if(s){s.value="en";s.dispatchEvent(new Event("change"))}document.documentElement.style.scrollBehavior="auto";await document.fonts.ready;document.querySelectorAll("img").forEach(i=>i.loading="eager");await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));return true}await new Promise(r=>setTimeout(r,50))}throw Error("Page not ready")})()';$r=Cdp 'Runtime.evaluate' @{expression=$expression;awaitPromise=$true;returnByValue=$true};if($r.exceptionDetails){throw ($r.exceptionDetails|ConvertTo-Json -Depth 3)}}
 function Shot($name){$shot=Cdp 'Page.captureScreenshot' @{format='png';captureBeyondViewport=$false};[IO.File]::WriteAllBytes((Join-Path $shots ($name+'.png')),[Convert]::FromBase64String($shot.data))}
 Load 'areas-we-serve.html'
 $r=Cdp 'Runtime.evaluate' @{expression='(async()=>{document.querySelector("[data-open-chat]").click();const sequence=[];for(let j=0;j<20;j++){const q=document.querySelector(".chat-question")?.textContent;if(q.startsWith("Here is"))break;sequence.push(q);let a=document.querySelector(".chat-options button");if(a){if(q.includes("meeting"))a=[...document.querySelectorAll(".chat-options button")].find(e=>e.textContent==="Email me first")||a;a.click()}else{const i=document.querySelector(".chat input");i.value=q.includes("state")?"California":q.includes("business do")?"Retail":q.includes("company")?"Example Company":q.includes("name")?"Example Owner":q.includes("email")?"owner@example.com":q.includes("phone")?"8185550123":"Example";document.querySelector(".send-message").click()}}const review=document.querySelector(".chat-question").textContent;[...document.querySelectorAll(".chat-options button")].find(e=>e.textContent==="Change a detail").click();document.querySelector(".chat-options button").click();document.querySelector(".chat input").value="Nevada";document.querySelector(".send-message").click();const edited=document.querySelector(".chat-question").textContent.includes("State: Nevada");document.querySelector(".chat-reset").click();const reset=document.querySelector(".chat-question").textContent;document.querySelector(".chat-close").click();const m=await import("./assets/hubspot.js");const payload=m.hubspotPayload({state:"Nevada",name:"Example Owner",business:"Example Company",issue:"Monthly records",email:"owner@example.com",phone:"8185550123",meetingTime:"Morning",timeZone:"Pacific"},"Test","http://127.0.0.1:8765/");return {sequence,review,edited,reset,payloadMessage:payload.fields.find(f=>f.name==="message").value,submitted:false}})()';awaitPromise=$true;returnByValue=$true}
 $r.result.value|ConvertTo-Json -Depth 10|Set-Content (Join-Path $out 'complete-chat-flow.json') -Encoding UTF8
 $choiceTests=@()
 foreach($route in @('areas-we-serve.html','can-several-months-be-corrected-at-once.html','how-long-does-it-take-to-bring-overdue-books-current.html','past-due-bookkeeping-questions.html','past-due-bookkeeping.html','what-should-i-do-if-my-bookkeeping-is-several-months-behind.html','why-does-my-bank-balance-not-match-my-books.html')) {
 Load $route
 $r=Cdp 'Runtime.evaluate' @{expression='(()=>{document.querySelector("[data-open-chat]").click();const i=document.querySelector(".chat input");i.value="California";document.querySelector(".send-message").click();const issueOptions=[...document.querySelectorAll(".chat-options button")].map(b=>b.textContent);document.querySelector(".chat-options button").click();const periodOptions=[...document.querySelectorAll(".chat-options button")].map(b=>b.textContent);return {question:document.querySelector(".chat-question").textContent,issueOptions,periodOptions,activeQuestions:document.querySelectorAll(".chat-question").length}})()';returnByValue=$true}
 $choiceTests+=@{page=$route;result=$r.result.value}
 if($route -eq 'areas-we-serve.html'){Shot 'chat-desktop'}
 }
 $choiceTests|ConvertTo-Json -Depth 10|Set-Content (Join-Path $out 'question-choice-checks.json') -Encoding UTF8
 Cdp 'Browser.close'|Out-Null
}finally{if($socket){$socket.Dispose()}}
