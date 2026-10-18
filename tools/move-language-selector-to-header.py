"""Move the saved language control into every English page header, offline."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
home=(root/'index.html').read_text(encoding='utf-8')
control=re.search(r'<label class="language-control">.*?</label>',home,re.S)[0]
control=control.replace('<select id="language"','<select translate="no" id="language"')
changed=0
for p in [*root.glob('*.html'),*(root/'state-records').glob('*.html')]:
 s=p.read_text(encoding='utf-8')
 updated=re.sub(r'<label class="language-control">.*?</label>','',s,flags=re.S)
 updated=re.sub(r'<div class="page-language">.*?</div>','',updated,flags=re.S)
 assert updated.count('<div class="header-tools">')==1,p
 updated=updated.replace('<div class="header-tools">','<div class="header-tools">'+control,1)
 if updated!=s:p.write_text(updated,encoding='utf-8');changed+=1
print('Updated header controls:',changed)
