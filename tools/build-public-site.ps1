param([string]$Output = '.release/public')
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot
$destination = [IO.Path]::GetFullPath((Join-Path $root $Output))
if (!$destination.StartsWith($root+[IO.Path]::DirectorySeparatorChar)) {throw 'Build output must be inside the repository.'}
if (Test-Path $destination) {throw 'Build output already exists. Use a fresh output directory.'}
New-Item -ItemType Directory -Path $destination -Force | Out-Null
# Explicit allowlist: working documents, scripts and verification never enter Pages.
Get-ChildItem $root -File | Where-Object {$_.Extension -in @('.html','.svg') -or $_.Name -in @('CNAME','robots.txt','sitemap.xml','sitemap-translations.xml')} | Copy-Item -Destination $destination
foreach ($folder in @('assets','state-records','ar','es','fa','hy','ko','ru','te','tl','zh-CN')) {
    Copy-Item -LiteralPath (Join-Path $root $folder) -Destination $destination -Recurse
}
# Reject unexpected file types in the copied browser resources.
Get-ChildItem $destination -File -Recurse | Where-Object {$_.Extension -notin @('.html','.svg','.css','.js','.json','.png','.jpg','.jpeg','.webp','.gif','.ico','.woff','.woff2','.ttf','.otf','.mp4','.webm','.xml','.txt') -and $_.Name -ne 'CNAME'} | ForEach-Object {throw ('Unexpected public asset: '+$_.FullName)}
[IO.File]::WriteAllText((Join-Path $destination '.nojekyll'),'')
Write-Output $destination
