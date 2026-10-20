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
 Cdp 'Network.setBlockedURLs' @{urls=@('https://api.hsforms.com/*')}|Out-Null
 $out=Join-Path (Get-Location) 'verification/launch-audit-20261020';New-Item -ItemType Directory -Force $out|Out-Null
 function Eval($expression){$r=Cdp 'Runtime.evaluate' @{expression=$expression;awaitPromise=$true;returnByValue=$true};if($r.exceptionDetails){throw ($r.exceptionDetails|ConvertTo-Json -Depth 6)};return $r.result.value}
 function Load($route){Eval 'try{localStorage.clear();sessionStorage.clear()}catch{};true'|Out-Null;Cdp 'Page.navigate' @{url=('http://127.0.0.1:8765/'+$route)}|Out-Null; $expression='(async()=>{for(let i=0;i<150;i++){if(location.pathname==="/"+'+($route|ConvertTo-Json -Compress)+'&&document.readyState==="complete"&&window.paperTrailUI){await document.fonts.ready;return true}await new Promise(r=>setTimeout(r,40))}throw Error("Page did not initialize")})()';Eval $expression|Out-Null}
 $layout=@();$chat=@()
 foreach($width in @(390,1440)){
 Cdp 'Emulation.setDeviceMetricsOverride' @{width=$width;height=1000;deviceScaleFactor=1;mobile=($width -lt 600)}|Out-Null
 foreach($route in @('index.html','services.html','paper-trail-services.html','faq.html','monthly-bookkeeping-review.html','tax-ready-bookkeeping.html','paper-trail-monthly-bookkeeping.html','nationwide-bookkeeping.html','los-angeles-county.html','areas-we-serve.html','tax-ready-bookkeeping-records.html','profit-vs-cash-flow-business-money.html','catch-up-bookkeeping-overdue-books.html','state-records/california.html')){
 Load $route
 $state=Eval '(()=>({overflow:document.documentElement.scrollWidth>innerWidth+2,brokenImages:[...document.images].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.src),menu:!!document.querySelector(".menu-toggle"),chat:!!document.querySelector("[data-open-chat]")}))()'
 $layout+=@{route=$route;width=$width;state=$state}
 if($state.overflow -or $state.brokenImages.Count){throw ('Layout/image failure: '+$route+' '+$width)}
 if($route -in @('index.html','nationwide-bookkeeping.html','tax-ready-bookkeeping-records.html')){$shot=Cdp 'Page.captureScreenshot' @{format='png'};[IO.File]::WriteAllBytes((Join-Path $out ($route+'-'+$width+'.png')),[Convert]::FromBase64String($shot.data))}
 }
 }
 Cdp 'Emulation.setDeviceMetricsOverride' @{width=390;height=1000;deviceScaleFactor=1;mobile=$true}|Out-Null
 foreach($lang in @('en','es','fa','hy','zh-CN','ko','tl','te','ru','ar')){
 $prefix=if($lang -eq 'en'){''}else{$lang+'/'}
 Load ($prefix+'index.html')
 Eval 'sessionStorage.clear();document.querySelector("[data-open-chat]").click();document.querySelector(".chat-reset").click();true'|Out-Null
 $greeting=Eval '({text:document.querySelector(".chat-question").textContent,lang:document.documentElement.lang,dir:document.querySelector(".chat").dir})'
 $flow=Eval ([IO.File]::ReadAllText((Join-Path $PSScriptRoot 'localized-chat-eval.js')))
 if(!$flow.questionsMatch -or !$flow.errorsMatch -or !$flow.reviewTranslated -or $flow.overflow){throw ('Intake failure: '+$lang+' '+($flow|ConvertTo-Json -Compress -Depth 4))}
 $delivery=Eval ([IO.File]::ReadAllText((Join-Path $PSScriptRoot 'localized-chat-confirmation-eval.js')))
 if(!$delivery.edited -or !$delivery.confirmationTranslated -or $delivery.externalDeliveryPerformed){throw ('Mock delivery failure: '+$lang)}
 Eval 'document.querySelector(".chat-reset").click();document.querySelector(".chat-mode").click();document.querySelector(".chat input").value="unmatched question";document.querySelector(".send-message").click();true'|Out-Null
 $answer=Eval '({choices:document.querySelector(".chat-options").children.length,status:document.querySelector(".chat-status").textContent})'
 if(!$answer.choices -or $answer.status){throw ('Typed question failure: '+$lang)}
 $published=Eval '(()=>{const before=document.querySelectorAll(".chat-log .bubble").length;document.querySelector(".chat-options button").click();return document.querySelectorAll(".chat-log .bubble").length>before&&!!document.querySelector(".chat-log a")})()'
 if(!$published){throw ('Published answer failure: '+$lang)}
 $chat+=@{language=$lang;greeting=$greeting;flow=$flow;mockDelivery=$delivery;typed=$answer}
 foreach($page in @('tax-ready-bookkeeping-records.html','profit-vs-cash-flow-business-money.html','nationwide-bookkeeping.html','los-angeles-county.html','catch-up-bookkeeping-overdue-books.html')){
 Load ($prefix+$page)
 $opened=Eval '(()=>{document.querySelector("[data-open-chat]").click();return document.querySelector("#conversation-dialog").open&&!!document.querySelector(".chat-question")})()'
 if(!$opened){throw ('Missing restored chat: '+$prefix+$page)}
 }
 }
 $badRequests=@($script:requests|Where-Object {$_ -match '/api/(chat|inquiry)'})
 $result=@{layout=$layout;chat=$chat;exceptions=$script:exceptions;badRequests=$badRequests}
 $result|ConvertTo-Json -Depth 30|Set-Content (Join-Path $out 'browser.json') -Encoding UTF8
 if($script:exceptions.Count -or $badRequests.Count){throw 'Runtime errors or nonexistent API requests detected'}
 'Browser verification passed: 28 layouts, 10 localized intake flows, 50 restored chat dialogs.'
 Cdp 'Browser.close'|Out-Null
}finally{if($socket){$socket.Dispose()}}