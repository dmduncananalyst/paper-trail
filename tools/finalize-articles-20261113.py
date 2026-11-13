"""Preserve standard chat UI, apply RTL to new article text, finalize route inventory."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/articles-20261113'
A=json.loads((OUT/'approved-content.json').read_text(encoding='utf8'))
LANGS=['es','fa','hy','zh-CN','ko','tl','te','ru','ar']
TEMPLATE='business-loan-proceeds-nobody-can-show-where-money-went.html'
for lang in ['',*LANGS]:
    folder=ROOT/lang
    source=(folder/TEMPLATE).read_text(encoding='utf8')
    chat=re.search(r'<section class="home-conversation">.*?</section>',source,re.S)[0]
    for a in A:
        p=folder/a['slug'];s=p.read_text(encoding='utf8')
        # Reuse the already-translated photograph alt for social metadata, too.
        alt=re.search(r'<header class="reading-masthead"><img\b[^>]*alt="([^"]*)"',s)[1]
        s=re.sub(r'(<meta (?:property="og:image:alt"|name="twitter:image:alt") content=")[^"]*(")',lambda m:m[1]+alt+m[2],s)
        if 'data-open-chat' not in s:s=s.replace('<dialog',chat+'<dialog',1)
        if lang in ['fa','ar']:
            s=s.replace('<article class="reading-feature approved-blog">','<article class="reading-feature approved-blog" dir="rtl">')
        p.write_text(s,encoding='utf8')
    if lang in ['fa','ar']:
        p=folder/'blog.html';s=p.read_text(encoding='utf8')
        def rtl(m):
            return m[0].replace('<article ','<article dir="rtl" ',1) if any('href="'+lang+'/'+a['slug']+'"' in m[0] for a in A) and 'dir="rtl"' not in m[0] else m[0]
        s=re.sub(r'<article\b[^>]*class="[^"]*\bblog-story\b[^"]*"[^>]*>.*?</article>',rtl,s,flags=re.S)
        p.write_text(s,encoding='utf8')
p=ROOT/'tools/production-pages.json';config=json.loads(p.read_text(encoding='utf8'))
for lang in LANGS:
    for a in A:
        if a['slug'] not in config['locales'][lang]:config['locales'][lang].append(a['slug'])
p.write_text(json.dumps(config,indent=2)+'\n',encoding='utf8')
for filename in ['sitemap.xml','sitemap-translations.xml']:
    p=ROOT/filename;s=p.read_text(encoding='utf8')
    def entry(m):
        url=re.search(r'<loc>(.*?)</loc>',m[0])[1]
        if not any(url.endswith('/'+a['slug']) for a in A):return m[0]
        text=m[0]
        if '<lastmod>' not in text:text=text.replace('</loc>','</loc><lastmod>2026-11-13</lastmod>',1)
        return text
    s=re.sub(r'<url\b[^>]*>.*?</url>',entry,s,flags=re.S)
    p.write_text(s,encoding='utf8')
print('Finalized 80 article pages and nine archives; prior article files preserved.')
