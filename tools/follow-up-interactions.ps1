$interactions=@()
Cdp 'Emulation.setDeviceMetricsOverride' @{width=1440;height=1100;deviceScaleFactor=1;mobile=$false}|Out-Null
foreach($route in @('index.html','areas-we-serve.html','balancing-corrections.html','transaction-categorization.html','notes.html')) {
 Load $route
 $r=Cdp 'Runtime.evaluate' @{expression='(()=>{document.querySelector("[data-open-chat]").click();const q=()=>document.querySelector(".chat-question")?.textContent;const questions=[q()];const answers=["California","Overdue books","A few months"];for(const value of answers){const i=document.querySelector(".chat input");i.value=value;document.querySelector(".send-message").click();questions.push(q())}return {questions,questionCount:document.querySelectorAll(".chat-question").length,oldQuestions:[...document.querySelectorAll(".chat .bubble")].filter(e=>e.textContent.includes("What state are you")).length,answers:[...document.querySelectorAll(".bubble.user")].map(e=>e.textContent)}})()';returnByValue=$true}
 $interactions+=@{page=$route;chat=$r.result.value}
 if($route -eq 'areas-we-serve.html'){Shot 'chat-desktop'}
}
Load 'index.html'
$r=Cdp 'Runtime.evaluate' @{expression='(()=>{document.querySelector(".header-tools a[href^=tel]").click();return {open:document.querySelector(".phone-dialog").open,number:document.querySelector(".phone-dialog a").getAttribute("href")}})()';returnByValue=$true};$interactions+=@{phone=$r.result.value};Shot 'phone-desktop'
$interactions|ConvertTo-Json -Depth 12|Set-Content (Join-Path $out 'interaction-checks.json') -Encoding UTF8
# Observe cold navigation, including direct file access used in the IDE.
$observer='window.coldShifts=[];new PerformanceObserver(list=>{for(const e of list.getEntries())if(!e.hadRecentInput)window.coldShifts.push({value:e.value,sources:e.sources.map(s=>({tag:s.node?.tagName,cls:s.node?.className,previous:s.previousRect,current:s.currentRect}))})}).observe({type:"layout-shift",buffered:true});window.coldFrames=[];addEventListener("DOMContentLoaded",()=>{const start=performance.now();function sample(){const box=e=>{const r=e?.getBoundingClientRect();return r?[r.x,r.y,r.width,r.height]:null};coldFrames.push({time:performance.now(),nav:box(document.querySelector(".pt-nav")),video:box(document.querySelector(".video-frame")),hero:box(document.querySelector("h1")),image:box(document.querySelector("main img"))});if(performance.now()-start<1800)requestAnimationFrame(sample)}sample()})'
Cdp 'Page.addScriptToEvaluateOnNewDocument' @{source=$observer}|Out-Null
$cold=@()
Cdp 'Network.setCacheDisabled' @{cacheDisabled=$true}|Out-Null
foreach($width in @(1440,834,390)) {
 Cdp 'Emulation.setDeviceMetricsOverride' @{width=$width;height=1100;deviceScaleFactor=1;mobile=($width -lt 600)}|Out-Null
 foreach($protocol in @('http','file')) {
 foreach($route in @('index.html','blog.html','notes.html','paper-trail-services.html','bookkeeping-chatsworth.html','state-records/arkansas.html','catch-up-bookkeeping-overdue-books.html')) {
 $url=if($protocol -eq 'http'){'http://127.0.0.1:8765/'+$route}else{([uri]((Join-Path (Get-Location) $route))).AbsoluteUri}
 Cdp 'Page.navigate' @{url=$url}|Out-Null
 Start-Sleep -Milliseconds 2100
 $r=Cdp 'Runtime.evaluate' @{expression='({url:location.href,frames:window.coldFrames,shifts:window.coldShifts,fonts:document.fonts.status,ready:document.readyState,missing:[...document.images].filter(i=>i.loading!=="lazy"&&(!i.complete||!i.naturalWidth)).map(i=>i.src)})';returnByValue=$true}
 $cold+=@{page=$route;protocol=$protocol;viewport=$width;result=$r.result.value}
 }
 }
}
$cold|ConvertTo-Json -Depth 20|Set-Content (Join-Path $out 'cold-load-checks.json') -Encoding UTF8
