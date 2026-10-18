"""Apply only confirmed publication dates recorded in the review manifest.

Run without arguments for a dry run. The --apply option writes confirmed dates.
An editing timestamp is never substituted for a missing publication date.
"""
from pathlib import Path
from datetime import date
from html import escape
import argparse
import json
import re

parser = argparse.ArgumentParser()
parser.add_argument('--apply', action='store_true')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
manifest = json.loads((root/'verification/visual-corrections/blog-date-review.json').read_text(encoding='utf-8'))
listing = (root/'blog.html').read_text(encoding='utf-8')
confirmed=[]
missing=[]
for post in manifest['posts']:
    if not post.get('datePublished'):
        missing.append(post['url'])
        continue
    iso = date.fromisoformat(post['datePublished']).isoformat()
    label = date.fromisoformat(iso).strftime('%m/%d/%Y')
    markup = '<p class="publication-date">Published <time datetime="'+iso+'">'+label+'</time></p>'
    path=root/post['url']
    text=path.read_text(encoding='utf-8')
    text=re.sub(r'<p class="publication-date(?: missing)?">.*?</p>','',text)
    column=re.search(r'<div class="reading-column">',text)
    at=column.end() if column else text.index('</header>',text.index('class="reading-masthead"'))+9
    text=text[:at]+markup+text[at:]
    def update_schema(match):
        data=json.loads(match[1])
        def walk(obj):
            if isinstance(obj,dict):
                kind=obj.get('@type',[])
                if kind in ('Article','BlogPosting') or isinstance(kind,list) and any(t in kind for t in ['Article','BlogPosting']):obj['datePublished']=iso
                for value in obj.values():walk(value)
            elif isinstance(obj,list):
                for value in obj:walk(value)
        walk(data)
        return '<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False)+'</script>'
    text=re.sub(r'<script type="application/ld\+json">(.*?)</script>',update_schema,text,flags=re.S)
    def update_card(match):
        block=match[0]
        if 'href="'+post['url']+'"' in block:
            block=re.sub(r'<p class="publication-date(?: missing)?">.*?</p>',markup,block,count=1)
        return block
    listing=re.sub(r'<article class="blog-story">.*?</article>',update_card,listing,flags=re.S)
    if args.apply:path.write_text(text,encoding='utf-8')
    confirmed.append({'url':post['url'],'display_date':label})
if args.apply:(root/'blog.html').write_text(listing,encoding='utf-8')
print(json.dumps({'mode':'apply' if args.apply else 'dry run','confirmed':confirmed,'missing_actual_publication_date':missing},indent=2))
