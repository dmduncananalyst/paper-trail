param([int]$Port=8765)
$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../.release/verified'))
$listener=New-Object Net.HttpListener
$listener.Prefixes.Add("http://localhost:$Port/")
$listener.Prefixes.Add("http://127.0.0.1:$Port/")
$listener.Start()
try {while($listener.IsListening){
 $context=$listener.GetContext()
 $relative=[Uri]::UnescapeDataString($context.Request.Url.AbsolutePath).TrimStart('/')
 if(!$relative){$relative='index.html'}
 $path=[IO.Path]::GetFullPath((Join-Path $root $relative))
 if($path.StartsWith($root+[IO.Path]::DirectorySeparatorChar) -and [IO.File]::Exists($path)){
  $types=@{'.html'='text/html; charset=utf-8';'.js'='text/javascript';'.css'='text/css';'.json'='application/json';'.svg'='image/svg+xml';'.webp'='image/webp';'.png'='image/png';'.mp4'='video/mp4'}
  $context.Response.ContentType=$types[[IO.Path]::GetExtension($path)]
  $bytes=[IO.File]::ReadAllBytes($path);$context.Response.ContentLength64=$bytes.Length
  try{$context.Response.OutputStream.Write($bytes,0,$bytes.Length)}catch{}
 }else{$context.Response.StatusCode=404}
 $context.Response.Close()
}}finally{$listener.Stop()}
