$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
$root=Split-Path $PSScriptRoot
$out=Join-Path $root 'verification/articles-20261113'
$sources=(Get-Content -LiteralPath (Join-Path $out 'image-generation.json') -Raw -Encoding UTF8|ConvertFrom-Json).images
$articles=Get-Content -LiteralPath (Join-Path $out 'approved-content.json') -Raw -Encoding UTF8|ConvertFrom-Json
$codec=[Drawing.Imaging.ImageCodecInfo]::GetImageEncoders()|Where-Object MimeType -eq 'image/jpeg'
$parameters=New-Object Drawing.Imaging.EncoderParameters 1
$parameters.Param[0]=New-Object Drawing.Imaging.EncoderParameter ([Drawing.Imaging.Encoder]::Quality),([long]85)
$report=@()
for($i=0;$i -lt $articles.Count;$i++){
 $source=$sources[$i].source
 $destination=Join-Path $root $articles[$i].image
 $image=[Drawing.Image]::FromFile($source)
 try{
  if($image.Width -ne 1448 -or $image.Height -ne 1086){throw 'Unexpected generated image dimensions'}
  $image.Save($destination,$codec,$parameters)
  $report+=@{article=$articles[$i].slug;image=$articles[$i].image;width=$image.Width;height=$image.Height;bytes=(Get-Item -LiteralPath $destination).Length;sha256=(Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLower();mode='built-in image_gen; JPEG quality 85';alt=$articles[$i].alt}
 }finally{$image.Dispose()}
}
$parameters.Dispose()
[IO.File]::WriteAllText((Join-Path $out 'image-provenance.json'),($report|ConvertTo-Json -Depth 5),[Text.UTF8Encoding]::new($false))
$report|Select-Object article,bytes,width,height
