"""Install only the eight owner-approved replacement articles and archive records."""
from pathlib import Path
import html, json, re, hashlib
from urllib.parse import quote

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/articles-20261113'
ORIGIN='https://www.papertrailusa.com/'
ARTICLES=json.loads((OUT/'approved-content.json').read_text(encoding='utf8'))
LANGS=['es','fa','hy','zh-CN','ko','tl','te','ru','ar']
REJECTED=['how-much-does-a-bookkeeper-cost-for-small-businesses.html','why-every-small-business-needs-a-bookkeeper.html','how-to-choose-a-bookkeeper-for-your-small-business.html','what-to-look-for-when-hiring-a-bookkeeper-in-2025.html']
ALTS=[
    'Finance professional comparing customer invoices and vendor bills beside a laptop and calculator.',
    'Business owner organizing receipts and account records in a new design studio.',
    'Finance professional reviewing archived expense receipts and monthly recordkeeping folders.',
    'Accountant matching payment processor records with bank statements at an office desk.',
    'Business owner and accountant reviewing an organized tax season document package.',
    'Bookkeeper reconciling monthly transactions with invoices and financial records at her workstation.',
    'Finance professional checking ledger balances against bank statements before the tax handoff.',
    'Business owner and bookkeeper reviewing financial reports and supporting records together.'
]

def write(path,text):
    if not path.exists() or path.read_text(encoding='utf8')!=text: path.write_text(text,encoding='utf8')

