$ErrorActionPreference='Stop'
$root=(Get-Location).Path
$archive=Join-Path $root 'verification/phase-a/snapshots/before-latest-feedback'
New-Item -ItemType Directory -Force -Path $archive | Out-Null
foreach($name in @('home.html','notes.html','blog.html','article.html','direction-4.css','direction-4.js')){if(!(Test-Path (Join-Path $archive $name))){Copy-Item -LiteralPath (Join-Path $root ('verification/phase-a/'+$name)) -Destination (Join-Path $archive $name)}}
$p=Join-Path $root 'tools/preview-direction-4.ps1'
$s=[IO.File]::ReadAllText($p)
$old='<div class="nav-family"><a href="areas-we-serve.html" aria-haspopup="true" aria-expanded="false" data-i18n="contact">Contact Us</a><div class="nav-panel"><a href="areas-we-serve.html" data-i18n="contact">Contact Us</a><a href="faq.html" data-i18n="working">Working With Paper Trail</a><a href="verification/phase-a/blog.html" data-i18n="blog">Blog</a><a href="services.html" data-i18n="allServices">All Services</a></div></div>'
$new='<a href="verification/phase-a/blog.html" data-i18n="blog">Blog</a><a href="verification/phase-a/areas-we-serve.html" data-i18n="contact">Contact Us</a>'
if(!$s.Contains($old)){throw 'Contact menu source did not match'}
$s=$s.Replace($old,$new)
$s=$s.Replace('<p data-i18n="location">Nationwide – Based in Los Angeles.</p>','<a class="footer-location" href="verification/phase-a/areas-we-serve.html#cities" data-i18n="location">Nationwide – Based in Los Angeles.</a>')
$s=$s.Replace('<nav aria-label="Footer"><a href="services.html" data-i18n="services">Services</a><a href="verification/phase-a/notes.html" data-i18n="notes">Notes</a><a href="areas-we-serve.html" data-i18n="contact">Contact Us</a></nav>','<nav aria-label="Footer"><a href="verification/phase-a/notes.html" data-i18n="notes">Notes</a><a href="services.html" data-i18n="services">Services</a><a href="verification/phase-a/areas-we-serve.html" data-i18n="contact">Contact Us</a></nav>')
$s=$s.Replace('data-i18n="bookkeep">Bookkeep with Paper Trail','data-i18n="start">Get started')
$s=$s.Replace('</h1><button class="action" type="button" data-open-chat data-i18n="start">','</h1><p class="hero-description" data-i18n="heroDescription">From overdue records to monthly reports, we help you keep track of income, expenses and account balances.</p><button class="action" type="button" data-open-chat data-i18n="start">')
$s=$s.Replace("(Label 'repair' 'Bookkeeping Repair')","(Label 'catchUp' 'Catch up overdue books')").Replace("(Label 'monthly' 'Monthly Bookkeeping')","(Label 'keepCurrent' 'Keep monthly records current')")
$s=$s.Replace('<button type="button" data-open-chat>''+(Label ''talk'' ''Talk with Paper Trail'')+''</button>','')
$start=$s.IndexOf(" $content='<main")
# Locate the actual literal variable name, without PowerShell interpolation.
$start=$s.IndexOf(' $content=''<main')
$end=$s.IndexOf(' $page=Page',$start)
$reading=@'
 $content='<main id="main"><article class="reading-feature"><header class="reading-masthead"><img src="'+$photo+'" alt="Bookkeeping records related to this note" loading="eager"><h1>'+$title+'</h1></header><div class="reading-column"><p class="reading-lead">'+$summary+'</p><div class="reading-spread">'+$body+'</div></div></article><div class="reading-actions"><a class="action" href="verification/phase-a/notes.html">Notes</a><a class="action quiet" href="verification/phase-a/blog.html">Blog</a></div></main>'
'@
if($start -lt 0 -or $end -lt 0){throw 'Reading template source missing'}
$s=$s.Substring(0,$start)+$reading+"`r`n"+$s.Substring($end)
$footerEnd=$s.IndexOf('function Page(')
$extension=@'
$areaSource=ReadSite 'areas-we-serve.html'
$cityLinks=[regex]::Matches($areaSource,'<a class="photo-card"[^>]*href="(bookkeeping-[^"]+)"[\s\S]*?<h3>(.*?)</h3>')
$cityNav='<nav class="footer-cities" aria-label="Los Angeles County cities">'
foreach($city in $cityLinks){$cityNav+='<a href="'+$city.Groups[1].Value+'">'+$city.Groups[2].Value+'</a>'}
$cityNav+='</nav>'
$footer=$footer.Replace('<div class="footer-bottom">',$cityNav+'<div class="footer-bottom">')
'@
$s=$s.Insert($footerEnd,$extension+"`r`n")
# Create a contact preview from existing site information and the existing globe.
$contactBuild=@'
$globe=[regex]::Match($areaSource,'<figure class="nationwide-globe">[\s\S]*?</figure>').Value
$contactBody='<main id="main" class="contact-main"><h1>Contact Us – Nationwide</h1><div class="contact-intro"><div><p>Remote bookkeeping nationwide over Zoom. In-person meetings throughout Los Angeles County, by appointment only.</p><div class="contact-methods"><a href="tel:+18189340444">818-934-0444</a><button type="button" data-email aria-haspopup="dialog">bookkeeping@papertrailusa.com</button></div><a class="action quiet" href="faq.html">Working With Paper Trail</a></div>'+$globe+'</div><section id="cities"><h2>Based in Los Angeles</h2><div class="contact-cities">'
foreach($city in $cityLinks){$contactBody+='<a class="action quiet" href="'+$city.Groups[1].Value+'">'+$city.Groups[2].Value+'</a>'}
$contactBody+='</div></section></main>'
SavePreview 'areas-we-serve.html' (Page 'Contact Us – Nationwide' $contactBody 'pt-contact')
'@
$insertAt=$s.IndexOf('$preserved=@()')
$s=$s.Insert($insertAt,$contactBuild+"`r`n")
[IO.File]::WriteAllText($p,$s,[Text.UTF8Encoding]::new($true))
