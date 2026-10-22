$ErrorActionPreference='Stop'
$out=Join-Path (Get-Location) 'verification/approved-blogs-20261021'
$targets=Invoke-RestMethod 'http://127.0.0.1:9264/json'
$target=$targets | Where-Object type -EQ 'page' | Select-Object -First 1
$socket=[Net.WebSockets.ClientWebSocket]::new()
$socket.ConnectAsync([uri]$target.webSocketDebuggerUrl,[Threading.CancellationToken]::None).GetAwaiter().GetResult()
$script:requestId=0
function Cdp($method,$params=@{}) {
 $script:requestId++;$id=$script:requestId
 $bytes=[Text.Encoding]::UTF8.GetBytes((@{id=$id;method=$method;params=$params}|ConvertTo-Json -Depth 20 -Compress))
 $socket.SendAsync([ArraySegment[byte]]::new($bytes),[Net.WebSockets.WebSocketMessageType]::Text,$true,[Threading.CancellationToken]::None).GetAwaiter().GetResult()
 while($true){$stream=[IO.MemoryStream]::new();do{$buffer=New-Object byte[] 65536;$read=$socket.ReceiveAsync([ArraySegment[byte]]::new($buffer),[Threading.CancellationToken]::None).GetAwaiter().GetResult();$stream.Write($buffer,0,$read.Count)}while(!$read.EndOfMessage);$reply=[Text.Encoding]::UTF8.GetString($stream.ToArray())|ConvertFrom-Json;$stream.Dispose();if($reply.id -eq $id){if($reply.error){throw ($reply.error|ConvertTo-Json -Compress)};return $reply.result}}
}
function Eval($expression){$r=Cdp 'Runtime.evaluate' @{expression=$expression;awaitPromise=$true;returnByValue=$true};if($r.exceptionDetails){throw ($r.exceptionDetails|ConvertTo-Json -Depth 8)};return $r.result.value}
Cdp 'Page.enable'|Out-Null
Cdp 'Network.enable'|Out-Null
Cdp 'Network.setBlockedURLs' @{urls=@('https://*','http://api.*')}|Out-Null
$manifest=Get-Content (Join-Path $out 'approved-content.json') -Raw -Encoding UTF8|ConvertFrom-Json
$routes=@('blog.html')+@($manifest|ForEach-Object slug)
$results=@()
foreach($width in @(320,390,834,909,1440)){
 Cdp 'Emulation.setDeviceMetricsOverride' @{width=$width;height=1000;deviceScaleFactor=1;mobile=($width -le 390)}|Out-Null
 foreach($route in $routes){
  Cdp 'Page.navigate' @{url=('file:///C:/Users/Owner/OneDrive/Documents/GitHub/paper-trail/'+$route)}|Out-Null
  $ready='(async()=>{for(let i=0;i<150;i++){if(location.pathname.endsWith('+($route|ConvertTo-Json -Compress)+')&&document.readyState==="complete"&&window.paperTrailUI){await document.fonts.ready;await Promise.all([...document.images].map(x=>x.decode().catch(()=>{})));await new Promise(r=>setTimeout(r,100));return true}await new Promise(r=>setTimeout(r,50))}throw Error("Page not ready")})()'
  Eval $ready|Out-Null
  $state=Eval '(()=>{const images=[...document.querySelectorAll(".approved-blog img,.approved-blog-card>img")].map(i=>{const b=i.getBoundingClientRect(),s=getComputedStyle(i);return {src:decodeURI(new URL(i.src).pathname),naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight,width:b.width,height:b.height,fit:s.objectFit,ratioError:Math.abs(b.width/b.height-i.naturalWidth/i.naturalHeight)}});return {title:document.title,h1:document.querySelector("h1")?.textContent,overflow:document.documentElement.scrollWidth>innerWidth+1,images,archiveLinks:[...document.querySelectorAll(".approved-blog-card a")].map(a=>a.getAttribute("href")),references:[...document.querySelectorAll(".reference-list a")].map(a=>({text:a.textContent,href:a.href})),intro:[...document.querySelectorAll(".approved-blog .reading-spread > p")].map(p=>p.textContent),sections:[...document.querySelectorAll(".approved-blog .story-section")].map(s=>({heading:s.querySelector("h2").textContent,paragraphs:[...s.querySelectorAll("p")].map(p=>p.textContent)})),navBlog:!!document.querySelector(".pt-nav a[href=\"blog.html\"]"),chatReady:!!document.querySelector("dialog.chat"),emailReady:!!document.querySelector("dialog.email-dialog")}})()'
  if($state.overflow){throw "Overflow: $route $width"}
  foreach($im in $state.images){if(!$im.naturalWidth -or $im.ratioError -gt .015){throw "Image failed: $route $width $($im|ConvertTo-Json -Compress)"}}
  if($route -ne 'blog.html' -and $width -ge 651 -and $width -le 980 -and $state.images[0].width -lt $width*.40){throw "Article photo too small: $route $width"}
  if($route -ne 'blog.html'){
   $approved=$manifest|Where-Object slug -EQ $route
   $actual=@($state.intro);foreach($s in $state.sections){$actual+=$s.heading;$actual+=@($s.paragraphs)}
   $expected=@($approved.article|ForEach-Object text)
   if(($actual -join "`n") -cne ($expected -join "`n")){throw "Article text mismatch: $route"}
   if($state.references.Count -ne $approved.references.Count){throw "Missing references: $route"}
   if(!$state.images[0].src.EndsWith('/assets/photos/'+$approved.photo)){throw "Photo mismatch: $route"}
  }elseif($state.archiveLinks.Count -ne 5){throw 'Missing blog card links'}
  $results+=@{route=$route;width=$width;state=$state}
  if($width -eq 390 -or $width -eq 909 -or $width -eq 1440){$shot=Cdp 'Page.captureScreenshot' @{format='png';captureBeyondViewport=$true};[IO.File]::WriteAllBytes((Join-Path $out ($route.Replace('.html','')+'-'+$width+'.png')),[Convert]::FromBase64String($shot.data))}
 }
}
# Exercise existing dialogs without submitting a message or contacting an integration.
Cdp 'Page.navigate' @{url='file:///C:/Users/Owner/OneDrive/Documents/GitHub/paper-trail/blog.html'}|Out-Null
Eval '(async()=>{for(let i=0;i<100;i++){if(location.pathname.endsWith("blog.html")&&document.readyState==="complete"&&window.paperTrailUI)return true;await new Promise(r=>setTimeout(r,50))}throw Error("Archive not ready")})()'|Out-Null
$dialogs=Eval '(()=>{const e=document.querySelector("[data-email]");e.click();const email=document.querySelector(".email-dialog").open;document.querySelector(".email-close").click();const b=document.querySelector(".chat-launcher,[data-open-chat]");b?.click();return {emailOpened:email,emailClosed:!document.querySelector(".email-dialog").open,chatOpened:!!document.querySelector("#conversation-dialog[open],dialog.chat[open]")}})()'
if(!$dialogs.emailOpened -or !$dialogs.emailClosed -or !$dialogs.chatOpened){throw 'Dialog regression check failed'}
[IO.File]::WriteAllText((Join-Path $out 'browser-checks.json'),(@{checks=$results;dialogs=$dialogs}|ConvertTo-Json -Depth 30),[Text.UTF8Encoding]::new($false))
$socket.Dispose()
Write-Output (@{pageViewportChecks=$results.Count;dialogs=$dialogs;status='passed'}|ConvertTo-Json -Depth 8)


