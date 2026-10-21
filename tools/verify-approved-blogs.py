"""Verify approved article text, assets, links, SEO, and preservation locally."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from urllib.request import urlopen
import hashlib, json, re, subprocess, xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/approved-blogs-20261020'
manifest=json.loads((OUT/'approved-content.json').read_text(encoding='utf-8'))
class Document(HTMLParser):
    def __init__(self,text):
        super().__init__(convert_charrefs=True);self.tags=[];self.feed(text)
    def handle_starttag(self,tag,attrs):self.tags.append((tag,dict(attrs)))

archive=(ROOT/'blog.html').read_text(encoding='utf-8')
original=subprocess.check_output(['git','show','HEAD:blog.html'],cwd=ROOT).decode('utf-8')
old_cards=re.findall(r'<article class="blog-story">.*?</article>',original,re.S)
assert len(old_cards)==3 and all(card in archive for card in old_cards)
sitemap=ET.fromstring((ROOT/'sitemap.xml').read_text(encoding='utf-8'))
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
locations=[x.text for x in sitemap.findall('s:url/s:loc',ns)]
checks=[]
for item in manifest:
    slug=item['slug'];text=(ROOT/slug).read_text(encoding='utf-8');doc=Document(text)
    title=re.search(r'<title>(.*?)</title>',text)[1]
    assert title==item['title']
    metas={a['name']:a['content'] for t,a in doc.tags if t=='meta' and 'name' in a}
    assert metas['description']==item['description']
    canon=[a['href'] for t,a in doc.tags if t=='link' and a.get('rel')=='canonical']
    assert canon==['https://www.papertrailusa.com/'+slug]
    assert locations.count(canon[0])==1
    assert sum(t=='h1' for t,a in doc.tags)==1
    schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',text,re.S)[1])
    assert schema['headline']==item['title'] and schema['description']==item['description']
    assert schema['articleBody']=='\n\n'.join(x['text'] for x in item['article'])
    assert all('\u2014' not in x['text'] and '\u2013' not in x['text'] for x in item['article'])
    assert len(item['article'])==14
    assert 'Developer placement:' not in text and 'IMAGE ASSIGNMENT:' not in text
    for ref in item['references']:
        assert any(t=='a' and a.get('href')==ref['url'] for t,a in doc.tags)
    local_links=0
    for t,a in doc.tags:
        value=a.get('href') if t in ('a','link') else a.get('src') if t in ('img','script') else None
        if not value:continue
        u=urlsplit(value)
        if u.scheme or u.netloc or not u.path:continue
        target=ROOT/unquote(u.path)
        assert target.is_file(), (slug,value)
        with urlopen('http://127.0.0.1:8765/'+u.path.replace(' ','%20'),timeout=10) as r:
            assert r.status==200
        local_links+=1
    source=Path(r'C:\Users\Owner\OneDrive\Desktop')/item['photo']
    copied=ROOT/'assets/photos'/item['photo']
    assert source.read_bytes()==copied.read_bytes()
    assert hashlib.sha256(copied.read_bytes()).hexdigest()==item['sha256']
    checks.append({'article':slug,'sections':7,'complete_text':True,'references':2,'local_links_and_assets_http_200':local_links,'photo_unchanged':True,'seo_verified':True})
tracked=subprocess.check_output(['git','diff','--name-only'],cwd=ROOT).decode().splitlines()
assert set(tracked)=={'blog.html','sitemap.xml'},tracked
result={'articles':checks,'existing_cards_preserved':len(old_cards),'unrelated_tracked_files_unchanged':True,'translation_status':'Blocked: existing workflow imports absent sun-and-sage/scripts/translation_pipeline. Both inventory and prepare raise ModuleNotFoundError. No replacement or paid calls made.','publication':'Local only. No commits, pushes, deployment, or live form submissions.'}
(OUT/'verification-summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
