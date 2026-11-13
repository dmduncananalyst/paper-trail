"""Release checks; never publish an incomplete multilingual release."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib, html, json, re, sys, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/articles-20261113'
A=json.loads((OUT/'approved-content.json').read_text(encoding='utf8'))
LANGS=['es','fa','hy','zh-CN','ko','tl','te','ru','ar']
REJECTED=['how-much-does-a-bookkeeper-cost-for-small-businesses.html','why-every-small-business-needs-a-bookkeeper.html','how-to-choose-a-bookkeeper-for-your-small-business.html','what-to-look-for-when-hiring-a-bookkeeper-in-2025.html']
errors=[]
def check(test,message):
    if not test: errors.append(message)
def text(s):return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>','',s))).strip()
maps={p.name:{n.text for n in ET.parse(p).iter() if n.tag.endswith('}loc')} for p in ROOT.glob('sitemap*.xml')}
for name,urls in maps.items():
    for slug in REJECTED:check(not any(u.endswith('/'+slug) for u in urls),name+': rejected '+slug)
for a in A:
    s=(ROOT/a['slug']).read_text(encoding='utf8')
    check(text(re.search(r'<h1>(.*?)</h1>',s,re.S)[1])==a['title'],a['slug']+': title')
    check(html.unescape(re.search(r'<title>(.*?)</title>',s,re.S)[1])==a['meta_title'],a['slug']+': meta title')
    check('content="'+html.escape(a['description'],quote=True)+'"' in s,a['slug']+': description')
    check('rel="canonical" href="'+a['canonical']+'"' in s,a['slug']+': canonical')
    check('<time datetime="2026-11-13">11/13/2026</time>' in s,a['slug']+': date')
    body=s.split('<div class="reading-spread">',1)[1].split('<section class="reference-list">',1)[0]
    actual=[text(m[1]) for m in re.finditer(r'<(?:p|h2)\b[^>]*>(.*?)</(?:p|h2)>',body,re.S)]
    check(actual==[b['text'] for b in a['article']],a['slug']+': PDF body mismatch')
    check('small business' not in ' '.join(actual+[a['title']]).lower(),a['slug']+': prohibited visible wording')
    schemas=[json.loads(m[1]) for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>',s,re.S)]
    schema=next(x for x in schemas if x.get('@type')=='BlogPosting')
    check(schema['datePublished']=='2026-11-13',a['slug']+': schema date')
    check(schema['articleBody']=='\n\n'.join(b['text'] for b in a['article']),a['slug']+': schema body')
    for r in a['references']:check('href="'+html.escape(r['url'],quote=True)+'"' in s,a['slug']+': source '+r['url'])
    check((ROOT/a['image']).is_file(),a['slug']+': photograph missing')
    check(a['canonical'] in maps['sitemap.xml'],a['slug']+': sitemap missing')
baseline=json.loads((OUT/'preservation-baseline.json').read_text(encoding='utf8'))
portable_path=OUT/'preservation-portable.json'
portable=json.loads(portable_path.read_text(encoding='utf8')) if portable_path.exists() else None
allowed={'blog.html','sitemap.xml','sitemap-translations.xml'}|{l+'/blog.html' for l in LANGS}
preserved=0
for name,digest in baseline.items():
    if name in allowed:continue
    p=ROOT/name
    check(p.is_file(),name+': pre-existing file disappeared')
    if p.is_file():
        data=p.read_bytes()
        expected=portable[name] if portable is not None else digest
        if portable is not None and name.endswith(('.html','.xml')):data=data.replace(b'\r\n',b'\n')
        check(hashlib.sha256(data).hexdigest()==expected,name+': pre-existing file changed')
        preserved+=1
missing=[l+'/'+a['slug'] for l in LANGS for a in A if not (ROOT/l/a['slug']).exists()]
if '--require-translations' in sys.argv:
    for route in missing:errors.append('Missing translation: '+route)
    for lang in LANGS:
        archive=(ROOT/lang/'blog.html').read_text(encoding='utf8')
        for a in A:
            route=lang+'/'+a['slug'];path=ROOT/route
            if not path.exists():continue
            s=path.read_text(encoding='utf8')
            url='https://www.papertrailusa.com/'+route
            check('rel="canonical" href="'+url+'"' in s,route+': canonical')
            check('datetime="2026-11-13"' in s,route+': date')
            check(url in maps['sitemap-translations.xml'],route+': sitemap')
            check('href="'+route+'"' in archive,route+': archive card')
            check(a['image'] in s,route+': photo')
            hero=re.search(r'<header class="reading-masthead"><img\b[^>]*alt="([^"]*)"',s)
            social=re.search(r'<meta property="og:image:alt" content="([^"]*)"',s)
            check(hero is not None and social is not None and html.unescape(hero[1])==html.unescape(social[1]),route+': localized social image alt')
            check(len(re.findall(r'rel="alternate" hreflang=',s))==11,route+': hreflang')
            schema=next(json.loads(m[1]) for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>',s,re.S) if json.loads(m[1]).get('@type')=='BlogPosting')
            check(schema['datePublished']=='2026-11-13',route+': schema date')
            check(schema['inLanguage']==lang,route+': schema language')
            check(schema['citation']==[r['url'] for r in a['references']],route+': source references')
            body=s.split('<div class="reading-spread">',1)[1].split('<section class="reference-list">',1)[0]
            actual=[text(m[1]) for m in re.finditer(r'<(?:p|h2)\b[^>]*>(.*?)</(?:p|h2)>',body,re.S)]
            check(len(actual)==len(a['article']),route+': full article structure')
            check(schema['articleBody']=='\n\n'.join(actual),route+': full structured article body')
            if lang in ['fa','ar']:check('class="reading-feature approved-blog" dir="rtl"' in s,route+': RTL')
before_path=OUT/'sitemap-baseline.json'
if before_path.exists():
    before=json.loads(before_path.read_text(encoding='utf8'))
    for filename,urls in before.items():
        for url in urls:
            if not any(url.endswith('/'+slug) for slug in REJECTED):
                check(url in maps[filename],filename+': existing sitemap URL disappeared: '+url)
report={'english_articles':len(A),'preserved_files_checked':preserved,'missing_translated_pages':len(missing),'paid_calls_made_by_verifier':0,'errors':errors,'release_ready':not errors and not missing}
(OUT/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps(report,indent=2))
if errors:raise SystemExit(1)
