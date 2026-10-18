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
 Cdp 'Emulation.setFocusEmulationEnabled' @{enabled=$true}|Out-Null
 $checks=[ordered]@{}
 Cdp 'Emulation.setDeviceMetricsOverride' @{width=1440;height=1100;deviceScaleFactor=1;mobile=$false}|Out-Null
 Cdp 'Page.navigate' @{url='http://127.0.0.1:8765/verification/phase-a/home.html'}|Out-Null
 Start-Sleep -Milliseconds 1200
 $checks.home=(Cdp 'Runtime.evaluate' @{expression='(async()=>{for(let i=0;i<20&&!window.paperTrailPreview;i++)await new Promise(r=>setTimeout(r,200));if(!window.paperTrailPreview)return {error:"Preview script did not load",locale:!!window.PAPER_TRAIL_LOCALES};const select=document.querySelector("#language"),locales=[];for(const code of Object.keys(window.PAPER_TRAIL_LOCALES)){select.value=code;select.dispatchEvent(new Event("change"));locales.push({code,lang:document.documentElement.lang,dir:document.documentElement.dir,gaps:window.paperTrailPreview.localeGaps(),notice:!document.querySelector(".translation-notice").hidden,width:innerWidth,scrollWidth:document.documentElement.scrollWidth,heading:document.querySelector("h1").innerText})}select.value="en";select.dispatchEvent(new Event("change"));const family=document.querySelector(".nav-family"),a=family.querySelector("a");a.focus();const keyboardOpens=getComputedStyle(document.getElementById(a.getAttribute("aria-controls"))).display!=="none";document.dispatchEvent(new KeyboardEvent("keydown",{key:"Escape",bubbles:true}));const escapeCloses=getComputedStyle(document.getElementById(a.getAttribute("aria-controls"))).display==="none";document.querySelector("[data-email]").click();const emailOpens=document.querySelector(".email-dialog").open;document.querySelector(".email-close").click();document.querySelector("[data-open-chat]").click();const chatOpens=document.querySelector("#conversation-dialog").open;document.querySelector(".chat-close").click();const v=document.querySelector("video"),button=document.querySelector(".video-toggle");await v.play();const time=v.currentTime;await new Promise(r=>setTimeout(r,200));const playing=!v.paused&&v.currentTime>time;button.click();const paused=v.paused;button.click();const icons=[...document.querySelectorAll("[data-icon-id]")].map(e=>e.dataset.iconId);return {locales,languageChoices:select.options.length,keyboardOpens,escapeCloses,emailOpens,chatOpens,playing,paused,resumes:!v.paused,source:v.currentSrc,uniqueIcons:icons.length===new Set(icons).size,nav:[...document.querySelectorAll(".pt-nav>a,.nav-family>a")].map(x=>x.textContent),footerLogo:!!document.querySelector(".pt-footer img"),providerCalls:window.paperTrailPreview.providerCalls}})()';awaitPromise=$true;returnByValue=$true}).result.value
 $checks.locales=(Cdp 'Runtime.evaluate' @{expression='window.PAPER_TRAIL_LOCALES';returnByValue=$true}).result.value
 Cdp 'Emulation.setDeviceMetricsOverride' @{width=390;height=1100;deviceScaleFactor=1;mobile=$true}|Out-Null
 Cdp 'Page.navigate' @{url='http://127.0.0.1:8765/verification/phase-a/notes.html'}|Out-Null
 Start-Sleep -Milliseconds 900
 $checks.notes=(Cdp 'Runtime.evaluate' @{expression='(async()=>{for(let i=0;i<20&&!window.paperTrailPreview;i++)await new Promise(r=>setTimeout(r,200));const select=document.querySelector("#language"),states=[];for(const code of Object.keys(window.PAPER_TRAIL_LOCALES)){select.value=code;select.dispatchEvent(new Event("change"));states.push({code,dir:document.documentElement.dir,scrollWidth:document.documentElement.scrollWidth,width:innerWidth,gaps:window.paperTrailPreview.localeGaps(),h1:document.querySelector("h1").textContent})}select.value="ar";select.dispatchEvent(new Event("change"));return {states,topics:document.querySelectorAll(".topic-row").length,noBreadcrumbs:!document.querySelector(".pt-reading-nav,[aria-label=Breadcrumb]"),noIntro:!document.querySelector(".pt-notes-opening"),saved:localStorage.getItem("paper-trail-preview-language")}})()';awaitPromise=$true;returnByValue=$true}).result.value
 $shot=Cdp 'Page.captureScreenshot' @{format='png';captureBeyondViewport=$false}
 [IO.File]::WriteAllBytes((Join-Path $folder 'notes-arabic-mobile.png'),[Convert]::FromBase64String($shot.data))
 Cdp 'Page.navigate' @{url='http://127.0.0.1:8765/verification/phase-a/home.html'}|Out-Null
 Start-Sleep -Milliseconds 800
 $checks.retention=(Cdp 'Runtime.evaluate' @{expression='({lang:document.documentElement.lang,selected:document.querySelector("#language").value,width:innerWidth,scrollWidth:document.documentElement.scrollWidth})';returnByValue=$true}).result.value
 $shot=Cdp 'Page.captureScreenshot' @{format='png';captureBeyondViewport=$false}
 [IO.File]::WriteAllBytes((Join-Path $folder 'home-arabic-mobile.png'),[Convert]::FromBase64String($shot.data))
 Cdp 'Runtime.evaluate' @{expression='localStorage.setItem("paper-trail-preview-language","en")'}|Out-Null
 Cdp 'Page.navigate' @{url='http://127.0.0.1:8765/verification/phase-a/blog.html'}|Out-Null
 Start-Sleep -Milliseconds 700
 $checks.blog=(Cdp 'Runtime.evaluate' @{expression='({stories:document.querySelectorAll(".blog-story").length,hiddenStories:document.querySelectorAll(".blog-story[hidden]").length,tabs:document.querySelectorAll("[role=tab]").length,englishOnly:document.querySelector("#language").disabled})';returnByValue=$true}).result.value
 foreach($locale in $checks.locales.PSObject.Properties){$locale.Value|ConvertTo-Json -Depth 6|Set-Content -LiteralPath (Join-Path $folder ('locales/'+$locale.Name+'.draft.json')) -Encoding UTF8}
 $checks.Remove('locales')
 $checks|ConvertTo-Json -Depth 12|Set-Content -LiteralPath (Join-Path $folder 'direction-4-validation.json') -Encoding UTF8
 $checks|ConvertTo-Json -Depth 12
 Cdp 'Browser.close'|Out-Null
}finally{if($socket){$socket.Dispose()}}