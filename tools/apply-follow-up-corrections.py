"""Apply the owner's follow-up corrections locally, without provider calls."""
from pathlib import Path
from PIL import Image
from html import escape, unescape
import csv
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/follow-up-20261016'
OUT.mkdir(exist_ok=True)
if (OUT/'applied.json').exists():
    raise SystemExit('Follow-up corrections already applied. Edit the targeted files directly for further changes.')
snapshot={p.as_posix():p.read_text(encoding='utf-8') for p in [Path('assets/design.css'),Path('assets/design.js'),Path('assets/site.js'),Path('assets/site.css'),Path('assets/hubspot.js')]}
(OUT/'before-assets.json').write_text(json.dumps(snapshot,ensure_ascii=False),encoding='utf-8')

# Keep the current font families, but eliminate the remote font swap dependency.
p=ROOT/'assets/site.css';text=p.read_text(encoding='utf-8')
text=re.sub(r"@import url\('https://fonts.googleapis.com/[^']+'\);\s*",'',text,count=1)
fonts="@font-face{font-family:'DM Sans';font-style:normal;font-weight:100 1000;font-display:optional;src:url('fonts/dm-sans.ttf') format('truetype')}\n@font-face{font-family:'Libre Caslon Display';font-style:normal;font-weight:400;font-display:optional;src:url('fonts/libre-caslon-display.ttf') format('truetype')}\n"
p.write_text(fonts+text,encoding='utf-8')

changed=[];images_fixed=0;chat_configs=0
pages=list(ROOT.glob('*.html'))+list((ROOT/'state-records').glob('*.html'))
dimensions={}
for path in pages:
    text=path.read_text(encoding='utf-8');original=text
    text=re.sub(r'<link rel="preconnect" href="https://fonts\.(?:googleapis|gstatic)\.com"[^>]*>','',text)
    text=text.replace('</head>','<link rel="preload" href="assets/fonts/dm-sans.ttf" as="font" type="font/ttf" crossorigin></head>')
    text=text.replace('Nationwide – Based in Los Angeles.','Nationwide, based out of Los Angeles.')
    text=text.replace('&Amp;','&amp;')
    text=text.replace('Find The Difference','Balance My Books').replace('Find the difference','Balance My Books')
    def notes_action(match):
        return match[1]+escape(unescape(match[2]).replace('&','and'))+match[3]
    text=re.sub(r'(<div class="all-service-notes"><a[^>]*>)(.*?)(</a>)',notes_action,text,flags=re.S)
    text=re.sub(r'<p class="state-review-date">.*?</p>','',text,flags=re.S)
    if path.name.startswith('bookkeeping-') and path.parent==ROOT:
        match=re.search(r'<h1>Bookkeeping for (.*?) businesses</h1>',text)
        if match:
            city=match[1]
            text=text.replace('<p class="eyebrow">Across Los Angeles County</p>','<p class="eyebrow">Bookkeeping</p>')
            text=text.replace(match[0],'<h1>'+city+'</h1>',1)
    config=re.search(r'(<script[^>]+id="conversation-data"[^>]*>)(.*?)(</script>)',text,re.S)
    if config:
        data=json.loads(config[2]);data['opening']='What about your books needs attention?'
        text=text[:config.start()]+config[1]+json.dumps(data,ensure_ascii=False)+config[3]+text[config.end():]
        chat_configs+=1
    def image_size(match):
        global images_fixed
        tag=match[0];source=re.search(r'src="([^"]+)"',tag)
        if not source:return tag
        src=unescape(source[1]);asset=ROOT/src
        if not asset.exists() or asset.suffix.lower()=='.svg':return tag
        if src not in dimensions:
            try:
                with Image.open(asset) as image:dimensions[src]=image.size
            except Exception:return tag
        width,height=dimensions[src]
        if not re.search(r'\bwidth="',tag):tag=tag.replace('<img','<img width="'+str(width)+'"',1);images_fixed+=1
        if not re.search(r'\bheight="',tag):tag=tag.replace('<img','<img height="'+str(height)+'"',1)
        if path.name in ['notes.html','index.html','blog.html']:
            tag=tag.replace('loading="lazy"','loading="eager"').replace('decoding="async"','decoding="sync"')
        return tag
    text=re.sub(r'<img\b[^>]*>',image_size,text)
    # Prioritize the first content image while the rest of the document is parsed.
    main=text.find('<main');first=re.search(r'<img\b[^>]*src="([^"]+)"[^>]*>',text[main:]) if main>=0 else None
    if first:
        src=first[1]
        text=text.replace('</head>','<link rel="preload" as="image" href="'+src+'" fetchpriority="high"></head>')
        start=main+first.start();end=main+first.end();tag=text[start:end]
        # Preload insertion precedes main, so locate the image again after insertion.
        first=re.search(r'<img\b[^>]*src="'+re.escape(src)+r'"[^>]*>',text[text.find('<main'):])
        if first:
            start=text.find('<main')+first.start();end=text.find('<main')+first.end();tag=text[start:end]
            tag=tag.replace('loading="lazy"','loading="eager"').replace('decoding="async"','decoding="sync"')
            if 'fetchpriority=' not in tag:tag=tag.replace('<img','<img fetchpriority="high"',1)
            text=text[:start]+tag+text[end:]
    text=text.replace('v=visual-20261016','v=follow-up-20261016').replace('assets/site.js?v=owner-feedback-3','assets/site.js?v=follow-up-20261016').replace('current.js?v=corrections-4','current.js?v=follow-up-20261016')
    if text!=original:path.write_text(text,encoding='utf-8');changed.append(path.relative_to(ROOT).as_posix())

