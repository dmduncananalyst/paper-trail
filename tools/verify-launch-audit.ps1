param([string]$Public='.release/verified', [string]$Report=(Join-Path $env:TEMP 'paper-trail-production-verification.json'))
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot
$publicRoot=[IO.Path]::GetFullPath((Join-Path $root $Public))
if(!$publicRoot.StartsWith($root+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Public build must be inside Paper Trail.'}
if(!(Test-Path -LiteralPath $publicRoot -PathType Container)){throw 'Public build does not exist.'}
$reportPath=[IO.Path]::GetFullPath($Report)
if($reportPath.StartsWith($root+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Verification reports must remain outside the repository and public build.'}
$errors=New-Object 'Collections.Generic.List[string]'
$languages=@('es','fa','hy','zh-CN','ko','tl','te','ru','ar')
# Approved English and saved localized routes are independent inventories.
# New English content must not imply permission to generate translated pages.
$inventory=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'production-pages.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$sourcePages=@(Get-ChildItem -LiteralPath $root -Filter '*.html' -File)
$sourcePages+=@(Get-ChildItem -LiteralPath (Join-Path $root 'state-records') -Filter '*.html' -File)
$actualEnglish=@($sourcePages|ForEach-Object {$_.FullName.Substring($root.Length+1).Replace('\','/')})
if(@(Compare-Object @($inventory.english) $actualEnglish).Count){$errors.Add('Approved English source inventory mismatch')}
$expectedPages=New-Object 'Collections.Generic.HashSet[string]' ([StringComparer]::Ordinal)
foreach($name in $inventory.english){[void]$expectedPages.Add($name)}
foreach($language in $languages){foreach($name in $inventory.locales.$language){[void]$expectedPages.Add($language+'/'+$name)}}
$withoutChat=@('packages.html','request-a-custom-quote.html','enterprise-monthly-bookkeeping-quote.html','enterprise-accounts-billing-quote.html','bookkeeping-repair-quote.html')
$pages=@(Get-ChildItem $publicRoot -Filter '*.html' -Recurse)
$files=New-Object 'Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
Get-ChildItem $publicRoot -Recurse -Force | ForEach-Object {
 [void]$files.Add($_.FullName)
 $path=$_.FullName.Substring($publicRoot.Length+1).Replace('\','/')
 if($_.Attributes -band [IO.FileAttributes]::ReparsePoint){$errors.Add('Public reparse point: '+$path)}
 if($path -match '(^|/)(\.git|\.github|\.translation-cache|\.release|verification|tools|browser-profile[^/]*|chrome-profile[^/]*|user-data|__pycache__)(/|$)' -or
    $_.Name -match '^\.env(?:\.|$)|^(Cookies|Login Data|Web Data|Local State|credentials\.json|tokens\.json)$|\.(sqlite3?|db|pem|key|log|pyc|ps1|py)$'){$errors.Add('Private public-build path: '+$path)}
}
$urls=New-Object 'Collections.Generic.HashSet[string]'
foreach($map in @('sitemap.xml','sitemap-translations.xml')){
 [xml]$xml=[IO.File]::ReadAllText((Join-Path $publicRoot $map))
 foreach($node in $xml.urlset.url){if(!$urls.Add([string]$node.loc)){$errors.Add('Duplicate sitemap URL: '+$node.loc)}}
}
foreach($locale in @('')+$languages){
 $contact='https://www.papertrailusa.com/'+$(if($locale){$locale+'/'}else{''})+'areas-we-serve.html'
 if(!$urls.Contains($contact)){$errors.Add('Missing Contact Us sitemap URL: '+$contact)}
}
$references=0;$chats=0
foreach($page in $pages){
 $html=[IO.File]::ReadAllText($page.FullName)
 $relative=$page.FullName.Substring($publicRoot.Length+1).Replace('\','/')
 if(!$expectedPages.Contains($relative)){$errors.Add('Unapproved public page: '+$relative)}
 $sourceName=$relative;$locale='en'
 if($relative -match '^([^/]+)/(.*)$' -and $languages -ccontains $Matches[1]){$locale=$Matches[1];$sourceName=$Matches[2]}
 $htmlTag=[regex]::Match($html,'<html\b[^>]*>').Value
 $lang=[regex]::Match($htmlTag,'\blang="([^"]+)"').Groups[1].Value
 $staticLocale=[regex]::Match($htmlTag,'\bdata-static-locale="([^"]+)"').Groups[1].Value
 if($locale -eq 'en'){
  if($lang -cne 'en' -or $staticLocale -or $html -match 'x-mtfrom-en'){$errors.Add('Invalid English language metadata: '+$relative)}
 }elseif(($lang -cne $locale -and $lang -cne ($locale+'-x-mtfrom-en')) -or $staticLocale -cne $locale){$errors.Add('Localized language/route mismatch: '+$relative)}
 if($html -notmatch '<title>.+?</title>' -or $html -notmatch 'name="viewport"'){$errors.Add('Missing page metadata: '+$relative)}
 $url='https://www.papertrailusa.com/'+$relative
 # Existing noindex state pages are legitimate build dependencies, not indexable translations.
 $noindex=$html -match '<meta\b[^>]*name="robots"[^>]*content="[^"]*\bnoindex\b'
 if(!$noindex -and !$urls.Contains($url) -and !($relative -eq 'index.html' -and $urls.Contains('https://www.papertrailusa.com/'))){$errors.Add('Missing sitemap page: '+$relative)}
 $canonical=[regex]::Match($html,'<link\b[^>]*rel="canonical"[^>]*href="([^"]+)"').Groups[1].Value
 if($canonical -cne $url -and !($relative -eq 'index.html' -and $canonical -ceq 'https://www.papertrailusa.com/')){$errors.Add('Canonical mismatch: '+$relative)}
 # Citation sections are restricted to individual educational/blog articles.
 $individualArticle=$html -match '"@type"\s*:\s*"(Article|BlogPosting|NewsArticle|TechArticle)"' -or $html -match '<article\b[^>]*class="[^"]*(reading-feature|article-body|aeo-article)'
 if(!$individualArticle -and $html -match '<(section|aside|div)\b[^>]*class="[^"]*\b(references|sources|source-reference-links)\b'){$errors.Add('Inappropriate source/resource section: '+$relative)}
 if($sourceName -eq 'paper-trail-monthly-bookkeeping.html' -and $html -match '<a\b[^>]*href="[^"]*#monthly-bookkeeping-service-inclusions'){$errors.Add('Unwanted service inclusions jump link: '+$relative)}
 $clarityCount=[regex]::Matches($html,'https://(?:www\.)?clarity\.ms/tag/').Count
 if($clarityCount -ne 1 -or !$html.Contains('"z32dbrhlki"')){$errors.Add('Clarity initialization mismatch: '+$relative)}
 $configs=[regex]::Matches($html,'<script type="application/json" id="conversation-data">([\s\S]*?)</script>')
 $expectedConfigs=if($sourceName -match '^state-records/' -or $withoutChat -ccontains $sourceName){0}else{1}
 if($configs.Count -ne $expectedConfigs){$errors.Add('Chat config count: '+$relative)}elseif($configs.Count){
  $chats++;$config=$configs[0].Groups[1].Value | ConvertFrom-Json
  if($html -notmatch 'id="conversation-dialog"' -or $html -notmatch 'data-open-chat'){$errors.Add('Missing chat UI: '+$relative)}
 }
 $base=if($html -match '<base href="([^"]+)"'){[IO.Path]::GetFullPath((Join-Path $page.DirectoryName $Matches[1]))}else{$page.DirectoryName}
 foreach($match in [regex]::Matches(($html -replace '<base[^>]*>',''),'(?:href|src)="([^"#]+)"')){
  $ref=[Net.WebUtility]::HtmlDecode($match.Groups[1].Value).Split('#')[0].Split('?')[0]
  if(!$ref -or $ref -match '^(?:[a-z]+:|//)'){continue}
  $references++
  $target=if($ref.StartsWith('/')){Join-Path $publicRoot $ref.TrimStart('/')}else{Join-Path $base ([Uri]::UnescapeDataString($ref))}
  $resolvedTarget=[IO.Path]::GetFullPath($target)
  if(!$resolvedTarget.StartsWith($publicRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase) -and $resolvedTarget -cne $publicRoot){$errors.Add('Reference escapes public build: '+$relative+' -> '+$ref)}
  elseif(!$files.Contains($resolvedTarget)){$errors.Add('Broken reference: '+$relative+' -> '+$ref)}
 }
 if($relative -match 'state-records/' -and $html -match 'href="http://'){$errors.Add('Insecure state source: '+$relative)}
}
foreach($private in @('tools','verification','START_HERE.txt','Paper-Trail-Master-Website-Instructions.md','paper-trail-launch-audit-2026-10-18.md')){if(Test-Path (Join-Path $publicRoot $private)){$errors.Add('Private build content: '+$private)}}
foreach($expected in $expectedPages){if(!$files.Contains((Join-Path $publicRoot $expected))){$errors.Add('Missing approved page: '+$expected)}}
if($pages.Count -ne $expectedPages.Count){$errors.Add('Unexpected page count: '+$pages.Count)}
$result=@{pages=$pages.Count;expectedPages=$expectedPages.Count;languages=@('en')+$languages;chats=$chats;sitemapUrls=$urls.Count;internalReferences=$references;errors=@($errors.ToArray())}
$result | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $reportPath -Encoding UTF8
$result | ConvertTo-Json -Depth 5
if($errors.Count){throw 'Launch verification failed'}
