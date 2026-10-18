$ErrorActionPreference='Stop'
$root=(Get-Location).Path
$out=Join-Path $root 'verification/phase-a'
$homeSource=[IO.File]::ReadAllText((Join-Path $root 'index.html'))
$notesSource=[IO.File]::ReadAllText((Join-Path $root 'notes.html'))
$articleSource=[IO.File]::ReadAllText((Join-Path $root 'why-does-my-bank-balance-not-match-my-books.html'))
$drawings=@(
@('organized-records','<path d="M10 8h24v30H10z M6 13H3v29h26v-4 M16 16h12 M16 23h12 M16 30h8"/><path d="m33 28 5 5 7-10"/>'),
@('informed-decisions','<path d="M6 39h36 M10 33V22h6v11 M22 33V16h6v17 M34 33V8h6v25 M9 14l13-8 6 4 10-7"/>'),
@('ongoing-support','<path d="M11 28V19a13 13 0 0 1 26 0v9 M11 20H6v13h8V20z M37 20h5v13h-8V20z M37 33v5l-8 4h-8v-5h8"/>'),
@('past-due-service','<path d="M8 8h29 M8 40h29 M12 8v9l9 7-9 7v9 M33 8v9l-9 7 9 7v9 M16 34h13 M16 13h13"/>'),
@('monthly-service','<path d="M10 12h28v29H10z M10 21h28 M17 7v10 M31 7v10"/><path d="m16 31 5 5 11-10 M3 25v12 M43 16v12"/>'),
@('corrections-service','<path d="m10 36 21-25 7 6-21 25-9 1z M28 15l7 6 M11 35l7 6 M7 10h15 M7 18h9 M28 39h13"/>'),
@('tax-ready-service','<path d="M8 12h13l5 5h15v23H8z M8 23h33 M13 7h19v10"/><path d="m19 31 4 4 10-9"/>'),
@('bookkeeper-work','<path d="M7 10h16v30H7z M23 10h18v30H23 M12 17h6 M12 23h6 M29 17h6 M29 23h6 M12 32h6 M29 32h6"/>'),
@('reconciliation-routine','<path d="M7 14h19v27H7z M12 20h8 M12 26h8 M12 32h5"/><circle cx="33" cy="17" r="10"/><path d="m28 17 4 4 6-8 M30 31h11 M30 37h11"/>'),
@('business-expenses','<path d="M11 5h26v37l-5-3-4 3-5-3-5 3-7-3z M17 13h14 M17 21h7 M29 21h2 M17 28h7 M29 28h2"/>'),
@('tax-preparer-handoff','<path d="M9 16h14l6 6h12v18H9z M15 8h18v14 M21 3h17v19"/><path d="M16 30h17 m-5-5 5 5-5 5"/>'),
@('approve-monthly-reports','<path d="M8 6h23v15 M8 6v34h14 M14 14h11 M14 21h9 M14 28h5"/><circle cx="33" cy="32" r="11"/><path d="m27 32 4 4 9-10"/>'),
@('repair-topic','<path d="M9 8h28v31H9z M15 15h8 M15 22h6 M15 29h6"/><path d="m27 32 12-13 5 5-12 13-7 2z M37 22l5 5"/>'),
@('overdue-topic','<circle cx="24" cy="24" r="17"/><path d="M24 12v13l8 5 M7 24H3 M24 7V3 M41 24h4 M24 41v4"/>'),
@('balancing-topic','<path d="M24 6v35 M9 14h30 M12 14 5 29h14z M36 14l-7 15h14z M16 41h16"/>'),
@('year-end-topic','<path d="M6 13h36v8H6z M9 21v20h30V21 M18 27h12v6H18z M13 7h22"/><path d="m20 10 4 3 4-3"/>'),
@('tax-topic','<path d="M12 5h18l8 9v29H12z M30 5v10h8 M19 35l12-15"/><circle cx="20" cy="22" r="3"/><circle cx="30" cy="34" r="3"/>'),
@('monthly-topic','<path d="M7 12h34v29H7z M7 21h34 M15 6v11 M33 6v11 M14 28h4 M24 28h4 M14 35h4 M24 35h4"/>'),
@('categorization-topic','<rect x="5" y="6" width="15" height="15" rx="1"/><rect x="28" y="6" width="15" height="15" rx="1"/><rect x="5" y="29" width="15" height="15" rx="1"/><path d="M28 36h15 M35 29v15"/>'),
@('income-expense-topic','<path d="M11 7v32 M5 13l6-6 6 6 M37 9v32 M31 35l6 6 6-6 M21 17h7 M21 24h7 M21 31h7"/>'),
@('bank-card-topic','<path d="m5 16 19-10 19 10H5z M8 21v14 M18 21v14 M28 21v9 M5 39h20"/><rect x="27" y="28" width="19" height="14" rx="2"/><path d="M27 33h19"/>'),
@('payables-receivables-topic','<path d="M5 8h17v23H5z M27 17h16v23H27 M10 15h7 M32 24h6 M8 38h12l-4-4 M20 38l-4 4 M39 10H27l4-4 M27 10l4 4"/>'),
@('financial-reports-topic','<path d="M9 5h21l9 10v28H9z M30 5v11h9 M15 35v-8h4v8 M23 35V22h4v13 M31 35V19h3"/>'),
@('monthly-review-topic','<path d="M6 8h24v31H6z M12 15h12 M12 22h8 M12 29h5"/><circle cx="31" cy="29" r="10"/><path d="m38 36 7 8 m-18-15 3 3 5-7"/>'),
@('statement-ledger-reading','<path d="M5 7h15v32H5z M28 10h15v32H28 M9 15h7 M9 22h7 M9 29h7 M32 18h7 M32 25h7 M32 32h7 M24 5v37"/><path d="m21 8 3-3 3 3 M21 39l3 3 3-3"/>')
)
$registry=[ordered]@{}
foreach($entry in $drawings){$registry[$entry[0]]=$entry[1]}
function Icon([string]$id){if(!$registry.Contains($id)){throw "Unknown icon $id"};'<svg class="pt-icon" data-icon-id="'+$id+'" viewBox="0 0 48 48" aria-hidden="true" focusable="false">'+$registry[$id]+'</svg>'}
$header='<div class="preview-switcher" aria-label="Design previews"><span>LOCAL DESIGN PREVIEW</span><a href="verification/phase-a/home.html" data-preview="home">Home</a><a href="verification/phase-a/notes.html" data-preview="notes">Notes</a><a href="verification/phase-a/article.html" data-preview="article">Reading page</a><a href="verification/phase-a/review.html">All previews</a></div><header class="pt-header"><div class="pt-header-inner"><a class="pt-brand" href="verification/phase-a/home.html" aria-label="Paper Trail home"><img src="assets/images/paper-trail-logo.png" alt="Paper Trail" width="2170" height="725"></a><nav class="pt-nav" aria-label="Main navigation"><a href="verification/phase-a/home.html" data-page="home">Home</a><a href="services.html">Services</a><a href="verification/phase-a/notes.html" data-page="notes">Notes</a><a href="about.html">About</a><a href="areas-we-serve.html">Contact</a></nav><button class="pt-menu" aria-controls="pt-directory" aria-expanded="false">Menu <span aria-hidden="true">+</span></button></div></header>'
$nav=[regex]::Match($homeSource,'<nav[^>]*class="site-nav"[\s\S]*?</nav>').Value
$navLinks=[regex]::Matches($nav,'<a\b[^>]*href="([^"]+)"[^>]*>([\s\S]*?)</a>')
$services=foreach($m in $navLinks){if($m.Groups[1].Value -notmatch 'index.html|about.html|notes.html|blog.html|areas-we-serve.html|faq.html'){'<a href="'+$m.Groups[1].Value+'">'+$m.Groups[2].Value+'</a>'}}
$header+='<nav class="pt-directory" id="pt-directory" aria-label="All destinations" hidden><div><h2>Bookkeeping services</h2>'+($services -join '')+'</div><div><h2>Paper Trail</h2><a href="verification/phase-a/notes.html">Notes</a><a href="blog.html">Blog</a><a href="about.html">About Paper Trail</a><a href="faq.html">Working With Paper Trail</a><a href="areas-we-serve.html">Nationwide - Based in Los Angeles</a></div></nav>'
$footer='<footer class="pt-footer"><a href="verification/phase-a/home.html"><img src="assets/images/paper-trail-logo.png" alt="Paper Trail" width="2170" height="725"></a><p>Remote bookkeeping nationwide.<br>In person throughout LA County, by appointment only.</p><nav aria-label="Footer"><a href="services.html">Services</a><a href="verification/phase-a/notes.html">Notes</a><a href="areas-we-serve.html">Contact Us</a></nav></footer>'
function Page([string]$title,[string]$body,[string]$kind,[bool]$chat=$false){
$end='<script defer src="verification/phase-a/revision.js"></script>'
if($chat){$end='<script src="verification/phase-a/preview-safety.js"></script><script defer src="assets/site.js"></script>'+$end}
'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><base href="../../"><title>'+ $title +' | Paper Trail design preview</title><link rel="stylesheet" href="assets/site.css"><link rel="stylesheet" href="assets/presentation.css"><link rel="stylesheet" href="verification/phase-a/revision.css"></head><body class="pt-preview '+$kind+'">'+$header+$body+$footer+$end+'</body></html>'
}
$homeMain=[regex]::Match($homeSource,'<main\b[\s\S]*?</main>').Value
$iconIds=@('organized-records','informed-decisions','ongoing-support','bookkeeper-work','reconciliation-routine','business-expenses','tax-preparer-handoff','approve-monthly-reports')
$script:iconAt=0
$homeMain=[regex]::Replace($homeMain,'<svg\b[\s\S]*?</svg>',[Text.RegularExpressions.MatchEvaluator]{param($m) $id=$iconIds[$script:iconAt];$script:iconAt++;Icon $id})
$serviceIcons=@('past-due-service','monthly-service','corrections-service','tax-ready-service')
$script:serviceAt=0
$homeMain=[regex]::Replace($homeMain,'(<a class="service-card"[\s\S]*?<div class="home-card-copy">)',[Text.RegularExpressions.MatchEvaluator]{param($m) $s=$m.Value+(Icon $serviceIcons[$script:serviceAt]);$script:serviceAt++;$s})
$homeMain=$homeMain.Replace('href="notes.html"','href="verification/phase-a/notes.html"')
$homeMain=$homeMain.Replace('class="chat-footer"','class="chat-footer"').Replace('<div class="chat-footer">','<div class="chat-footer"><p class="preview-send-note">Design preview: sending is disabled. Your note will not be submitted.</p>')
Page 'Home' $homeMain 'pt-home' $true | Set-Content (Join-Path $out 'home.html') -Encoding UTF8
$topicData=@(
@('repair-topic','assets/images/paper-trail-services-html.webp'),@('overdue-topic','assets/photos/past-due-bookkeeping-html.webp'),@('balancing-topic','assets/photos/balancing-corrections-html.webp'),@('year-end-topic','assets/photos/year-end-bookkeeping-html.webp'),@('tax-topic','assets/photos/tax-ready-bookkeeping-html.webp'),@('monthly-topic','assets/images/paper-trail-monthly-bookkeeping-html.webp'),@('categorization-topic','assets/photos/transaction-categorization-html.webp'),@('income-expense-topic','assets/photos/income-expense-tracking-html.webp'),@('bank-card-topic','assets/photos/bank-credit-card-balancing-html.webp'),@('payables-receivables-topic','assets/photos/accounts-payable-receivable-html.webp'),@('financial-reports-topic','assets/photos/monthly-financial-reports-html.webp'),@('monthly-review-topic','assets/photos/monthly-bookkeeping-review-html.webp'))
$topics=[regex]::Matches($notesSource,'<a class="notes-topic-card" href="([^"]+)"[\s\S]*?<h2>(.*?)</h2>[\s\S]*?</a>')
$cards=for($i=0;$i -lt $topics.Count;$i++){$topic=$topics[$i];$photo=$topicData[$i][1];if(!(Test-Path (Join-Path $root $photo))){throw "Missing photo $photo"};'<a class="ritual-card" href="'+$topic.Groups[1].Value+'"><img src="'+$photo+'" alt="" loading="lazy" decoding="async"><div class="ritual-copy">'+(Icon $topicData[$i][0])+'<h2>'+ $topic.Groups[2].Value+'</h2><span>Read About '+$topic.Groups[2].Value+'</span></div></a>'}
$notesBody='<main id="main"><header class="pt-notes-opening"><div><p class="pt-kicker">The Paper Trail notebook</p><h1>Notes</h1></div><p>Practical guides to catching up your books, tracking business money and understanding your monthly reports.</p></header><section class="ritual-grid" aria-label="Bookkeeping topics">'+($cards -join '')+'</section><p class="reading-sample"><a href="verification/phase-a/article.html">View the redesigned reading-page sample: Bank Reconciliation When Your Books Do Not Match</a></p></main>'
Page 'Notes' $notesBody 'pt-notes' | Set-Content (Join-Path $out 'notes.html') -Encoding UTF8
$title=[regex]::Match($articleSource,'<h1[^>]*>(.*?)</h1>').Groups[1].Value
$summary=[regex]::Match($articleSource,'<p class="summary">([\s\S]*?)</p>').Groups[1].Value
$content=[regex]::Match($articleSource,'<article class="article-content">([\s\S]*?)</article>').Groups[1].Value
if(!$content){throw 'Article content missing'}
$articleBody='<main id="main"><nav class="pt-reading-nav" aria-label="Notes navigation"><a href="verification/phase-a/notes.html">Notes</a><span aria-hidden="true">/</span><a href="balancing-and-corrections-questions.html">Balancing &amp; Corrections</a></nav><header class="pt-reading-photo"><img src="assets/photos/why-does-my-bank-balance-not-match-my-books-html.webp" alt="Bank and credit card statements being compared with bookkeeping records"><div>'+(Icon 'statement-ledger-reading')+'<h1>'+$title+'</h1></div></header><div class="pt-reading-body"><p class="pt-reading-summary">'+$summary+'</p>'+$content+'</div></main>'
Page $title $articleBody 'pt-reading' | Set-Content (Join-Path $out 'article.html') -Encoding UTF8
$registry|ConvertTo-Json -Depth 5|Set-Content (Join-Path $out 'icon-registry.json') -Encoding UTF8
@{revision=2;uniqueCustomIcons=$registry.Count;homeBenefitIcons=3;homeServiceCards=4;homeNotesCards=5;notesTopics=12;base='relative ../../; compatible with file and HTTP';articleBodyPreserved=$true;originalHomeVideoMarkupPreserved=$true;note='Visual approval prototype. Home conversation works as guided intake; all network submissions are blocked in previews. Topic links lead to their real existing pages; reading-page sample is linked explicitly.'}|ConvertTo-Json|Set-Content (Join-Path $out 'prototype-scope.json') -Encoding UTF8
'Revised pages generated.'
