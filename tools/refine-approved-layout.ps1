$ErrorActionPreference='Stop'
$p=Join-Path (Get-Location) 'tools/preview-direction-4.ps1'
$s=[IO.File]::ReadAllText($p)
$s=$s.Replace('income, expenses and account balances.','income, expenses, and account balances.')
$s=$s.Replace('<button class="action" type="button" data-open-chat data-i18n="start">Get started</button>','')
$repair=@'
(Label 'catchUp' 'Catch up overdue books')+'<span class="hero-service-action" data-i18n="viewRepair">View repair</span>'
'@
$monthly=@'
(Label 'keepCurrent' 'Keep monthly records current')+'<span class="hero-service-action" data-i18n="viewMonthly">View monthly</span>'
'@
$s=$s.Replace("(Label 'catchUp' 'Catch up overdue books')",$repair)
$s=$s.Replace("(Label 'keepCurrent' 'Keep monthly records current')",$monthly)
$s=$s.Replace('<section class="home-about" id="about"><div class="section-label"><h2 data-i18n="about">About</h2></div><div class="about-content">','<section class="home-about" id="about"><div class="about-content">')
$s=$s.Replace('<div><p data-i18n="aboutBody">','<div><h2 class="about-text-title" data-i18n="about">About</h2><p data-i18n="aboutBody">')
$s=$s.Replace('href="verification/phase-a/areas-we-serve.html#cities"','href="verification/phase-a/areas-we-serve.html"')
$contactOld=@'
+$globe+'</div><section id="cities"><h2>Based in Los Angeles</h2><div class="contact-cities">'
'@
$contactNew=@'
+$globe+'</div>'
'@
$s=$s.Replace($contactOld,$contactNew)
$s=[regex]::Replace($s,'(?m)^foreach\(\$city in \$cityLinks\)\{\$contactBody\+=.*?\}\s*$','')
$s=$s.Replace("`$contactBody+='</div></section></main>'","`$contactBody+='</main>'")
[IO.File]::WriteAllText($p,$s,[Text.UTF8Encoding]::new($true))
