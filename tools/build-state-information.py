"""Build researched local state pages without approving or publishing them."""
from pathlib import Path
from html import escape
import csv
import json
import re

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / 'verification/state-guides/research'
OUTPUT = ROOT / 'state-records'
OUTPUT.mkdir(exist_ok=True)
header_flags={r['state']:r for r in json.loads((ROOT/'verification/visual-corrections/state-header-flag-assets.json').read_text(encoding='utf-8-sig'))}
states = {}
for filename in ['pilots.json', 'additional-a.json', 'additional-b.json', 'additional-c.json']:
    path = RESEARCH / filename
    if path.exists():
        data = json.loads(path.read_text(encoding='utf-8-sig'))
        for state in data.get('pilots', []):
            states[state['state']] = state

shell = (ROOT / 'about.html').read_text(encoding='utf-8')
head = re.search(r'<head>(.*?)</head>', shell, re.S)[1]
head = re.sub(r'<script type="application/ld\+json">.*?</script>', '', head, flags=re.S)
head = re.sub(r'<meta name="robots"[^>]*>', '<meta name="robots" content="noindex,follow">', head)
head=re.sub(r'<link rel="preload" as="image"[^>]*>', '', head)
head = '<base href="../">' + head
header = re.search(r'<body[^>]*>(.*?)<main', shell, re.S)[1]
tail = re.search(r'</main>(.*?)</body>', shell, re.S)[1]
rows = []
paragraph_index = {}
duplicates = []
for name, item in sorted(states.items()):
    slug = name.lower().replace(' ', '-')
    canonical = f'https://www.papertrailusa.com/state-records/{slug}.html'
    title = name + ' Bookkeeping'
    description = item['description']
    sources = {s['id']: s for s in item['sources']}
    assert len(item['sections']) >= 5, name
    assert len(sources) >= 3, name
    ph = re.sub(r'<title>.*?</title>', '<title>'+escape(title+' | Paper Trail')+'</title>', head)
    ph = re.sub(r'(<meta (?:name="(?:description|twitter:description)"|property="og:description") content=")[^"]*(")', lambda m:m[1]+escape(description, quote=True)+m[2], ph)
    ph = re.sub(r'(<meta (?:name="twitter:title"|property="og:title") content=")[^"]*(")', lambda m:m[1]+escape(title+' | Paper Trail', quote=True)+m[2], ph)
    ph = ph.replace('https://www.papertrailusa.com/about.html', canonical)
    reviewed = item.get('verified_on', '2026-10-16')
    schema = {'@context':'https://schema.org','@type':'WebPage','name':title,'description':description,'url':canonical,'inLanguage':'en-US','lastReviewed':reviewed,'citation':[s['url'] for s in sources.values()]}
    ph += '<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False)+'</script>'
    flag=header_flags[name]
    size=flag['dimensions']
    viewbox=(size.get('viewBox') or '').replace(',', ' ').split()
    width=re.search(r'[\d.]+',size.get('width') or '')
    height=re.search(r'[\d.]+',size.get('height') or '')
    fw=width[0] if width else viewbox[2] if len(viewbox)==4 else '900'
    fh=height[0] if height else viewbox[3] if len(viewbox)==4 else '600'
    ph+='<link rel="preload" as="image" href="'+escape(flag['header_file'])+'" fetchpriority="high">'
    body = '<main id="main" class="state-draft-main"><header class="reading-masthead state-masthead"><img src="'+escape(flag['header_file'])+'" alt="Flag of '+escape(name)+'" width="'+fw+'" height="'+fh+'" loading="eager" decoding="sync" fetchpriority="high"><h1>'+escape(title)+'</h1></header><div class="state-resource-body"><p class="state-summary">'+escape(item['summary'])+'</p>'
    words = 0
    for section in item['sections']:
        body += '<section><h2>'+escape(section['heading'])+'</h2>'
        for paragraph in section['paragraphs']:
            words += len(paragraph.split())
            normalized = re.sub(r'\s+', ' ', paragraph).strip().casefold()
            if normalized in paragraph_index:
                duplicates.append({'state':name,'also_in':paragraph_index[normalized],'paragraph':paragraph})
            paragraph_index[normalized] = name
            body += '<p>'+escape(paragraph)+'</p>'
        refs=[]
        for sid in section.get('source_ids', []):
            assert sid in sources, (name, sid)
            source=sources[sid]
            refs.append('<a href="'+escape(source['url'],quote=True)+'">'+escape(re.sub(r'\bGuide\b', 'Information', source['title'], flags=re.I))+'</a>')
        if section.get('source_context'):
            body+='<p class="source-context">'+escape(section['source_context'])+'</p>'
        if refs:
            body += '<div class="state-source-links">Sources: '+', '.join(refs)+'</div>'
        body+='</section>'
    body += '<section><h2>Official Sources</h2><ol class="state-reference-list">'+''.join('<li><a href="'+escape(s['url'],quote=True)+'">'+escape(re.sub(r'\bGuide\b', 'Information', s['title'], flags=re.I))+'</a></li>' for s in sources.values())+'</ol></section>'
    body += '<p class="state-boundary">'+escape(item.get('notice','This information explains bookkeeping records. Tax treatment and legal decisions should be reviewed with the appropriate qualified professional. Paper Trail does not claim an office in this state.'))+'</p></div><nav class="state-related" aria-label="Related bookkeeping services"><a class="action quiet" href="paper-trail-services.html">Bookkeeping Repair</a><a class="action quiet" href="paper-trail-monthly-bookkeeping.html">Monthly Bookkeeping</a><a class="action quiet" href="nationwide-bookkeeping.html">Nationwide Bookkeeping</a></nav></main>'
    path=OUTPUT/(slug+'.html')
    path.write_text('<!doctype html><html lang="en"><head>'+ph+'</head><body class="pt-preview pt-state-information">'+header+body+tail+'</body></html>',encoding='utf-8')
    rows.append({'state':name,'local_url':'state-records/'+slug+'.html','planned_canonical':canonical,'body_words':words,'source_count':len(sources),'sections':len(item['sections']),'last_reviewed':reviewed,'quality_review':item.get('quality_review',{}),'remaining_review':item.get('review_gaps',[]),'owner_approval':'Pending','publication':'Not published','sitemap':'Excluded until individually approved and published'})

