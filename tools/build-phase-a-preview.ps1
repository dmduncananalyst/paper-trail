$ErrorActionPreference='Stop'
$root=(Get-Location).Path;$out=Join-Path $root 'verification/phase-a'
$notes=[IO.File]::ReadAllText((Join-Path $root 'notes.html'))
$homeSource=[IO.File]::ReadAllText((Join-Path $root 'index.html'))
$article=[IO.File]::ReadAllText((Join-Path $root 'why-does-my-bank-balance-not-match-my-books.html'))
$base=([uri]($root+'\')).AbsoluteUri
$header='<div class="review-strip">PAPER TRAIL · PHASE A DESIGN PREVIEW · ENGLISH ONLY · LOCAL</div><header class="new-header"><a class="new-brand" href="verification/phase-a/home.html"><img src="assets/images/paper-trail-logo.png" alt="Paper Trail"></a><nav class="new-nav" aria-label="Main navigation"><a href="verification/phase-a/home.html" data-page="home">Home</a><a href="services.html">Services</a><a href="verification/phase-a/notes.html" data-page="notes">Notes</a><a href="about.html">About</a><a href="areas-we-serve.html">Contact</a></nav><button id="navigation-toggle" class="menu-button" aria-expanded="false" aria-controls="navigation-panel">All destinations +</button></header>'
$nav=[regex]::Match($homeSource,'<nav[^>]*class="site-nav"[\s\S]*?</nav>').Value
$links=[regex]::Matches($nav,'<a\b[^>]*href="([^"]+)"[^>]*>([\s\S]*?)</a>')
$navLinks=foreach($m in $links){'<a href="'+$m.Groups[1].Value+'">'+$m.Groups[2].Value+'</a>'}
$header+='<nav id="navigation-panel" class="nav-panel" aria-label="All destinations" hidden><div><h2>Services</h2>'+ (($navLinks|Where-Object {$_ -notmatch 'questions|index.html|about.html|areas-we-serve|faq.html|notes.html|blog.html'}) -join '')+'</div><div><h2>Notes topics</h2>'+ (([regex]::Matches($notes,'<a class="notes-topic-card" href="([^"]+)"[\s\S]*?<h2>(.*?)</h2>')|ForEach-Object {'<a href="'+$_.Groups[1].Value+'">'+$_.Groups[2].Value+'</a>'}) -join '')+'</div><div><h2>Paper Trail</h2><a href="about.html">About</a><a href="faq.html">Working With Paper Trail</a><a href="areas-we-serve.html">Contact Us</a><a href="blog.html">Blog</a></div><div><h2>Nationwide</h2><a href="areas-we-serve.html">Nationwide - Based in Los Angeles</a></div></nav>'
$tabs='<nav class="preview-links" aria-label="Prototype pages"><a href="verification/phase-a/home.html">Homepage sample</a><a href="verification/phase-a/notes.html">Notes listing</a><a href="verification/phase-a/article.html">Notes reading page</a></nav>'
$footer='<footer class="new-footer"><strong>Paper Trail</strong><span>Remote bookkeeping nationwide.<br>In person throughout LA County, by appointment only.</span><a href="areas-we-serve.html">Contact Paper Trail</a></footer>'
$head='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><base href="'+$base+'"><title>Paper Trail · Design preview</title><link rel="stylesheet" href="verification/phase-a/prototype.css"></head><body>'
$icons=@(
'<path d="m10 34 21-24 7 6-21 24-10 3z M28 14l7 6 M11 33l7 6 M8 11h13 M8 18h7"/>',
'<path d="M12 7h24 M12 41h24 M15 7v7c0 6 18 14 18 20v7 M33 7v7c0 6-18 14-18 20v7 M18 35h12 M18 13h12"/>',
'<path d="M24 6v35 M10 13h28 M13 13 6 27h14z M35 13l-7 14h14z M16 41h16"/>',
'<path d="M7 13h34v8H7z M10 21v21h28V21 M18 27h12v6H18z M14 7h20"/><path d="m20 10 4 3 4-3"/>',
'<path d="M14 5h17l7 8v29H14z M31 5v9h7 M20 20h12 M20 26h12 M20 32h5"/><path d="M7 15v23"/>',
'<path d="M8 11h31v29H8z M8 19h31 M16 6v10 M30 6v10 M14 26h5 M25 26h7 M14 33h5 M25 33h7"/>'
)
$photos=@('assets/images/paper-trail-services-html.webp','assets/photos/past-due-bookkeeping-html.webp','assets/photos/balancing-corrections-html.webp','assets/photos/year-end-bookkeeping-html.webp','assets/photos/tax-ready-bookkeeping-html.webp','assets/images/paper-trail-monthly-bookkeeping-html.webp')
$topics=[regex]::Matches($notes,'<a class="notes-topic-card" href="([^"]+)"[\s\S]*?<h2>(.*?)</h2>[\s\S]*?</a>')
$cards=for($i=0;$i -lt 6;$i++){$m=$topics[$i];$photo=$photos[$i]; if(!(Test-Path (Join-Path $root $photo))){$photo='assets/images/'+($m.Groups[1].Value -replace '-questions.html','-html.webp');if(!(Test-Path (Join-Path $root $photo))){throw "Missing approved topic photo: $photo"}};'<a class="glow-card" href="'+$m.Groups[1].Value+'"><img src="'+$photo+'" alt="" width="1536" height="1024"><div class="card-words"><svg class="topic-icon" role="img" aria-label="'+[Net.WebUtility]::HtmlEncode(([Net.WebUtility]::HtmlDecode($m.Groups[2].Value))+' symbol')+'" viewBox="0 0 48 48">'+$icons[$i]+'</svg><h2>'+$m.Groups[2].Value+'</h2><span class="read-link">Read About '+$m.Groups[2].Value+'</span></div></a>'}
$body='<main class="notes-composition"><aside class="notes-intro"><span class="small-label">The Paper Trail notebook</span><h1>Notes</h1><p>Practical guides to catching up your books, tracking business money and understanding your monthly reports.</p><p class="index-line">Choose a topic to find the details that matter to your business.</p></aside><section class="glow-grid" aria-label="Bookkeeping topics">'+($cards -join '')+'</section></main>'
$head+$header+$tabs+$body+$footer+'<script src="verification/phase-a/prototype.js"></script></body></html>'|Set-Content (Join-Path $out 'notes.html') -Encoding UTF8
$title=[regex]::Match($article,'<h1[^>]*>(.*?)</h1>').Groups[1].Value
$summary=[regex]::Match($article,'<p class="summary">([\s\S]*?)</p>').Groups[1].Value
$content=[regex]::Match($article,'<article class="article-content">([\s\S]*?)</article>').Groups[1].Value
if(!$content){throw 'Article body extraction failed'}
$body='<main><section class="reader-head"><aside><span class="small-label">Notes / Balancing &amp; Corrections</span><p><a href="balancing-and-corrections-questions.html">All notes on this topic</a></p></aside><div class="reader-photo"><img src="assets/photos/why-does-my-bank-balance-not-match-my-books-html.webp" alt="Bank and credit card statements being compared with bookkeeping records"><div class="card-words"><svg class="topic-icon" role="img" aria-label="Statement and ledger comparison" viewBox="0 0 48 48"><path d="M5 8h15v30H5z M28 11h15v30H28z M9 15h7 M9 21h7 M32 18h7 M32 24h7 M18 44h14 M24 7v34"/><path d="m21 10 3-3 3 3 M21 38l3 3 3-3"/></svg><h1>'+$title+'</h1></div></div></section><div class="reader-content"><p class="summary">'+$summary+'</p>'+$content+'</div></main>'
$head+$header+$tabs+$body+$footer+'<script src="verification/phase-a/prototype.js"></script></body></html>'|Set-Content (Join-Path $out 'article.html') -Encoding UTF8
$homeHead=$head.Replace('<link rel="stylesheet" href="verification/phase-a/prototype.css">','<link rel="stylesheet" href="assets/site.css"><link rel="stylesheet" href="assets/presentation.css"><link rel="stylesheet" href="verification/phase-a/prototype.css"><link rel="stylesheet" href="verification/phase-a/home.css">')
$homeMain=[regex]::Match($homeSource,'<main\b[\s\S]*?</main>').Value
$homeMain=[regex]::Replace($homeMain,'<dialog\b[\s\S]*?</dialog>','')
$homeMain=[regex]::Replace($homeMain,'<script type="application/json"[\s\S]*?</script>','')
$homeMain=[regex]::Replace($homeMain,'<button[^>]*data-open-chat[^>]*>([\s\S]*?)</button>','<a class="btn" href="areas-we-serve.html">$1</a>')
$homeHead+$header+$tabs+'<div class="home-prototype">'+$homeMain+'</div>'+$footer+'<script src="verification/phase-a/prototype.js"></script><script>document.querySelectorAll(".video-toggle").forEach(b=>{const v=b.parentElement.querySelector("video");const sync=()=>{b.textContent=v.paused?"Play":"Pause";b.setAttribute("aria-label",v.paused?"Play background video":"Pause background video")};b.onclick=()=>{if(v.paused)v.play().catch(sync);else v.pause()};v.onplay=sync;v.onpause=sync;if(matchMedia("(prefers-reduced-motion: reduce)").matches)v.pause();sync()})</script></body></html>'|Set-Content (Join-Path $out 'home.html') -Encoding UTF8
@{uniqueIcons=7;repeatedIcons=0;representativeTopics=6;articleTitle=[Net.WebUtility]::HtmlDecode($title);note='Phase A only. English only. Home conversation buttons navigate to the existing Contact page; no form submission or AI is connected in this preview.'}|ConvertTo-Json|Set-Content (Join-Path $out 'prototype-scope.json') -Encoding UTF8
'Prototype generated.'