locations={
'en':'Nationwide, based out of Los Angeles.',
'es':'En todo el país, con sede en Los Ángeles.',
'hy':'Ամբողջ երկրում, կենտրոնը Լոս Անջելեսում։',
'fa':'در سراسر آمریکا، مستقر در لس آنجلس.',
'ar':'خدمة في جميع أنحاء البلاد، مقرنا في لوس أنجلوس.',
'ko':'미국 전역 서비스, 로스앤젤레스 기반.',
'ru':'По всей стране, базируемся в Лос-Анджелесе.',
'te':'దేశవ్యాప్తంగా, లాస్ ఏంజెలెస్ కేంద్రంగా.',
'tl':'Sa buong bansa, nakabase sa Los Angeles.',
'zh-CN':'服务全美，总部位于洛杉矶。'}
bundle={}
for code,value in locations.items():
    p=ROOT/'assets/locales/home-blog'/(code+'.json');data=json.loads(p.read_text(encoding='utf-8'));data['location']=value;p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');bundle[code]=data
(ROOT/'assets/locales/home-blog/current.js').write_text('/* Saved authored Home and Blog drafts. No provider calls. */\nwindow.PAPER_TRAIL_LOCALES='+json.dumps(bundle,ensure_ascii=False)+';\n',encoding='utf-8')
p=ROOT/'assets/locales/home-blog/manifest.json';manifest=json.loads(p.read_text(encoding='utf-8'));manifest['fields']['location']['source']=locations['en'];manifest['fields']['location']['source_sha256']=hashlib.sha256(locations['en'].encode()).hexdigest();p.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')

# Empty source rows are not rendered as if references were missing. General
# bookkeeping sections use a clearly identified federal recordkeeping source.
research=ROOT/'verification/state-guides/research'
source_additions=[]
for filename in ['pilots.json','additional-a.json','additional-b.json','additional-c.json']:
    p=research/filename;data=json.loads(p.read_text(encoding='utf-8-sig'))
    for state in data['pilots']:
        empty=[s for s in state['sections'] if not s.get('source_ids')]
        if not empty:continue
        sid=state['code']+'BK'
        if not any(s['id']==sid for s in state['sources']):
            state['sources'].append({'id':sid,'title':'IRS, Small Business Recordkeeping','url':'https://www.irs.gov/businesses/small-businesses-self-employed/recordkeeping','claims':['General support for income, expense and transaction documentation, financial statements and tax preparation. Not a state specific monthly reporting mandate.'],'checked_on':'2026-10-16','verification':'Official IRS page read. Hypothetical examples remain illustrative, not agency examples.'})
        for section in empty:section['source_ids']=[sid];section['source_context']='General bookkeeping reference. The example and monthly routine are practical illustrations, not additional state requirements.'
        source_additions.append(state['state'])
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

# Owner has now supplied the publication date for each Blog post.
p=ROOT/'verification/visual-corrections/blog-date-review.json';dates=json.loads(p.read_text(encoding='utf-8'))
for post in dates['posts']:post['datePublished']='2026-10-16';post['status']='Publication date supplied by the owner in the follow-up instruction.'
p.write_text(json.dumps(dates,indent=2),encoding='utf-8')

(OUT/'applied.json').write_text(json.dumps({'changed_html':changed,'image_dimensions_added':images_fixed,'chat_configs_audited':chat_configs,'general_recordkeeping_references_added_to_states':source_additions,'google_api_calls':0},indent=2),encoding='utf-8')
print(json.dumps({'html_files':len(changed),'image_dimensions_added':images_fixed,'chat_configurations':chat_configs,'state_general_sources_added':len(source_additions)}))
