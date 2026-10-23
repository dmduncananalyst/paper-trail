param([string]$Public='.release/verified')
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot
$publicRoot=Join-Path $root $Public
$errors=New-Object 'Collections.Generic.List[string]'
$pages=@(Get-ChildItem $publicRoot -Filter '*.html' -Recurse)
$files=New-Object 'Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
Get-ChildItem $publicRoot -Recurse | ForEach-Object {[void]$files.Add($_.FullName)}
$urls=New-Object 'Collections.Generic.HashSet[string]'
foreach($map in @('sitemap.xml','sitemap-translations.xml')){
 [xml]$xml=[IO.File]::ReadAllText((Join-Path $publicRoot $map))
 foreach($node in $xml.urlset.url){if(!$urls.Add([string]$node.loc)){$errors.Add('Duplicate sitemap URL: '+$node.loc)}}
}
$references=0;$chats=0
foreach($page in $pages){
 $html=[IO.File]::ReadAllText($page.FullName)
 $relative=$page.FullName.Substring($publicRoot.Length+1).Replace('\','/')
 if($html -match 'x-mtfrom-en'){$errors.Add('Machine language marker: '+$relative)}
 if($html -notmatch '<title>.+?</title>' -or $html -notmatch 'name="viewport"'){$errors.Add('Missing page metadata: '+$relative)}
 $url='https://www.papertrailusa.com/'+$relative
 if(!$urls.Contains($url) -and !($relative -eq 'index.html' -and $urls.Contains('https://www.papertrailusa.com/'))){$errors.Add('Missing sitemap page: '+$relative)}
 $configs=[regex]::Matches($html,'<script type="application/json" id="conversation-data">([\s\S]*?)</script>')
 $expectedConfigs=if($relative -match 'state-records/'){0}else{1}
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
  if(!$files.Contains([IO.Path]::GetFullPath($target))){$errors.Add('Broken reference: '+$relative+' -> '+$ref)}
 }
 if($relative -match 'state-records/' -and $html -match 'href="http://'){$errors.Add('Insecure state source: '+$relative)}
}
foreach($private in @('tools','verification','START_HERE.txt','Paper-Trail-Master-Website-Instructions.md','paper-trail-launch-audit-2026-10-18.md')){if(Test-Path (Join-Path $publicRoot $private)){$errors.Add('Private build content: '+$private)}}
if($pages.Count -ne 2000){$errors.Add('Unexpected page count: '+$pages.Count)}
$result=@{pages=$pages.Count;chats=$chats;sitemapUrls=$urls.Count;internalReferences=$references;errors=@($errors.ToArray())}
New-Item -ItemType Directory -Force (Join-Path $root 'verification/launch-audit-20261020') | Out-Null
$result | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $root 'verification/launch-audit-20261020/static.json') -Encoding UTF8
$result | ConvertTo-Json -Depth 5
if($errors.Count){throw 'Launch verification failed'}
