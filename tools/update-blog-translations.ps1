param([switch]$Inventory)
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
$pythonPath=Join-Path $root '../sun-and-sage/.tools/python/python.exe'
if(!(Test-Path -LiteralPath $pythonPath)){
 $pythonCommand=Get-Command python -ErrorAction SilentlyContinue
 if(!$pythonCommand){throw 'Python with google-auth and requests is required for the existing Google connection.'}
 $pythonPath=$pythonCommand.Source
}
$env:PYTHONDONTWRITEBYTECODE='1'
$arguments=@((Join-Path $PSScriptRoot 'sync-blog-translations.py'))
if(!$Inventory){$arguments+='--refresh'}
& $pythonPath @arguments
if($LASTEXITCODE -ne 0){throw 'Blog translations are incomplete. Saved results are retained; inspect the reported failure before retrying.'}
