"""Extract the approved PDF without rewriting prose; capture preservation evidence."""
from pathlib import Path
from pypdf import PdfReader
import hashlib, json, re, sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/articles-20261113'
OUT.mkdir(exist_ok=True)
PDF = Path(r'C:\Users\Owner\Downloads\Paper_Trail_Final_8_Articles_Content_Metadata_Sources.pdf')

def save(name, value):
    (OUT/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

if '--extract-only' not in sys.argv and not (OUT/'preservation-baseline.json').exists():
    paths = list(ROOT.glob('*.html'))
    for lang in ['es','fa','hy','zh-CN','ko','tl','te','ru','ar']:
        paths += list((ROOT/lang).glob('*.html'))
    # Hash publication assets, avoiding redundant historical translation releases.
    paths += [p for folder in ['photos','images','blog-leads-20261103'] for p in (ROOT/'assets'/folder).rglob('*')]
    paths += list(ROOT.glob('*.xml'))
    save('preservation-baseline.json', {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()})

reader = PdfReader(PDF)
blocks=[]
for page in reader.pages[1:14]:
    groups=[]
    def visit(text, cm, tm, font, size):
        if not text.strip() or size == 8 or size == 8.4 and 'PAPER TRAIL /' in text:
            return
        identity=(tuple(cm),size)
        if groups and groups[-1]['identity']==identity:
            groups[-1]['text'] += text
        else:
            groups.append({'identity':identity,'size':size,'text':text})
    page.extract_text(visitor_text=visit)
    blocks.extend({'size':g['size'],'text':re.sub(r'\s+',' ',g['text']).strip().replace('\x7f',"'").replace('\u2019',"'")} for g in groups)

articles=[]
for b in blocks:
    t=b['text']
    if b['size']==16:
        articles.append({'title':t,'article':[],'references':[]})
        mode='metadata'
        continue
    a=articles[-1]
    if t.startswith('Original URL filename:'): a['slug']=t.split(': ',1)[1]
    elif t.startswith('Canonical URL:'): a['canonical']=t.split(': ',1)[1]
    elif t.startswith('Meta title:'): a['meta_title']=t.split(': ',1)[1]
    elif t.startswith('Meta description:'): a['description']=t.split(': ',1)[1]
    elif t.startswith('Publication date:'): mode='body'
    elif t=='Sources and reference links': mode='references'
    elif mode=='references': a['references'].append(t)
    elif mode=='body':
        heading=b['size']==11.1
        if not heading and a['article'] and not a['article'][-1]['heading'] and not re.search(r'[.!?]$',a['article'][-1]['text']):
            a['article'][-1]['text'] += ' '+t
        else: a['article'].append({'heading':heading,'text':t})
    else: raise ValueError('Unparsed metadata: '+t)
for a in articles:
    refs=' '.join(a['references'])
    references=[]; start=0
    for m in re.finditer(r'https://\S+',refs):
        references.append({'label':refs[start:m.start()].strip().rstrip(':'),'url':m[0]})
        start=m.end()
    assert not refs[start:].strip(), refs[start:]
    a['references']=references
    a['date']='2026-11-13'
    assert a['title']==a['meta_title']
    assert a['canonical']=='https://www.papertrailusa.com/'+a['slug']
    assert 'small business' not in ' '.join([a['title']]+[b['text'] for b in a['article']]).lower()
assert len(articles)==8
save('approved-content.json',articles)
save('source-provenance.json',{'pdf':PDF.name,'sha256':hashlib.sha256(PDF.read_bytes()).hexdigest(),'publication_date_authority':'Owner pasted request; replacement articles dated November 13, 2026','articles':len(articles)})
print(json.dumps([{'slug':a['slug'],'sections':len(a['article']),'sources':len(a['references'])} for a in articles],indent=2))
