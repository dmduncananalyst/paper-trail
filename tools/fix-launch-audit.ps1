$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot
$utf8 = New-Object Text.UTF8Encoding $false
$languages = @('en','ar','es','fa','hy','ko','ru','te','tl','zh-CN')
$missing = @('tax-ready-bookkeeping-records.html','profit-vs-cash-flow-business-money.html','nationwide-bookkeeping.html','los-angeles-county.html','catch-up-bookkeeping-overdue-books.html')
foreach ($language in $languages) {
    $folder = if ($language -eq 'en') {$root} else {Join-Path $root $language}
    $donor = [IO.File]::ReadAllText((Join-Path $folder 'index.html'))
    $dialog = [regex]::Match($donor,'<dialog[^>]*conversation-dialog[\s\S]*?</dialog>').Value
    $opener = [regex]::Match($donor,'<section class="home-conversation">[\s\S]*?</section>').Value
    $data = [regex]::Match($donor,'<script type="application/json" id="conversation-data">([\s\S]*?)</script>').Groups[1].Value
    foreach ($name in $missing) {
        $path = Join-Path $folder $name
        $html = [IO.File]::ReadAllText($path)
        if ($html.Contains('id="conversation-data"')) {continue}
        $config = $data | ConvertFrom-Json
        $config.page = $name
        $config.topic = [Net.WebUtility]::HtmlDecode([regex]::Match($html,'<title>(.*?)</title>').Groups[1].Value)
        $markup = $opener + $dialog + '<script type="application/json" id="conversation-data">' + ($config | ConvertTo-Json -Depth 30 -Compress) + '</script>'
        $html = $html.Replace('</main>', $markup+'</main>')
        [IO.File]::WriteAllText($path,$html,$utf8)
    }
    $pages = @(Get-ChildItem $folder -Filter '*.html') + @(Get-ChildItem (Join-Path $folder 'state-records') -Filter '*.html')
    $pages | ForEach-Object {
        $html = [IO.File]::ReadAllText($_.FullName)
        $updated = $html -replace '(lang="[a-zA-Z-]+)-x-mtfrom-en"','$1"'
        $updated = $updated -replace '(href="|"url":\s*")http://','$1https://'
        $updated = $updated.Replace('https://www.revenue.ne.gov/sites/revenue.nebraska.gov/files/doc/legal/regs/1-008.pdf','https://revenue.nebraska.gov/sites/default/files/doc/legal/regs/1-008.pdf')
        if ($updated -cne $html) {[IO.File]::WriteAllText($_.FullName,$updated,$utf8)}
    }
}
foreach ($name in @('sitemap.xml','sitemap-translations.xml')) {
    $path = Join-Path $root $name
    $xml = [IO.File]::ReadAllText($path)
    $add = @()
    foreach ($language in $languages) {
        if (($name -eq 'sitemap.xml') -ne ($language -eq 'en')) {continue}
        $prefix = if ($language -eq 'en') {''} else {$language+'/'}
        Get-ChildItem (Join-Path $root ($prefix+'state-records')) -Filter '*.html' | Sort-Object Name | ForEach-Object {
            $url = 'https://www.papertrailusa.com/'+$prefix+'state-records/'+$_.Name
            if (!$xml.Contains('<loc>'+$url+'</loc>')) {$add += '  <url><loc>'+$url+'</loc></url>'}
        }
    }
    if ($add.Count) {[IO.File]::WriteAllText($path,$xml.Replace('</urlset>',($add -join "`n")+"`n</urlset>"),$utf8)}
}
