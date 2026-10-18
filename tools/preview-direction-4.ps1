$ErrorActionPreference='Stop'
$root=(Get-Location).Path
$out=Join-Path $root 'verification/phase-a'
$reading=Join-Path $out 'reading'
$topicsOut=Join-Path $out 'topics'
New-Item -ItemType Directory -Force -Path $reading,$topicsOut | Out-Null
function ReadSite($name){[IO.File]::ReadAllText((Join-Path $root $name))}
function SavePreview($name,$text){[IO.File]::WriteAllText((Join-Path $out $name),$text,[Text.UTF8Encoding]::new($false))}
function TextOnly($s){[Net.WebUtility]::HtmlDecode([regex]::Replace($s,'<[^>]+>','')).Trim()}
$icons=Get-Content -LiteralPath (Join-Path $out 'icon-registry.json') -Raw|ConvertFrom-Json
function Icon($id){'<svg class="pt-icon" viewBox="0 0 48 48" data-icon-id="'+$id+'" aria-hidden="true">'+$icons.$id+'</svg>'}
function Label($id,$text){'<span data-i18n="'+$id+'">'+$text+'</span>'}
$header=@'
<a class="skip" href="#main">Skip to content</a><header class="pt-header"><div class="header-brand"><a href="verification/phase-a/home.html" aria-label="Paper Trail home"><span class="brand-art"><img class="brand-paper" src="assets/images/paper-trail-logo.png" alt="Paper Trail" width="2170" height="725"><img class="brand-lettering" src="assets/images/paper-trail-logo.png" alt="" aria-hidden="true" width="2170" height="725"></span></a></div><div class="header-tools"><a href="tel:+18189340444">818-934-0444</a><button type="button" data-email aria-haspopup="dialog">bookkeeping@papertrailusa.com</button><label class="language-control"><svg class="language-symbol" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c5 5 5 13 0 18M12 3c-5 5-5 13 0 18"/></svg><span class="sr-only" data-i18n="language">Language</span><select id="language" aria-label="Language"><option value="en">English</option><option value="es">Español</option><option value="fa">فارسی</option><option value="hy">Հայերեն</option><option value="zh-CN">中文</option><option value="ko">한국어</option><option value="tl">Tagalog</option><option value="te">తెలుగు</option><option value="ru">Русский</option><option value="ar">العربية</option></select></label></div><nav class="pt-nav" aria-label="Main navigation"><a href="verification/phase-a/home.html" data-i18n="home">Home</a><a href="verification/phase-a/home.html#about" data-i18n="about">About</a><div class="nav-family"><a href="paper-trail-services.html" aria-haspopup="true" aria-expanded="false" data-i18n="repair">Bookkeeping Repair</a><div class="nav-panel"><a href="paper-trail-services.html" data-i18n="repairOverview">Bookkeeping Overview</a><a href="past-due-bookkeeping.html" data-i18n="pastDue">Past Due Bookkeeping</a><a href="balancing-corrections.html" data-i18n="balancing">Balancing &amp; Corrections</a><a href="year-end-bookkeeping.html" data-i18n="yearEnd">Year End Bookkeeping</a><a href="tax-ready-bookkeeping.html" data-i18n="taxReady">Tax Ready Bookkeeping</a></div></div><div class="nav-family"><a href="paper-trail-monthly-bookkeeping.html" aria-haspopup="true" aria-expanded="false" data-i18n="monthly">Monthly Bookkeeping</a><div class="nav-panel"><a href="paper-trail-monthly-bookkeeping.html" data-i18n="monthlyOverview">Monthly Bookkeeping Overview</a><a href="transaction-categorization.html" data-i18n="categorization">Transaction Categorization</a><a href="income-expense-tracking.html" data-i18n="income">Income &amp; Expense Tracking</a><a href="bank-credit-card-balancing.html" data-i18n="bank">Bank &amp; Credit Card Balancing</a><a href="accounts-payable-receivable.html" data-i18n="payables">Accounts Payable &amp; Receivable</a><a href="monthly-financial-reports.html" data-i18n="reports">Monthly Financial Reports</a><a href="monthly-bookkeeping-review.html" data-i18n="review">Monthly Bookkeeping Review</a></div></div><a href="verification/phase-a/notes.html" data-i18n="notes">Notes</a><a href="verification/phase-a/blog.html" data-i18n="blog">Blog</a><a href="verification/phase-a/areas-we-serve.html" data-i18n="contact">Contact Us</a></nav></header><p class="translation-notice" data-i18n="notice" hidden>Only the Home and Notes pages are available in this language.</p>
'@
$footer=@'
<footer class="pt-footer"><div><a class="footer-location" href="verification/phase-a/areas-we-serve.html" data-i18n="location">Nationwide – Based in Los Angeles.</a><nav aria-label="Footer"><a href="verification/phase-a/notes.html" data-i18n="notes">Notes</a><a href="services.html" data-i18n="services">Services</a><a href="verification/phase-a/areas-we-serve.html" data-i18n="contact">Contact Us</a></nav><div class="footer-contact"><a href="tel:+18189340444">818-934-0444</a><button type="button" data-email aria-haspopup="dialog">bookkeeping@papertrailusa.com</button></div></div><div class="footer-bottom"><span data-i18n="copyright">© 2026 Paper Trail. All rights reserved.</span><a href="https://www.startweb7.com/" target="_blank" rel="noopener" data-i18n="credit">Web Design and SEO by StartWeb7</a></div></footer><dialog class="email-dialog" aria-labelledby="email-title"><button class="email-close" aria-label="Close email options">×</button><h2 id="email-title" data-i18n="emailTitle">Email Paper Trail</h2><p>bookkeeping@papertrailusa.com</p><div class="email-options"><a href="https://mail.google.com/mail/?view=cm&amp;fs=1&amp;to=bookkeeping%40papertrailusa.com" target="_blank" rel="noopener">Gmail</a><a href="https://outlook.office.com/mail/deeplink/compose?to=bookkeeping%40papertrailusa.com" target="_blank" rel="noopener">Microsoft 365 / Outlook</a><a href="mailto:bookkeeping@papertrailusa.com" data-i18n="defaultEmail">Default email app</a><button type="button" class="copy-email" data-i18n="copyEmail">Copy email address</button></div><p class="email-status" role="status"></p></dialog>
'@
$areaSource=ReadSite 'areas-we-serve.html'
$cityLinks=[regex]::Matches($areaSource,'<a class="photo-card"[^>]*href="(bookkeeping-[^"]+)"[\s\S]*?<h3>(.*?)</h3>')
$cityNav='<nav class="footer-cities" aria-label="Los Angeles County cities">'
foreach($city in $cityLinks){$cityNav+='<a href="'+$city.Groups[1].Value+'">'+$city.Groups[2].Value+'</a>'}
$cityNav+='</nav>'
$footer=$footer.Replace('<div class="footer-bottom">',$cityNav+'<div class="footer-bottom">')
function Page($title,$content,$kind,$depth=0,$chat=$false){
 $base=if($depth){'../../../'}else{'../../'}
 $scripts='<script defer src="verification/phase-a/direction-4.js?v=hero-hover-padding-15"></script>'
 if($chat){$scripts='<script src="verification/phase-a/preview-safety.js"></script><script defer src="assets/site.js"></script>'+$scripts}
 '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><base href="'+$base+'"><title>'+[Net.WebUtility]::HtmlEncode((TextOnly $title))+' | Paper Trail preview</title><script>try{document.documentElement.dataset.colorDirection="neutral"}catch{}</script><script>try{const l=localStorage.getItem("paper-trail-preview-language");if((location.pathname.endsWith("/home.html")||location.pathname.endsWith("/notes.html"))&&l&&l!=="en")document.documentElement.classList.add("locale-loading")}catch{}</script><link rel="stylesheet" href="assets/site.css"><link rel="stylesheet" href="verification/phase-a/direction-4.css?v=hero-hover-padding-15"><script src="verification/phase-a/locales/drafts.js"></script></head><body class="pt-preview '+$kind+'">'+$header+$content+$footer+$scripts+'</body></html>'
}
$source=ReadSite 'index.html'
$homePreviewMain=[regex]::Match($source,'<main\b[\s\S]*?</main>').Value
$hero=[regex]::Match($homePreviewMain,'<section class="hero home">[\s\S]*?</section>').Value
$film=[regex]::Match($hero,'<div class="video-frame home-video">[\s\S]*?</div>').Value
$dialog=[regex]::Match($homePreviewMain,'<dialog id="conversation-dialog"[\s\S]*?</script>').Value
$dialog=$dialog.Replace('"topic": "More Than Bookkeeping"','"topic": "Business bookkeeping"')
$homePreview='<main id="main"><section class="home-hero"><div class="hero-heading"><h1 data-i18n="hero">Bookkeeping</h1><p class="hero-description" data-i18n="heroDescription">From overdue records to monthly reports, we help you keep track of income, expenses, and account balances.</p></div><div class="hero-workspace">'+$film+'<div class="hero-service-links"><a href="paper-trail-services.html">'+(Icon 'past-due-service')+(Label 'catchUp' 'Catch up overdue books')+'<span class="hero-service-action" data-i18n="viewRepair">View Repair</span>'+'</a><a href="paper-trail-monthly-bookkeeping.html">'+(Icon 'monthly-service')+(Label 'keepCurrent' 'Keep monthly records current')+'<span class="hero-service-action" data-i18n="viewMonthly">View Monthly</span>'+'</a></div></div></section>'
$aboutText=[regex]::Match($homePreviewMain,'<div class="split-copy">[\s\S]*?</div>').Value
$paras=[regex]::Matches($aboutText,'<p>(.*?)</p>')
$homePreview+='<section class="home-about" id="about"><div class="about-content"><img src="assets/images/service-details-paper-trail-services-html.webp" alt="Bookkeeping professional organizing receipts and records" width="1448" height="1086" loading="lazy"><div><h2 class="about-text-title" data-i18n="about">About</h2><p data-i18n="aboutBody">'+$paras[0].Groups[1].Value+'</p><p data-i18n="aboutClosing">'+$paras[1].Groups[1].Value+'</p><a class="action quiet" href="about.html" data-i18n="aboutPaperTrail">About Paper Trail</a></div></div></section>'
$homePreview+='<section class="home-services" id="home-services"><div class="section-label"><h2 data-i18n="services">Services</h2><a class="action quiet" href="services.html" data-i18n="allServices">All Services</a></div><div class="service-grid">'
$services=@(@('past-due-bookkeeping.html','assets/photos/past-due-bookkeeping-html.webp','pastDue','Past Due Bookkeeping','past-due-service'),@('paper-trail-monthly-bookkeeping.html','assets/images/paper-trail-monthly-bookkeeping-html.webp','monthly','Monthly Bookkeeping','monthly-service'),@('balancing-corrections.html','assets/photos/balancing-corrections-html.webp','balancing','Balancing &amp; Corrections','corrections-service'),@('tax-ready-bookkeeping.html','assets/photos/tax-ready-bookkeeping-html.webp','taxReady','Tax Ready Bookkeeping','tax-ready-service'))
# Hero uses dedicated icons, so the service cards keep their own four unique symbols.
$homePreview=$homePreview.Replace((Icon 'past-due-service'),(Icon 'repair-hero')).Replace((Icon 'monthly-service'),(Icon 'monthly-hero'))
foreach($s in $services){$homePreview+='<a class="service-tile" href="'+$s[0]+'"><img src="'+$s[1]+'" alt="" width="1448" height="1086" loading="lazy"><div class="service-copy">'+(Icon $s[4])+'<h3 data-i18n="'+$s[2]+'">'+$s[3]+'</h3><span class="tile-action" data-i18n="viewService">View service</span></div></a>'}
$homePreview+='</div></section><section class="home-notes" id="home-notes"><div class="section-label"><h2 data-i18n="notes">Notes</h2><a class="action quiet" href="verification/phase-a/notes.html" data-i18n="allNotes">All Notes</a></div><div class="home-note-list">'
$noteCards=[regex]::Matches($homePreviewMain,'<a class="note-card" href="([^"]+)"[\s\S]*?<img[^>]*src="([^"]+)"[\s\S]*?<h3>(.*?)</h3>[\s\S]*?</a>')
$noteIconIds=@('bookkeeper-work','reconciliation-routine','business-expenses','tax-preparer-handoff','approve-monthly-reports')
for($i=0;$i -lt [Math]::Min(4,$noteCards.Count);$i++){$n=$noteCards[$i];$photo=@('assets/images/home-article-card-1.webp','assets/images/bank-credit-card-balancing-html.webp','assets/photos/transaction-categorization-html.webp','assets/images/home-article-card-4.webp','assets/photos/monthly-financial-reports-html.webp')[$i];$homePreview+='<a class="home-note" href="verification/phase-a/reading/'+$n.Groups[1].Value+'"><img src="'+$photo+'" alt="" width="1448" height="1086" loading="lazy"><div class="home-note-copy"><span class="note-emblem">'+(Icon $noteIconIds[$i])+'</span><h3 data-i18n="homeNote'+$i+'">'+$n.Groups[3].Value+'</h3><span class="action quiet" data-i18n="readNote">Read</span><small class="article-language" data-i18n="englishNote" hidden>Full note in English.</small></div></a>'}
$homePreview+='</div></section><section class="home-conversation"><button class="action" data-open-chat type="button" data-i18n="talk">Talk with Paper Trail</button></section>'+$dialog+'</main>'
SavePreview 'home.html' (Page 'Home' $homePreview 'pt-home' 0 $true)
$notesSource=ReadSite 'notes.html'
$topics=[regex]::Matches($notesSource,'<a class="notes-topic-card" href="([^"]+)"[\s\S]*?<h2>(.*?)</h2>[\s\S]*?</a>')
$topicIcons=@('repair-topic','overdue-topic','balancing-topic','year-end-topic','tax-topic','monthly-topic','categorization-topic','income-expense-topic','bank-card-topic','payables-receivables-topic','financial-reports-topic','monthly-review-topic')
$topicKeys=@('repair','pastDue','balancing','yearEnd','taxReady','monthly','categorization','income','bank','payables','reports','review')
$photos=@('assets/images/paper-trail-services-html.webp','assets/photos/past-due-bookkeeping-html.webp','assets/images/home-article-card-2.webp','assets/images/home-article-card-4.webp','assets/photos/tax-ready-bookkeeping-html.webp','assets/images/paper-trail-monthly-bookkeeping-html.webp','assets/photos/transaction-categorization-html.webp','assets/images/service-details-income-expense-tracking-html.webp','assets/photos/bank-credit-card-balancing-html.webp','assets/photos/accounts-payable-receivable-html.webp','assets/images/home-article-card-1.webp','assets/photos/monthly-financial-reports-html.webp')
$notes='<main id="main"><h1 class="center-title" data-i18n="notes">Notes</h1><div class="topic-index">'
$articleNames=[Collections.Generic.HashSet[string]]::new()
for($i=0;$i -lt $topics.Count;$i++){
 $t=$topics[$i];$target=$t.Groups[1].Value;$title=$t.Groups[2].Value
 $notes+='<a class="topic-row" href="verification/phase-a/topics/'+$target+'"><span class="topic-emblem">'+(Icon $topicIcons[$i])+'</span><h2 data-i18n="'+$topicKeys[$i]+'">'+$title+'</h2><img src="'+$photos[$i]+'" alt="" width="1448" height="1086" loading="lazy"><span class="action quiet" data-i18n="readNotes">Read</span><small class="article-language" data-i18n="englishNote" hidden>Full note in English.</small></a>'
 $category=ReadSite $target
 $categoryMain=[regex]::Match($category,'<main\b[\s\S]*?</main>').Value
 $links=[regex]::Matches($categoryMain,'<a[^>]*class="(?:reading-link|photo-card)[^"]*"[^>]*href="([^"]+)"[\s\S]*?</a>')
 if(!$links.Count){$links=[regex]::Matches($categoryMain,'<a[^>]*href="([^"]+)"[\s\S]*?</a>')}
 $topicBody='<main id="main"><header class="topic-opening"><h1>'+$title+'</h1><a class="action quiet" href="verification/phase-a/notes.html">All Notes</a></header><div class="topic-reading-list">'
 foreach($link in $links){$file=$link.Groups[1].Value;if(!(Test-Path (Join-Path $root $file))){continue};$articleSource=ReadSite $file;if($articleSource -notmatch '<article class="article-content">'){continue};[void]$articleNames.Add($file);$actualTitle=[regex]::Match($articleSource,'<h1[^>]*>(.*?)</h1>').Groups[1].Value;$topicBody+='<a href="verification/phase-a/reading/'+$file+'"><h2>'+$actualTitle+'</h2><span class="action quiet">Read</span></a>'}
 $topicBody+='</div></main>'
 SavePreview ('topics/'+$target) (Page $title $topicBody 'pt-topic' 1)
}
$notes+='</div><div class="notes-blog-button"><a class="action" href="verification/phase-a/blog.html" data-i18n="blog">Blog</a></div></main>'
SavePreview 'notes.html' (Page 'Notes' $notes 'pt-notes')
foreach($n in $noteCards){[void]$articleNames.Add($n.Groups[1].Value)}
[void]$articleNames.Add('why-does-my-bank-balance-not-match-my-books.html')
$blogSource=ReadSite 'blog.html'
$blogCards=[regex]::Matches($blogSource,'<a class="photo-card"[^>]*href="([^"]+)"[\s\S]*?<img[^>]*src="([^"]+)"[\s\S]*?<h3>(.*?)</h3>[\s\S]*?</a>')
$blog='<main id="main" class="blog-main"><h1 class="blog-title">Blog</h1><div class="blog-story-list">'
for($i=0;$i -lt $blogCards.Count;$i++){
 $b=$blogCards[$i];[void]$articleNames.Add($b.Groups[1].Value)
 $photo=if($i -eq 2){'assets/photos/tax-ready-bookkeeping-html.webp'}else{$b.Groups[2].Value}
 $blog+='<article class="blog-story"><img src="'+$photo+'" alt="" loading="lazy"><div><h2>'+$b.Groups[3].Value+'</h2><a class="action" href="verification/phase-a/reading/'+$b.Groups[1].Value+'">Read</a></div></article>'
}
$blog+='</div></main>'
SavePreview 'blog.html' (Page 'Blog' $blog 'pt-blog')
$globe=[regex]::Match($areaSource,'<figure class="nationwide-globe">[\s\S]*?</figure>').Value
# Match the Contact globe to the approved neutral preview palette.
$globeColors=@{'#f7f5e9'='#f5f5f5';'#e7ebda'='#e7e7e7';'#c4cfb7'='#cccccc';'#173d31'='#202020';'#294d3b'='#333333';'#a1af98'='#aaaaaa';'#a4b69b'='#aaaaaa';'#a6b39a'='#b0b0b0';'#c0cdb2'='#cccccc';'#7a9670'='#8a8a8a';'#365b42'='#505050';'#f3f1dd'='#f2f2f2';'#f4ead5'='#ffffff';'#f9edce'='#ffffff';'#264632'='#303030';'#193d31'='#202020';'#f8f5eb'='#f7f7f7';'#bcc9b1'='#c5c5c5'}
foreach($color in $globeColors.Keys){$globe=$globe.Replace($color,$globeColors[$color])}
$contactBody='<main id="main" class="contact-main"><h1>Contact Us – Nationwide</h1><div class="contact-intro"><div><p>Remote bookkeeping nationwide over Zoom. In-person meetings throughout Los Angeles County, by appointment only.</p><div class="contact-methods"><a href="tel:+18189340444">818-934-0444</a><button type="button" data-email aria-haspopup="dialog">bookkeeping@papertrailusa.com</button></div><a class="action quiet" href="faq.html">Working With Paper Trail</a></div>'+$globe+'</div>'

