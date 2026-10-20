param([int]$Port=9235,[int]$SitePort=8768)
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
 function Load($route){Eval 'try{localStorage.clear();sessionStorage.clear()}catch{};true'|Out-Null;Cdp 'Page.navigate' @{url=('http://127.0.0.1:'+$SitePort+'/'+$route)}|Out-Null; $expression='(async()=>{for(let i=0;i<150;i++){if(location.pathname==="/"+'+($route|ConvertTo-Json -Compress)+'&&document.readyState==="complete"&&window.paperTrailUI){await document.fonts.ready;return true}await new Promise(r=>setTimeout(r,40))}throw Error("Page did not initialize")})()';Eval $expression|Out-Null}
 Cdp 'Emulation.setDeviceMetricsOverride' @{width=390;height=1000;deviceScaleFactor=1;mobile=$true}|Out-Null
 $results=@()
 foreach($language in @('en','es','fa','hy','zh-CN','ko','tl','te','ru','ar')){
  $prefix=if($language -eq 'en'){''}else{$language+'/'}
  Load ($prefix+'index.html')
  Eval 'document.querySelector("[data-open-chat]").click();true'|Out-Null
  $results+=Eval ([IO.File]::ReadAllText((Join-Path $PSScriptRoot 'auto-send-chat-eval.js')))
  # Reopening a completed conversation must not send again.
  Cdp 'Page.reload'|Out-Null
  Start-Sleep -Milliseconds 250
  $restored=Eval '(async()=>{for(let i=0;i<100;i++){if(document.readyState==="complete"&&window.paperTrailUI){document.querySelector("[data-open-chat]").click();return document.querySelector(".chat input").disabled&&!document.querySelector(".chat-options").children.length}await new Promise(r=>setTimeout(r,25))}return false})()'
  if(!$restored){throw ('Completed conversation was not restored: '+$language)}
 }
 if($script:exceptions.Count){throw ($script:exceptions|ConvertTo-Json -Depth 5)}
 if(@($script:requests|Where-Object {$_ -match 'api.hsforms.com'}).Count){throw 'Real delivery request detected'}
 $results|ConvertTo-Json -Depth 5
 Cdp 'Browser.close'|Out-Null
}finally{if($socket){$socket.Dispose()}}