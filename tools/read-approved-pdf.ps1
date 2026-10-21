$ErrorActionPreference='Stop'
$path='C:\Users\Owner\Downloads\Paper_Trail_Two_Blogs_UPDATED_PHOTO_NAMES.pdf'
$raw=[Text.Encoding]::GetEncoding(28591).GetString([IO.File]::ReadAllBytes($path))
function Decode85([string]$s){
 $out=[Collections.Generic.List[byte]]::new(); $group=[Collections.Generic.List[int]]::new()
 foreach($c in $s.Replace('~>','').ToCharArray()){
  if([char]::IsWhiteSpace($c)){continue}
  if($c -ceq 'z'){ $out.AddRange([byte[]]@(0,0,0,0));continue }
  $group.Add(([int]$c-33))
  if($group.Count -eq 5){[long]$v=0;foreach($n in $group){$v=$v*85+$n};for($i=3;$i -ge 0;$i--){$out.Add([byte](($v -shr ($i*8)) -band 255))};$group.Clear()}
 }
 if($group.Count){$count=$group.Count;while($group.Count -lt 5){$group.Add(84)};[long]$v=0;foreach($n in $group){$v=$v*85+$n};for($i=0;$i -lt $count-1;$i++){$out.Add([byte](($v -shr ((3-$i)*8)) -band 255))}}
 return ,$out.ToArray()
}
$output=[Text.StringBuilder]::new()
foreach($m in [regex]::Matches($raw,'(?s)(\d+) 0 obj\s*<<((?:(?!endobj).)*?)>>\s*stream\r?\n(.*?)\r?\nendstream')){
 $dict=$m.Groups[2].Value;if($dict -match '/Type/EmbeddedFile'){continue}
 $bytes=[Text.Encoding]::GetEncoding(28591).GetBytes($m.Groups[3].Value)
 if($dict -match 'ASCII85Decode'){$bytes=Decode85 $m.Groups[3].Value}
 if($dict -match 'FlateDecode'){
  Write-Host $m.Groups[1].Value $bytes.Length ($bytes[0..5] -join ','); $compressedInput=[IO.MemoryStream]::new($bytes,2,$bytes.Length-6)
  $deflate=[IO.Compression.DeflateStream]::new($compressedInput,[IO.Compression.CompressionMode]::Decompress)
  $ms=[IO.MemoryStream]::new();$deflate.CopyTo($ms);$bytes=$ms.ToArray();$deflate.Dispose()
 }
 $str=[Text.Encoding]::GetEncoding(1252).GetString($bytes)
 [void]$output.AppendLine(('STREAM '+$m.Groups[1].Value));[void]$output.AppendLine($str)
}
$dir='verification/approved-blogs-20261020';New-Item -ItemType Directory -Force $dir|Out-Null
[IO.File]::WriteAllText((Join-Path (Get-Location) "$dir/pdf-streams.txt"),$output.ToString(),[Text.UTF8Encoding]::new($false))
Write-Output $output.ToString()
