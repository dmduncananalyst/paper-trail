$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'revise-phase-a-preview.ps1')
$root=(Get-Location).Path
$out=Join-Path $root 'verification/phase-a'
$source=[IO.File]::ReadAllText((Join-Path $root 'index.html'))
$header=@'
<a class="skip" href="#main">Skip to content</a><div class="preview-switcher"><span>DESIGN 03</span><a href="verification/phase-a/home.html">Home</a><a href="verification/phase-a/notes.html">Notes</a><a href="verification/phase-a/article.html">Reading page</a><a href="verification/phase-a/review.html">Desktop / mobile</a></div><header class="pt-header"><div class="pt-contact-line"><span>Nationwide · Based in Los Angeles</span><a href="tel:+18189340444">818-934-0444</a><button type="button" data-email aria-haspopup="dialog">bookkeeping@papertrailusa.com</button></div><div class="pt-header-inner"><a class="pt-brand" href="verification/phase-a/home.html" aria-label="Paper Trail home"><img src="assets/images/paper-trail-logo.png" alt="Paper Trail" width="2170" height="725"></a><button class="pt-menu" aria-controls="pt-navigation" aria-expanded="false">Navigation <span aria-hidden="true">+</span></button><nav id="pt-navigation" class="pt-nav" aria-label="Main navigation"><a href="verification/phase-a/home.html">Home</a><a href="verification/phase-a/home.html#about">About</a><button class="pt-services-toggle" aria-controls="pt-directory" aria-expanded="false">Services <span aria-hidden="true">+</span></button><a href="verification/phase-a/notes.html">Notes</a><a href="areas-we-serve.html">Contact Us</a></nav></div><nav class="pt-directory" id="pt-directory" aria-label="Service directory" hidden>
'@
$nav=[regex]::Match($source,'<nav[^>]*class="site-nav"[\s\S]*?</nav>').Value
$groups=[regex]::Matches($nav,'<div class="nav-group "><button[^>]*>(.*?)</button><div class="dropdown">([\s\S]*?)</div></div>')
foreach($group in $groups){if($group.Groups[1].Value -match 'Bookkeeping'){$links=[regex]::Replace($group.Groups[2].Value,'(<a[^>]*class="overview"[^>]*>).*?(</a>)','$1Service overview$2');$header+='<div><h2>'+$group.Groups[1].Value+'</h2>'+$links+'</div>'}}
$header+='<div class="pt-other-links"><a href="services.html">All Services</a><a href="blog.html">Blog</a><a href="faq.html">Working With Paper Trail</a></div></nav></header>'
$footer=@'
<footer class="pt-footer"><div class="pt-footer-main"><p>Nationwide.<br>Based in Los Angeles.</p><nav aria-label="Footer"><a href="services.html">Services</a><a href="verification/phase-a/notes.html">Notes</a><a href="areas-we-serve.html">Contact Us</a></nav><div class="pt-footer-contact"><a href="tel:+18189340444">818-934-0444</a><button type="button" data-email aria-haspopup="dialog">bookkeeping@papertrailusa.com</button></div></div><div class="pt-footer-bottom"><span>© 2026 Paper Trail. All rights reserved.</span><a href="https://www.startweb7.com/" target="_blank" rel="noopener">Web Design and SEO by StartWeb7</a></div></footer><dialog class="email-dialog" aria-labelledby="email-title"><button class="email-close" aria-label="Close email options">×</button><h2 id="email-title">Email Paper Trail</h2><p>bookkeeping@papertrailusa.com</p><div class="email-options"><a href="https://mail.google.com/mail/?view=cm&amp;fs=1&amp;to=bookkeeping%40papertrailusa.com" target="_blank" rel="noopener">Gmail</a><a href="https://outlook.office.com/mail/deeplink/compose?to=bookkeeping%40papertrailusa.com" target="_blank" rel="noopener">Microsoft 365 / Outlook</a><a href="mailto:bookkeeping@papertrailusa.com">Default email app</a><button class="copy-email" type="button">Copy email address</button></div><p class="email-status" role="status"></p></dialog>
'@
foreach($page in @('home','notes','article')){
 $path=Join-Path $out ($page+'.html')
 $html=[IO.File]::ReadAllText($path)
 $html=[regex]::Replace($html,'<div class="preview-switcher"[\s\S]*?</nav>(?=<main)',$header)
 $html=[regex]::Replace($html,'<footer class="pt-footer">[\s\S]*?</footer>',$footer)
 $html=$html.Replace('verification/phase-a/revision.css','verification/phase-a/direction-3.css')
 if($page -eq 'home'){
  $html=$html.Replace('<p class="eyebrow">Bookkeeping for a brighter tomorrow</p>','<p class="eyebrow">Paper Trail · Nationwide</p>').Replace('<h1>More Than<br/>Bookkeeping</h1>','<h1>Bookkeeping repair<br>&amp; monthly services.</h1>')
  $html=[regex]::Replace($html,'<h1>Bookkeeping repair<br>&amp; monthly services.</h1><p>.*?</p>','<h1>Bookkeeping repair<br>&amp; monthly services.</h1><p>Past-due books, account balancing, transaction records and monthly financial reports.</p>')
  $html=$html.Replace('Get my books in order','Talk with Paper Trail').Replace('"topic": "More Than Bookkeeping"','"topic": "Bookkeeping repair and monthly services"')
  $html=[regex]::Replace($html,'<section class="benefits">[\s\S]*?</section>','')
  $about=[regex]::Match($html,'<section class="split">[\s\S]*?</section>').Value
  $html=$html.Replace($about,'')
  $about=$about.Replace('<section class="split">','<section class="about-section" id="about"><div class="section-head"><h2>About</h2><a href="about.html">About Paper Trail</a></div><div class="about-layout">').Replace('<h2>About Paper Trail</h2>','').Replace('</section>','</div></section>').Replace('assets/photos/home-about-photo-v3.webp','assets/images/service-details-paper-trail-services-html.webp').Replace('A business operator reviewing financial records at a cafe','A bookkeeping professional organizing receipts and financial records at her desk')
  $end=$html.IndexOf('</section>')+10
  $html=$html.Insert($end,$about)
  $html=$html.Replace('assets/video/monthly-poster.webp','assets/images/paper-trail-monthly-bookkeeping-html.webp').Replace('Monthly Bookkeeping Services video still','Preparing monthly bookkeeping records').Replace('width="1280" height="720" loading="lazy"','width="1448" height="1086" loading="lazy"')
  $html=$html.Replace('assets/photos/what-does-a-bookkeeper-actually-do-for-a-small-business-html-scene-v2.webp','assets/images/home-article-card-1.webp').Replace('A bookkeeping workspace with accounting software and a receipt scanner','Bookkeeping records, reports, files and a calculator').Replace('width="1536" height="1024"','width="1448" height="1086"')
  $html=[regex]::Replace($html,'<span class="round-arrow" aria-hidden="true">.*?</span>','<span class="card-action">Read more</span>')
  $html=$html.Replace('<a class="btn" href="about.html">About Paper Trail</a>','')
 }
 if($page -eq 'notes'){$html=$html.Replace('assets/photos/monthly-bookkeeping-review-html.webp','assets/photos/what-questions-should-i-ask-during-a-bookkeeping-review-html.webp')}
 if($page -eq 'article'){
  $html=$html.Replace('<header class="pt-reading-photo">','<div class="pt-reading-intro"><header class="pt-reading-photo">')
  $html=$html.Replace('</div></header><div class="pt-reading-body"><p class="pt-reading-summary">','</div></header><aside class="pt-reading-abstract"><p class="pt-kicker">Bank reconciliation</p><p class="pt-reading-summary">')
  $html=$html.Replace('</p><section id="section-0"','</p><a href="#section-0">Read the note ↓</a></aside></div><div class="pt-reading-body"><nav class="pt-contents" aria-label="In this note"><p>In this note</p>CONTENTS</nav><article class="pt-reading-content"><section id="section-0"')
  $contents=([regex]::Matches($html,'<section id="([^"]+)"[^>]*><h2>(.*?)</h2>')|ForEach-Object{'<a href="#'+$_.Groups[1].Value+'">'+$_.Groups[2].Value+'</a>'}) -join ''
  $html=$html.Replace('CONTENTS',$contents).Replace('</section></div></main>','</section></article></div></main>')
 }
 [IO.File]::WriteAllText($path,$html,[Text.UTF8Encoding]::new($false))
}
$registry=Get-Content -LiteralPath (Join-Path $out 'icon-registry.json') -Raw | ConvertFrom-Json
$used=[ordered]@{}
foreach($property in $registry.PSObject.Properties){if($property.Name -notin @('organized-records','informed-decisions','ongoing-support')){$used[$property.Name]=$property.Value}}
$used|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $out 'icon-registry.json') -Encoding UTF8
@{revision=3;uniqueCustomIcons=22;homeServiceCards=4;homeNotesCards=5;notesTopics=12;approval='Pending visual review';scope='Home, Notes listing and one reading-page prototype only. English visual stage. Multilingual work remains after design approval.';submissions='Disabled in preview';video='Original home.mp4, original hero section, playback and pause control retained'}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $out 'prototype-scope.json') -Encoding UTF8
Write-Output 'Direction 03 generated: Home, Notes, reading page.'
