import json
from pathlib import Path
p=Path('verification/state-guides/research/additional-b.json');d=json.loads(p.read_text(encoding='utf8'))
x=next(x for x in d['pilots'] if x['code']=='MA')
x['sections'][0]['source_ids']=['MA1']
x['sections'][4]['source_ids']=[]
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Final total words',sum(len(t.split()) for x in d['pilots'] for s in x['sections'] for t in s['paragraphs']))
