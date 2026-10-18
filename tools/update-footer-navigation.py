"""Update only the footer's primary row in English source pages."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
links=[('index.html','home','Home'),('about.html','about','About'),('services.html','services','Services'),('notes.html','notes','Notes'),('nationwide-bookkeeping.html',None,'Nationwide')]
nav='<nav aria-label="Footer">'+''.join('<a href="'+url+'"'+(' data-i18n="'+key+'"' if key else '')+'>'+text+'</a>' for url,key,text in links)+'</nav>'
primary='<div class="footer-primary">'+nav+'<div class="footer-contact"><a href="tel:+18189340444">818-934-0444</a><button type="button" data-email aria-haspopup="dialog">bookkeeping@papertrailusa.com</button></div></div>'
count=0
for p in [*root.glob('*.html'),*(root/'state-records').glob('*.html')]:
 s=p.read_text(encoding='utf-8')
 updated,n=re.subn(r'(<footer class="pt-footer">).*?(<nav class="footer-cities")',lambda m:m[1]+primary+m[2],s,count=1,flags=re.S)
 assert n==1,p
 if updated!=s:p.write_text(updated,encoding='utf-8');count+=1
print('Updated footer rows:',count)