def render():
    template=(ROOT/'business-loan-proceeds-nobody-can-show-where-money-went.html').read_text(encoding='utf8')
    oldslug='business-loan-proceeds-nobody-can-show-where-money-went.html'
    cards=[]
    for i,a in enumerate(ARTICLES):
        a['image']='assets/photos/'+a['slug'][:-5]+'-20261113.jpg'
        a['alt']=ALTS[i]
        # Generated photographs use the same 1448 x 1086 dimensions as existing blog assets.
        image='<img src="'+a['image']+'" alt="'+html.escape(a['alt'],quote=True)+'" width="1448" height="1086" loading="eager" decoding="sync" fetchpriority="high" style="display:block;width:100%;height:auto;object-fit:cover;--image-intrinsic-ratio:auto 1448 / 1086;"/>'
        sections=[]
        for b in a['article']:
            if b['heading']:
                if sections: sections.append('</div></section>')
                sections.append('<section class="story-section"><h2>'+html.escape(b['text'])+'</h2><div class="section-copy">')
            else: sections.append('<p>'+html.escape(b['text'])+'</p>')
        sections.append('</div></section>')
        refs='<section class="reference-list"><h2>Sources and references</h2><ol>'+''.join('<li><a href="'+html.escape(r['url'],quote=True)+'" target="_blank" rel="noopener">'+html.escape(r['label'])+'</a></li>' for r in a['references'])+'</ol></section>'
        date='<p class="publication-date">Published <time datetime="2026-11-13">11/13/2026</time></p>'
        standard_chat=re.search(r'<section class="home-conversation">.*?</section>',template,re.S)[0]
        content='<article class="reading-feature approved-blog"><header class="reading-masthead">'+image+'<h1>'+html.escape(a['title'])+'</h1></header><div class="reading-column">'+date+'<div class="reading-spread">'+''.join(sections)+refs+'</div></div></article><div class="reading-actions"><a class="action quiet" href="blog.html">Blog</a></div>'+standard_chat
        page=template.replace(oldslug,a['slug'])
        page=re.sub(r'<link[^>]*data-paper-trail-translation-alternate="true"[^>]*>','',page)
        page=re.sub(r'(<main\b[^>]*>).*?(<dialog\b)',lambda m:m[1]+content+m[2],page,count=1,flags=re.S)
        page=re.sub(r'<title>.*?</title>','<title>'+html.escape(a['meta_title'])+'</title>',page,count=1)
        values={'description':a['description'],'og:title':a['title'],'og:description':a['description'],'og:url':a['canonical'],'og:image':ORIGIN+quote(a['image']),'og:image:alt':a['alt'],'twitter:title':a['title'],'twitter:description':a['description'],'twitter:image':ORIGIN+quote(a['image']),'twitter:image:alt':a['alt']}
        for key,value in values.items():
            page=re.sub(r'(<meta (?:name|property)="'+re.escape(key)+r'" content=")[^"]*(")',lambda m:m[1]+html.escape(value,quote=True)+m[2],page)
        schema={'@context':'https://schema.org','@type':'BlogPosting','@id':a['canonical']+'#article','url':a['canonical'],'mainEntityOfPage':a['canonical'],'headline':a['title'],'description':a['description'],'image':ORIGIN+quote(a['image']),'datePublished':a['date'],'dateModified':a['date'],'inLanguage':'en-US','author':{'@type':'Organization','name':'Paper Trail','url':ORIGIN},'publisher':{'@type':'Organization','name':'Paper Trail','logo':{'@type':'ImageObject','url':ORIGIN+'assets/images/paper-trail-logo.png'}},'citation':[r['url'] for r in a['references']],'articleBody':'\n\n'.join(b['text'] for b in a['article'])}
        page=re.sub(r'<script type="application/ld\+json">.*?</script>',lambda m:'<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=True)+'</script>',page,count=1,flags=re.S)
        write(ROOT/a['slug'],page)
        cards.append('<article class="blog-story approved-blog-card">'+image.replace('loading="eager"','loading="lazy"').replace('fetchpriority="high"','fetchpriority="low"')+'<div><h2>'+html.escape(a['title'])+'</h2>'+date+'<p class="blog-preview">'+html.escape(a['description'])+'</p><a class="action" data-i18n="readNote" href="'+a['slug']+'">Read</a></div></article>')
    return cards

if __name__=='__main__':
    assert (OUT/'preservation-baseline.json').exists(), 'Preservation baseline must complete first'
    cards=render()
    archive=(ROOT/'blog.html').read_text(encoding='utf8')
    excluded=set(REJECTED+[a['slug'] for a in ARTICLES])
    archive=re.sub(r'<article\b[^>]*class="[^"]*\bblog-story\b[^"]*"[^>]*>.*?</article>',lambda m:'' if any('href="'+s+'"' in m[0] for s in excluded) else m[0],archive,flags=re.S)
    archive=archive.replace('<div class="blog-story-list">','<div class="blog-story-list">'+''.join(cards),1)
    def update_schema(m):
        data=json.loads(m[1])
        for node in data.get('@graph',[]):
            if node.get('@type')=='ItemList':
                old=[v for v in node['itemListElement'] if not any(v.get('url','').endswith(s) for s in excluded)]
                new=[{'@type':'ListItem','name':a['title'],'url':a['canonical']} for a in ARTICLES]+old
                for i,v in enumerate(new):v['position']=i+1
                node['itemListElement']=new
                if 'numberOfItems' in node:node['numberOfItems']=len(new)
        return '<script type="application/ld+json">'+json.dumps(data,ensure_ascii=True)+'</script>'
    archive=re.sub(r'<script type="application/ld\+json">(.*?)</script>',update_schema,archive,flags=re.S)
    write(ROOT/'blog.html',archive)
    for path in ROOT.glob('*.xml'):
        xml=path.read_text(encoding='utf8')
        xml=re.sub(r'<url\b[^>]*>.*?</url>',lambda m:'' if any('/'+s+'</loc>' in m[0] for s in REJECTED) else m[0],xml,flags=re.S)
        if path.name=='sitemap.xml':
            for a in ARTICLES:
                if '<loc>'+a['canonical']+'</loc>' not in xml:
                    xml=xml.replace('</urlset>','<url><loc>'+a['canonical']+'</loc><lastmod>2026-11-13</lastmod><image:image><image:loc>'+ORIGIN+a['image']+'</image:loc></image:image></url></urlset>')
        write(path,xml)
    (OUT/'approved-content.json').write_text(json.dumps(ARTICLES,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Installed eight English articles; translation and image validation remain required.')
