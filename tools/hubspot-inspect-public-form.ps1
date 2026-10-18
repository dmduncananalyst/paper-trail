param([int]$Port=9261)
$ErrorActionPreference='Stop'
$folder=Join-Path $env:TEMP 'paper-trail-audit5-20261016'
$browserProfile=Join-Path $env:TEMP ('paper-trail-preview-'+$Port)
if (!(Test-NetConnection 127.0.0.1 -Port $Port -InformationLevel Quiet -WarningAction SilentlyContinue)) { $browser=Start-Process -FilePath 'C:/Program Files/Google/Chrome/Application/chrome.exe' -ArgumentList @('--headless=new','--disable-gpu','--no-first-run','--no-default-browser-check',"--remote-debugging-port=$Port",('--user-data-dir="'+$browserProfile+'"'),'about:blank') -WindowStyle Hidden -PassThru }
try {
 $target=$null
 for($i=0;$i -lt 40;$i++){try{$targets=Invoke-RestMethod "http://127.0.0.1:$Port/json" -TimeoutSec 2;$target=$targets|Where-Object type -EQ 'page'|Select-Object -First 1;if($target){break}}catch{};Start-Sleep -Milliseconds 250}
 if(!$target){throw 'Local browser debugging endpoint unavailable'}
 $socket=[Net.WebSockets.ClientWebSocket]::new();$socket.ConnectAsync([uri]$target.webSocketDebuggerUrl,[Threading.CancellationToken]::None).GetAwaiter().GetResult()
 $script:responses=@();$script:requestId=0;$script:requests=@();$script:exceptions=@()
 function Cdp($method,$params=@{},$TargetSession=$null) {
  $script:requestId++;$id=$script:requestId
  $message=@{id=$id;method=$method;params=$params};if($TargetSession){$message.sessionId=$TargetSession};$msg=$message|ConvertTo-Json -Depth 15 -Compress
  $bytes=[Text.Encoding]::UTF8.GetBytes($msg)
  $socket.SendAsync([ArraySegment[byte]]::new($bytes),[Net.WebSockets.WebSocketMessageType]::Text,$true,[Threading.CancellationToken]::None).GetAwaiter().GetResult()
  while($true){$stream=[IO.MemoryStream]::new();do{$buffer=New-Object byte[] 65536;$read=$socket.ReceiveAsync([ArraySegment[byte]]::new($buffer),[Threading.CancellationToken]::None).GetAwaiter().GetResult();$stream.Write($buffer,0,$read.Count)}while(!$read.EndOfMessage);$reply=[Text.Encoding]::UTF8.GetString($stream.ToArray())|ConvertFrom-Json;$stream.Dispose();if($reply.method -eq 'Network.requestWillBeSent'){$script:requests+=$reply.params.request.url};if($reply.method -eq 'Network.responseReceived'){$script:responses+=@{id=$reply.params.requestId;url=$reply.params.response.url;status=$reply.params.response.status;type=$reply.params.response.mimeType}};if($reply.method -eq 'Runtime.exceptionThrown'){$script:exceptions+=$reply.params.exceptionDetails};if($reply.id -eq $id){if($reply.error){throw ($reply.error|ConvertTo-Json -Compress)};return $reply.result}}
 }
 Cdp 'Page.enable'|Out-Null
 Cdp 'Network.enable'|Out-Null
 Cdp 'Runtime.enable'|Out-Null
 Cdp 'Network.setBlockedURLs' @{urls=@('*cloudtranslation*','*translation.googleapis.com/*','*translate.googleapis.com/*','*submissions/v3/*','*submissions/v1/*','*/api/chat','*/api/inquiry')}|Out-Null
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



 Cdp 'Page.navigate' @{url='http://127.0.0.1:8765/.release/hubspot-audit.html'}|Out-Null
 Start-Sleep -Seconds 12
 Cdp 'Runtime.evaluate' @{expression='document.readyState';returnByValue=$true}|Out-Null

 $targets=Cdp 'Target.getTargets'
 $frame=$targets.targetInfos|Where-Object {$_.type -eq 'iframe' -and $_.url -like '*ui-forms-embed-components-app*'}|Select-Object -First 1
 if($frame){
 $attached=Cdp 'Target.attachToTarget' @{targetId=$frame.targetId;flatten=$true};$targetSession=$attached.sessionId
 Cdp 'Runtime.enable' @{} $targetSession|Out-Null
 $r=Cdp 'Runtime.evaluate' @{expression='({url:location.href,text:document.body.innerText,forms:[...document.forms].map(f=>({action:f.action,fields:[...f.elements].map(e=>({name:e.name,type:e.type,required:e.required,label:e.labels?.[0]?.textContent,value:e.value}))}))})';returnByValue=$true} $targetSession
 $r|ConvertTo-Json -Depth 15|Set-Content '.release/hubspot-form-dom.json' -Encoding UTF8
 }else{$targets|ConvertTo-Json -Depth 8|Set-Content '.release/hubspot-form-targets.json' -Encoding UTF8}
 @{responses=$script:responses;exceptions=$script:exceptions}|ConvertTo-Json -Depth 12|Set-Content '.release/hubspot-audit-network.json' -Encoding UTF8
 Cdp 'Browser.close'|Out-Null
}finally{if($socket){$socket.Dispose()}}
