param([int]$Port=0,[int]$SitePort=8794,[switch]$InteractionsOnly,[string]$Output=(Join-Path $env:TEMP ('paper-trail-package-corrections-browser-'+[guid]::NewGuid().ToString('N'))))
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot
$out=[IO.Path]::GetFullPath($Output)
if($out.StartsWith($root+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Browser output must stay outside the repository'}
New-Item -ItemType Directory -Path $out -Force | Out-Null
Write-Output ('Temporary browser results: '+$out)
$profile=Join-Path $out 'disposable-profile'
if(!$Port){$probe=[Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback,0);$probe.Start();$Port=$probe.LocalEndpoint.Port;$probe.Stop()}
$browser=Start-Process -FilePath 'C:/Program Files/Google/Chrome/Application/chrome.exe' -ArgumentList @('--headless=new','--disable-gpu','--no-first-run','--no-default-browser-check',"--remote-debugging-port=$Port",('--user-data-dir="'+$profile+'"'),'about:blank') -WindowStyle Hidden -PassThru
$results=[Collections.Generic.List[object]]::new()
try{
 $target=$null
 for($i=0;$i -lt 60;$i++){try{$targets=Invoke-RestMethod "http://127.0.0.1:$Port/json" -TimeoutSec 2;$target=$targets | Where-Object type -EQ 'page' | Select-Object -First 1;if($target){break}}catch{};Start-Sleep -Milliseconds 250}
 if(!$target){throw 'Disposable headless browser unavailable'}
 $socket=[Net.WebSockets.ClientWebSocket]::new()
 $socket.ConnectAsync([uri]$target.webSocketDebuggerUrl,[Threading.CancellationToken]::None).GetAwaiter().GetResult()
 $script:requestId=0;$script:exceptions=@();$script:requests=@()
 function Cdp($method,$params=@{}){
  $script:requestId++;$id=$script:requestId
  $bytes=[Text.Encoding]::UTF8.GetBytes((@{id=$id;method=$method;params=$params}|ConvertTo-Json -Depth 20 -Compress))
  $socket.SendAsync([ArraySegment[byte]]::new($bytes),[Net.WebSockets.WebSocketMessageType]::Text,$true,[Threading.CancellationToken]::None).GetAwaiter().GetResult()
  while($true){
   $stream=[IO.MemoryStream]::new()
   do{$buffer=New-Object byte[] 65536;$read=$socket.ReceiveAsync([ArraySegment[byte]]::new($buffer),[Threading.CancellationToken]::None).GetAwaiter().GetResult();$stream.Write($buffer,0,$read.Count)}while(!$read.EndOfMessage)
   $reply=[Text.Encoding]::UTF8.GetString($stream.ToArray())|ConvertFrom-Json;$stream.Dispose()
   if($reply.method -eq 'Runtime.exceptionThrown'){$script:exceptions+=$reply.params.exceptionDetails.text}
   if($reply.method -eq 'Network.requestWillBeSent'){$script:requests+=@{url=$reply.params.request.url;method=$reply.params.request.method}}
   if($reply.id -eq $id){if($reply.error){throw ($reply.error|ConvertTo-Json -Compress)};return $reply.result}
  }
 }
 function Eval($expression){$r=Cdp 'Runtime.evaluate' @{expression=$expression;awaitPromise=$true;returnByValue=$true};if($r.exceptionDetails){throw ($r.exceptionDetails|ConvertTo-Json -Depth 6)};return $r.result.value}
 function Assert($condition,$message){if(!$condition){throw $message}}
 function Wait($condition){for($attempt=0;$attempt -lt 120;$attempt++){try{if(Eval $condition){return}}catch{};Start-Sleep -Milliseconds 100};throw ('Browser condition timed out: '+$condition)}
 function Load($route){
  Cdp 'Page.navigate' @{url="http://127.0.0.1:$SitePort/$route"}|Out-Null
  $expected=('/'+$route.Split('#')[0])|ConvertTo-Json -Compress
  Wait ('location.pathname+location.search==='+$expected+'&&document.readyState==="complete"&&!!document.querySelector(".pt-nav[data-organized-navigation]")')
  Eval '(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>{i.loading="eager";return i.decode().catch(()=>{})}));return true})()'|Out-Null
 }
 Cdp 'Page.enable'|Out-Null;Cdp 'Runtime.enable'|Out-Null;Cdp 'Network.enable'|Out-Null
 Cdp 'Network.setBlockedURLs' @{urls=@('https://*')}|Out-Null
 $languages=@('','es/','fa/','hy/','zh-CN/','ko/','tl/','te/','ru/','ar/')
 $kinds=@('weekly-bookkeeping','monthly-bookkeeping','bookkeeping-repair','accounts-billing','financial-analysis','payroll')
 $pages=@('all-services.html','packages.html','payroll.html')+@($kinds|ForEach-Object {$_+'-packages.html'})
 function Point($selector){Eval ('(()=>{const r=document.querySelector('+($selector|ConvertTo-Json -Compress)+').getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()')}
 function Mouse($selector){$point=Point $selector;Cdp 'Input.dispatchMouseEvent' @{type='mouseMoved';x=$point.x;y=$point.y}|Out-Null}
 function Tap($selector){$point=Point $selector;Cdp 'Input.dispatchTouchEvent' @{type='touchStart';touchPoints=@(@{x=$point.x;y=$point.y})}|Out-Null;Cdp 'Input.dispatchTouchEvent' @{type='touchEnd';touchPoints=@()}|Out-Null}
 if(!$InteractionsOnly){foreach($width in @(1440,1024,834,390)){
  Cdp 'Emulation.setDeviceMetricsOverride' @{width=$width;height=844;deviceScaleFactor=1;mobile=($width -lt 600)}|Out-Null
  Cdp 'Emulation.setTouchEmulationEnabled' @{enabled=($width -le 834)}|Out-Null
  foreach($language in $languages){
   Write-Output ('Checking screenshot corrections: '+$width+' '+$(if($language){$language}else{'en'}))
   Eval '(()=>{try{localStorage.removeItem("paper-trail-language")}catch{}return true})()'|Out-Null
   Load ($language+'all-services.html')
   foreach($family in @('services','packages')){
    $selector='.pt-nav>.nav-family:nth-of-type('+$(if($family -eq 'services'){1}else{2})+')>a'
    if($width -ge 981){Mouse $selector}else{Tap $selector}
    $position=Eval ('(()=>{const a=document.querySelector('+($selector|ConvertTo-Json -Compress)+'),p=document.querySelector("#navigation-'+$family+'"),r=a.getBoundingClientRect(),s=p.getBoundingClientRect();return {open:!p.hidden,topError:Math.abs(s.top-r.bottom),centerError:Math.abs(s.left-Math.max(12,Math.min(innerWidth-s.width-12,r.left+r.width/2-s.width/2))),within:s.left>=11&&s.right<=innerWidth-11,nested:!!p.querySelector(".nav-panel"),links:p.querySelectorAll("a").length}})()')
    Assert ($position.open -and $position.topError -le 1 -and $position.centerError -le 1 -and $position.within -and !$position.nested -and $position.links -eq 7) ('Dropdown alignment failed: '+$family+' '+($position|ConvertTo-Json -Compress))
    if($width -ge 981){Mouse ('#navigation-'+$family+'>a:nth-child(2)');Assert (Eval ('!document.querySelector("#navigation-'+$family+'").hidden')) 'Hover bridge failed'}
    Cdp 'Input.dispatchKeyEvent' @{type='keyDown';key='Escape';code='Escape';windowsVirtualKeyCode=27}|Out-Null
    Assert (Eval ('document.querySelector("#navigation-'+$family+'").hidden')) 'Escape did not close dropdown'
   }
   foreach($name in $pages){
    Load ($language+$name)
    $layout=Eval '(()=>{const n=document.querySelector(".pt-nav"),items=[...n.children];return {overflow:document.documentElement.scrollWidth>innerWidth+2,brokenImages:[...document.images].filter(i=>!i.naturalWidth).length,h1:document.querySelectorAll("main h1").length,navItems:items.length,rows:new Set(items.map(i=>Math.round(i.getBoundingClientRect().top))).size,font:parseFloat(getComputedStyle(n).fontSize),arrows:[...n.querySelectorAll("a")].some(a=>["before","after"].some(p=>!["none","normal","\"\""].includes(getComputedStyle(a,"::"+p).content)))}})()'
    Assert (!$layout.overflow -and !$layout.brokenImages -and $layout.h1 -eq 1 -and $layout.navItems -eq 8 -and !$layout.arrows) ('Page layout failure: '+$language+$name+' '+$width+' '+($layout|ConvertTo-Json -Compress))
    if($width -ge 981){Assert ($layout.rows -eq 1 -and $layout.font -ge 16) ('Desktop navigation size or row failed: '+$language+$name+' '+($layout|ConvertTo-Json -Compress))}
    if($name -eq 'all-services.html'){
     $cards=Eval '(()=>{const c=[...document.querySelectorAll(".service-overview-card")];return {count:c.length,bordered:c.every(e=>["Top","Right","Bottom","Left"].every(side=>parseFloat(getComputedStyle(e)["border"+side+"Width"])>=1)),buttons:c.every(e=>{const a=e.querySelector(".action"),r=e.getBoundingClientRect(),b=a.getBoundingClientRect();return b.height>0&&Math.abs(r.bottom-b.bottom-parseFloat(getComputedStyle(e).paddingBottom)-1)<2}),stretched:c.every(e=>getComputedStyle(e.querySelector(".action"),"::after").position==="absolute")}})()'
     Assert ($cards.count -eq 6 -and $cards.bordered -and $cards.buttons -and $cards.stretched) ('Service cards failed: '+($cards|ConvertTo-Json -Compress))
    }
    if($name -like '*-packages.html'){
     $design=Eval '(()=>{const group=document.querySelector("main>.pricing-category>.package-plans,main>.pricing-category>.repair-package-grid"),cards=[...group.children],last=cards.at(-1),a=last.getBoundingClientRect(),r=group.getBoundingClientRect();return {display:getComputedStyle(group).display,justify:getComputedStyle(group).justifyContent,count:cards.length,centerError:Math.abs((a.left+a.right-r.left-r.right)/2),borders:cards.every(e=>parseFloat(getComputedStyle(e).borderTopWidth)===1),inline:[...document.querySelectorAll("main .plan-price>span")].every(e=>getComputedStyle(e).display==="inline")}})()'
     Assert ($design.display -eq 'flex' -and $design.justify -eq 'center' -and $design.count -eq 4 -and $design.borders -and $design.inline) ('Package reference design failed: '+$language+$name+' '+($design|ConvertTo-Json -Compress))
     if($width -ge 651){Assert ($design.centerError -le 2) 'Final package card is not centered'}
     if($name -eq 'weekly-bookkeeping-packages.html'){
      $rates=Eval '(()=>{const digit=s=>s.replace(/[\u06f0-\u06f9]/g,c=>String(c.charCodeAt(0)-1776)).replace(/[\u0660-\u0669]/g,c=>String(c.charCodeAt(0)-1632));return [...document.querySelectorAll("#weekly-bookkeeping>.package-plans .plan-price")].slice(0,3).map(e=>Number(digit(e.textContent).replace(/[^0-9]/g,"")))})()'
      Assert (($rates -join ',') -eq '700,1300,2100') 'Weekly monthly price amounts incorrect'
     }
     if($name -eq 'bookkeeping-repair-packages.html'){Assert (Eval '!!document.querySelector(".repair-package-heading>span")&&!document.querySelector("#bookkeeping-repair .plan-price")') 'Repair lost Custom Quote presentation'}
     $consultation=Eval '(()=>{const d=document.querySelector("main>.pricing-category details.package-consultation");if(!d)return true;d.querySelector("summary").click();const ok=d.open&&d.querySelectorAll("a").length===2;d.open=false;return ok})()'
     Assert $consultation 'Existing consultation controls failed'
    }
    if($name -eq 'payroll.html'){
     Assert (Eval '(()=>{const h=[...document.querySelectorAll(".work-card>h3")][5],label=document.documentElement.dataset.staticLocale==="tl"?"Pag-uulat ng Payroll":h.textContent;const p=[...document.querySelectorAll("p")].find(e=>e.textContent.startsWith(label)&&e.textContent.length>200);return !!p&&p.previousElementSibling?.tagName==="P"&&p.previousElementSibling.textContent.length>200})()') 'Payroll reporting paragraph break missing'
    }
    if($name -eq 'packages.html'){
     Assert (Eval '(async()=>{const source=await fetch(location.pathname.replace("packages.html","all-bundles.html")).then(r=>r.text()),d=new DOMParser().parseFromString(source,"text/html"),headings=[...document.querySelectorAll("#bundle-save .bundle-preview>h2")];return headings.length===2&&headings.every((h,i)=>h.textContent===d.querySelector("#bundle-"+(i+1)+">h2").textContent+" \u2014 "+d.querySelector("#bundle-"+(i+1)+">p").textContent)&&document.querySelectorAll("#bundle-save .category-preview-tier").length===6})()') 'Bundle inclusion headings or existing price tiers failed'
    }
    $results.Add(@{width=$width;route=$language+$name;layout=$layout})
    if($width -in @(1440,390) -and $language -in @('','ar/') -and $name -in @('all-services.html','weekly-bookkeeping-packages.html','accounts-billing-packages.html')){
     $shot=Cdp 'Page.captureScreenshot' @{format='png';captureBeyondViewport=$true}
     [IO.File]::WriteAllBytes((Join-Path $out (($language.Replace('/','')+$name.Replace('.html','')+'-'+$width)+'.png')),[Convert]::FromBase64String($shot.data))
    }
   }
   if($width -eq 1440){
    for($i=0;$i -lt 6;$i++){
     Load ($language+'all-services.html')
     $point=Eval ('(()=>{const c=document.querySelectorAll(".service-overview-card")['+$i+'];c.scrollIntoView({block:"center",behavior:"instant"});const r=c.getBoundingClientRect(),a=c.querySelector(".action");return {x:r.left+5,y:r.top+5,path:new URL(a.href).pathname}})()')
     Cdp 'Input.dispatchMouseEvent' @{type='mousePressed';button='left';clickCount=1;x=$point.x;y=$point.y}|Out-Null
     Cdp 'Input.dispatchMouseEvent' @{type='mouseReleased';button='left';clickCount=1;x=$point.x;y=$point.y}|Out-Null
     Wait ('location.pathname==="'+$point.path+'"&&document.readyState==="complete"')
     Load ($language+'all-services.html')
     Eval ('document.querySelectorAll(".service-overview-card>.action")['+$i+'].click()')|Out-Null
     Wait ('location.pathname==="'+$point.path+'"&&document.readyState==="complete"')
    }
   }
  }
 }
 }
 Cdp 'Emulation.setDeviceMetricsOverride' @{width=1440;height=844;deviceScaleFactor=1;mobile=$false}|Out-Null
 Cdp 'Emulation.setTouchEmulationEnabled' @{enabled=$false}|Out-Null
 $switches=0
 foreach($language in @('es','fa','hy','zh-CN','ko','tl','te','ru','ar')){
  Write-Output ('Checking language switching: '+$language)
  foreach($route in @('all-services.html','packages.html','monthly-bookkeeping-packages.html','payroll.html')){
   Eval '(()=>{try{localStorage.removeItem("paper-trail-language")}catch{}return true})()'|Out-Null
   Load $route
   Eval ('(()=>{const s=document.querySelector("#language");s.value="'+$language+'";s.dispatchEvent(new Event("change",{bubbles:true}));return true})()')|Out-Null
   Wait ('location.pathname==="/'+$language+'/'+$route+'"&&document.readyState==="complete"')
   $switches++
   Eval '(()=>{const s=document.querySelector("#language");s.value="en";s.dispatchEvent(new Event("change",{bubbles:true}));return true})()'|Out-Null
   Wait ('location.pathname==="/'+$route+'"&&document.readyState==="complete"')
   $switches++
  }
 }
 Assert ($script:exceptions.Count -eq 0) ('JavaScript exceptions: '+($script:exceptions -join ', '))
 Assert (@($script:requests|Where-Object {$_.method -notin @('GET','HEAD','OPTIONS')}).Count -eq 0) 'Unexpected write request'
 @{page_viewport_checks=$results.Count;whole_card_and_button_navigations=$(if($InteractionsOnly){0}else{120});aligned_hover_and_touch_dropdown_checks=$(if($InteractionsOnly){0}else{80});language_switches=$switches;languages=10;widths=@(1440,1024,834,390);javascript_errors=$script:exceptions;external_requests_blocked=$true;forms_submitted=0;checks=$results}|ConvertTo-Json -Depth 10|Set-Content -LiteralPath (Join-Path $out 'results.json') -Encoding UTF8
 Write-Output ('PASS: '+$results.Count+' page/viewport checks; '+$switches+' language switches. Results: '+$out)
}finally{
 if($socket){$socket.Dispose()}
 if($browser -and !$browser.HasExited){Stop-Process -Id $browser.Id -ErrorAction SilentlyContinue}
}