flags=list(csv.DictReader((RESEARCH/'flag-sources.csv').open(encoding='utf-8-sig')))
tiles=[]
for flag in sorted(flags,key=lambda f:f['state']):
    name=flag['state'];slug=name.lower().replace(' ','-')
    content='<img src="'+escape(flag['local_file'],quote=True)+'" alt="Flag of '+escape(name)+'" width="330" height="220" loading="lazy" decoding="async"><span class="state-name">'+escape(name)+'</span>'
    if name in states:
        tiles.append('<li><a href="state-records/'+slug+'.html" aria-label="'+escape(name)+' bookkeeping, View State Information">'+content+'<span class="state-action">View State Information</span></a></li>')
    else:
        tiles.append('<li><div class="state-entry">'+content+'</div></li>')
page=ROOT/'nationwide-bookkeeping.html'
t=page.read_text(encoding='utf-8')
t,count=re.subn(r'(<ul class="state-mosaic"[^>]*>).*?(</ul>)',lambda m:m[1]+''.join(tiles)+m[2],t,count=1,flags=re.S)
assert count==1
page.write_text(t,encoding='utf-8')
report={'reviewed_on':'2026-10-16','state_pages_built':len(rows),'planned_states':50,'missing_states':[f['state'] for f in flags if f['state'] not in states],'duplicate_body_paragraphs':duplicates,'states':rows,'sitemap_unchanged':True,'indexing_policy':'Local content review only, noindex until owner approval. No publication or Git actions performed.'}
(ROOT/'verification/visual-corrections/state-completion-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'local_pages':len(rows),'missing':report['missing_states'],'exact_duplicate_paragraphs':len(duplicates)}))
