from pathlib import Path
p=Path('tools/localized-phone-digits-qa.ps1');s=p.read_text(encoding='utf-8-sig');a=s.index(' $digits=switch');b=s.index(" $r=Cdp 'Runtime.evaluate'",a)
s=s[:a]+''' $offset=switch($code){'fa'{1776}'ar'{1632}'te'{3174}'zh-CN'{65296}}
 $flow=[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'localized-chat-eval.js')).Replace("answer('8185550123')",("answer(String.fromCharCode(...[8,1,8,5,5,5,0,1,2,3].map(n=>"+$offset+"+n)))"))
'''+s[b:];p.write_text(s,encoding='utf-8-sig')