$contactBody+='</main>'
SavePreview 'areas-we-serve.html' (Page 'Contact Us – Nationwide' $contactBody 'pt-contact')
$preserved=@()
foreach($file in $articleNames){
 $a=ReadSite $file
 $title=[regex]::Match($a,'<h1[^>]*>(.*?)</h1>').Groups[1].Value
 $summary=[regex]::Match($a,'<p class="summary">([\s\S]*?)</p>').Groups[1].Value
 $body=[regex]::Match($a,'<article class="article-content">([\s\S]*?)</article>').Groups[1].Value
 $photo=[regex]::Match($a,'<img[^>]*src="(assets/photos/[^"]+)"').Groups[1].Value
 if(!$photo){$photo='assets/photos/why-does-my-bank-balance-not-match-my-books-html.webp'}
 $content='<main id="main"><article class="reading-feature"><header class="reading-masthead"><img src="'+$photo+'" alt="Bookkeeping records related to this note" loading="eager"><h1>'+$title+'</h1></header><div class="reading-column"><p class="reading-lead">'+$summary+'</p><div class="reading-spread">'+$body+'</div></div></article><div class="reading-actions"><a class="action" href="verification/phase-a/notes.html">Notes</a><a class="action quiet" href="verification/phase-a/blog.html">Blog</a></div></main>'
 $page=Page $title $content 'pt-reading' 1
 SavePreview ('reading/'+$file) $page
 $preserved+=@{file=$file;fullBodyPreserved=$page.Contains($body);titlePreserved=$page.Contains('<h1>'+$title+'</h1>')}
}
# Cross-links between reading samples keep visitors inside the redesign preview.
foreach($file in $articleNames){$path=Join-Path $reading $file;$page=[IO.File]::ReadAllText($path);foreach($target in $articleNames){$page=$page.Replace('href="'+$target+'"','href="verification/phase-a/reading/'+$target+'"')};[IO.File]::WriteAllText($path,$page,[Text.UTF8Encoding]::new($false))}
$sample=[IO.File]::ReadAllText((Join-Path $reading 'why-does-my-bank-balance-not-match-my-books.html')).Replace('<base href="../../../">','<base href="../../">')
SavePreview 'article.html' $sample
$blogSample=[IO.File]::ReadAllText((Join-Path $reading 'profit-vs-cash-flow-business-money.html')).Replace('<base href="../../../">','<base href="../../">')
SavePreview 'blog-article.html' $blogSample
$preserved | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $out 'direction-4-preservation.json') -Encoding UTF8
@{revision=4;topics=$topics.Count;readingPreviews=$articleNames.Count;blogStories=$blogCards.Count;languages='English plus nine locally authored draft locales; zero provider calls';scope='Separate preview pages only. Original website files remain unchanged.';approval='Design approval pending';translationBackend='Not activated';chat='Existing English guided conversation preserved. Preview sends blocked; multilingual free-form chat not implemented.'}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $out 'prototype-scope.json') -Encoding UTF8
Write-Output ('Direction 04: Home, Notes, Blog, '+$topics.Count+' topics and '+$articleNames.Count+' reading previews.')
