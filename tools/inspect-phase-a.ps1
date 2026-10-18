$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
$out=Join-Path $root 'verification/phase-a'
$pages=@(Get-ChildItem $root -Filter '*.html')
$all=@{}; foreach($p in $pages){$all[$p.Name]=[IO.File]::ReadAllText($p.FullName)}
$photos=@(foreach($f in Get-ChildItem (Join-Path $root 'assets') -Recurse -File | Where-Object Extension -In '.webp','.png'){
$b=[IO.File]::ReadAllBytes($f.FullName); $w=0; $h=0
if($f.Extension -eq '.webp'){$k=[Text.Encoding]::ASCII.GetString($b,12,4); if($k -eq 'VP8X'){$w=1+$b[24]+256*$b[25]+65536*$b[26];$h=1+$b[27]+256*$b[28]+65536*$b[29]} elseif($k -eq 'VP8 '){$w=[BitConverter]::ToUInt16($b,26)-band 16383;$h=[BitConverter]::ToUInt16($b,28)-band 16383} elseif($k -eq 'VP8L'){$n=[BitConverter]::ToUInt32($b,21);$w=1+($n-band 16383);$h=1+(($n-shr 14)-band 16383)}}
elseif($f.Extension -eq '.png'){$a=$b[16..19];[Array]::Reverse($a);$w=[BitConverter]::ToUInt32($a,0);$a=$b[20..23];[Array]::Reverse($a);$h=[BitConverter]::ToUInt32($a,0)}
$path=$f.FullName.Substring($root.Length+1).Replace('\','/');$used=@($pages|Where-Object {$all[$_.Name].Contains($path)}|ForEach-Object Name)
[pscustomobject]@{path=$path;width=$w;height=$h;bytes=$f.Length;usedBy=($used -join ';')}
})
$photos|Export-Csv (Join-Path $out 'photo-inventory.csv') -NoTypeInformation -Encoding UTF8
$videos=@(foreach($p in $pages){foreach($m in [regex]::Matches($all[$p.Name],'<video\b[\s\S]*?</video>')){[pscustomobject]@{page=$p.Name;markup=$m.Value}}})
$videos|ConvertTo-Json -Depth 5|Set-Content (Join-Path $out 'video-baseline.json') -Encoding UTF8
$heads=@(foreach($p in $pages){$m=[regex]::Matches($all[$p.Name],'<h1\b[^>]*>([\s\S]*?)</h1>');[pscustomobject]@{page=$p.Name;count=$m.Count;title=(($m|ForEach-Object {[Net.WebUtility]::HtmlDecode(($_.Groups[1].Value -replace '<[^>]+>',' '))})-join '; ')}})
$heads|Export-Csv (Join-Path $out 'headings.csv') -NoTypeInformation -Encoding UTF8
@(Get-ChildItem $root -File;Get-ChildItem (Join-Path $root 'assets') -Recurse -File)|Get-FileHash|Select-Object Path,Hash|Export-Csv (Join-Path $out 'source-baseline.csv') -NoTypeInformation -Encoding UTF8
[ordered]@{pages=$pages.Count;photos=$photos.Count;dimensions=@($photos|Group-Object width,height|Select-Object Name,Count);unusedPhotos=@($photos|Where-Object usedBy -EQ ''|ForEach-Object path);videoPages=@($videos|ForEach-Object page);headingErrors=@($heads|Where-Object count -NE 1)}|ConvertTo-Json -Depth 6|Set-Content (Join-Path $out 'inspection.json') -Encoding UTF8
for($i=0;$i -lt $photos.Count;$i+=36){$cards=$photos[$i..([math]::Min($i+35,$photos.Count-1))]|ForEach-Object {'<figure><img src="../../'+$_.path+'"><figcaption>'+[Net.WebUtility]::HtmlEncode($_.path)+'<br>'+$_.width+' x '+$_.height+'</figcaption></figure>'};'<!doctype html><meta charset="utf-8"><style>body{margin:20px;background:#f8f6ef;color:#193d31;font:11px Arial}main{display:grid;grid-template-columns:repeat(6,1fr);gap:12px}figure{margin:0;min-width:0}img{width:100%;height:130px;object-fit:contain}figcaption{overflow-wrap:anywhere;height:44px}</style><h1>Paper Trail photo library</h1><main>'+($cards -join '')+'</main>'|Set-Content (Join-Path $out ('library-'+($i/36)+'.html')) -Encoding UTF8}
Get-Content (Join-Path $out 'inspection.json') -Raw
