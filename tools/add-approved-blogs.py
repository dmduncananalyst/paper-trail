"""Install the two approved PDF articles locally, without editing their prose."""
from pathlib import Path
import base64, hashlib, html, json, re, shutil, struct, zlib
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/approved-blogs-20261020'
OUT.mkdir(parents=True, exist_ok=True)
PDF = Path(r'C:\Users\Owner\Downloads\Paper_Trail_Two_Blogs_UPDATED_PHOTO_NAMES.pdf')
raw = PDF.read_bytes()
streams = {}
for m in re.finditer(rb'(\d+) 0 obj\s*<<((?:(?!endobj).)*?)>>\s*stream\r?\n(.*?)\r?\nendstream', raw, re.S):
    d, data = m[2], m[3]
    if b'/Type/EmbeddedFile' in d:
        continue
    if b'ASCII85Decode' in d:
        data = base64.a85decode(data, adobe=True)
    if b'FlateDecode' in d:
        data = zlib.decompress(data)
    streams[int(m[1])] = data.decode('cp1252')

def literal(s):
    def sub(m):
        v=m[1]
        if re.fullmatch(r'[0-7]{1,3}',v):
            return bytes([int(v,8)]).decode('cp1252')
        return {'n':'\n','r':'\r','t':'\t','b':'\b','f':'\f'}.get(v,v)
    return re.sub(r'\\([0-7]{1,3}|.)',sub,s)

def blocks(n):
    result=[]
    for m in re.finditer(r'BT\b(.*?)\bET', streams[n], re.S):
        block=m[1]
        text=' '.join(literal(t[1]) for t in re.finditer(r'\(((?:\\.|[^\\)])*)\)\s*Tj',block))
        if text:
            result.append({'text':text,'heading':bool(re.search(r'/F2\s+12\s+Tf',block))})
    return result

assignments=[
    (14,10,16,'the-real-cost-of-monthly-bookkeeping-for-small-businesses.html',
     'Golden Hour Home Office Bookkeeping.png',
     'Business owner reviewing bookkeeping records with a calculator beside a laptop'),
    (17,11,18,'the-point-when-managing-your-own-books-stops-making-sense.html',
     'Warm Home Office Accounting Workspace.png',
     'Home office desk with organized financial records, a laptop, and a monthly review notebook'),
]
template=(ROOT/'profit-vs-cash-flow-business-money.html').read_text(encoding='utf-8')
archive=(ROOT/'blog.html').read_text(encoding='utf-8')
origin='https://www.papertrailusa.com/'
cards=[]; manifest=[]
for first,last,image_stream,slug,filename,alt in assignments:
    a,b=blocks(first),blocks(last)
    title=a[1]['text']
    description=a[3]['text'].removeprefix('SEO meta description: ')
    hexname=re.search(r'<([0-9a-fA-F]+)>',streams[image_stream])[1]
    assert bytes.fromhex(hexname).decode()==filename
    assert title not in re.sub(r'<script\b.*?</script>','',archive,flags=re.S)
    assert not (ROOT/slug).exists(), 'Existing article must not be overwritten'
    start=next(i for i,x in enumerate(a) if x['heading'])
    body=a[start:]+b
    body=[x for x in body if not x['text'].startswith('Developer placement:')]
    # A paragraph continues from PDF page three onto page four.
    if not a[-1]['heading'] and not b[0]['heading']:
        boundary=len(a[start:])-1
        body[boundary]['text']+=' '+body[boundary+1]['text']
        body.pop(boundary+1)
    references_at=next(i for i,x in enumerate(body) if x['text']=='Sources and references')
    article=body[:references_at]
    references=[]
    for x in body[references_at+1:]:
        label,url=x['text'].rsplit(' ',1)
        assert url.startswith('https://')
        references.append({'label':label,'url':url})
    photo=ROOT/'assets/photos'/filename
    source=Path(r'C:\Users\Owner\OneDrive\Desktop')/filename
    shutil.copyfile(source,photo)
    image_bytes=photo.read_bytes(); width,height=struct.unpack('>II',image_bytes[16:24])
    assert image_bytes==source.read_bytes()
    src='assets/photos/'+filename
    image=f'<img fetchpriority="high" height="{height}" width="{width}" src="{html.escape(src)}" alt="{html.escape(alt)}" loading="eager">'
    sections=[]
    for x in article:
        if x['heading']:
            if sections:sections.append('</div></section>')
            sections.append('<section class="story-section"><h2>'+html.escape(x['text'])+'</h2><div class="section-copy">')
        else:sections.append('<p>'+html.escape(x['text'])+'</p>')
    sections.append('</div></section>')
    refs='<section class="reference-list"><h2>Sources and references</h2><ol>'+''.join('<li><a href="'+r['url']+'" target="_blank" rel="noopener">'+html.escape(re.sub(r'^\d+\. ','',r['label']))+'</a></li>' for r in references)+'</ol></section>'
    content='<article class="reading-feature approved-blog"><header class="reading-masthead">'+image+'<h1>'+html.escape(title)+'</h1></header><div class="reading-column"><p class="publication-date">Published <time datetime="2026-10-20">10/20/2026</time></p><div class="reading-spread">'+''.join(sections)+refs+'</div></div></article><div class="reading-actions"><a class="action" href="monthly-bookkeeping-review.html">Monthly Bookkeeping Review</a><a class="action quiet" href="blog.html">Blog</a></div>'
    page=template
    page=re.sub(r'<title>.*?</title>','<title>'+html.escape(title)+'</title>',page,count=1)
    for attr,name,value in [('name','description',description),('property','og:title',title),('property','og:description',description)]:
        page=re.sub(r'(<meta '+attr+'="'+name+r'" content=")[^"]*(")',lambda m:m[1]+html.escape(value,quote=True)+m[2],page)
    page=page.replace('profit-vs-cash-flow-business-money.html',slug)
    page=re.sub(r'<link[^>]*data-paper-trail-translation-alternate="true"[^>]*>','',page)
    page=re.sub(r'(<main\b[^>]*>).*?(<dialog\b)',lambda m:m[1]+content+m[2],page,count=1,flags=re.S)
    schema={'@context':'https://schema.org','@type':'BlogPosting','@id':origin+slug+'#article','url':origin+slug,'mainEntityOfPage':origin+slug,'headline':title,'description':description,'image':origin+quote(src),'datePublished':'2026-10-20','dateModified':'2026-10-20','inLanguage':'en-US','author':{'@type':'Organization','name':'Paper Trail','url':origin},'publisher':{'@type':'Organization','name':'Paper Trail','logo':{'@type':'ImageObject','url':origin+'assets/images/paper-trail-logo.png'}},'citation':[r['url'] for r in references],'articleBody':'\n\n'.join(x['text'] for x in article)}
    page=re.sub(r'<script type="application/ld\+json">.*?</script>',lambda _: '<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=True)+'</script>',page,count=1,flags=re.S)
    page=page.replace('</head>','<meta property="og:url" content="'+origin+slug+'"><meta property="og:image" content="'+origin+quote(src)+'"><link rel="stylesheet" href="assets/approved-blogs.css"></head>')
    (ROOT/slug).write_text(page,encoding='utf-8')
    cards.append('<article class="blog-story approved-blog-card">'+image+'<div><h2>'+html.escape(title)+'</h2><p class="publication-date">Published <time datetime="2026-10-20">10/20/2026</time></p><p class="blog-preview">'+html.escape(description)+'</p><a class="action" data-i18n="readNote" href="'+slug+'">Read</a></div></article>')
    manifest.append({'title':title,'slug':slug,'description':description,'photo':filename,'width':width,'height':height,'sha256':hashlib.sha256(image_bytes).hexdigest(),'article':article,'references':references})
archive=archive.replace('<div class="blog-story-list">','<div class="blog-story-list">'+''.join(cards),1)
archive=archive.replace('</head>','<link rel="stylesheet" href="assets/approved-blogs.css"></head>')
def update_archive_schema(m):
    data=json.loads(m[1])
    for node in data.get('@graph',[]):
        if node.get('@type')=='ItemList':
            old=node['itemListElement']
            new=[{'@type':'ListItem','position':i+1,'name':x['title'],'url':origin+x['slug']} for i,x in enumerate(manifest)]
            for x in old:x['position']+=len(new)
            node['itemListElement']=new+old
            if 'numberOfItems' in node:node['numberOfItems']=len(new+old)
    return '<script type="application/ld+json">'+json.dumps(data,ensure_ascii=True)+'</script>'
archive=re.sub(r'<script type="application/ld\+json">(.*?)</script>',update_archive_schema,archive,flags=re.S)
(ROOT/'blog.html').write_text(archive,encoding='utf-8')
sitemap=(ROOT/'sitemap.xml').read_text(encoding='utf-8')
entries=''.join('  <url>\n    <loc>'+origin+x['slug']+'</loc>\n    <lastmod>2026-10-20</lastmod>\n    <image:image><image:loc>'+origin+quote('assets/photos/'+x['photo'])+'</image:loc></image:image>\n  </url>\n' for x in manifest)
(ROOT/'sitemap.xml').write_text(sitemap.replace('</urlset>',entries+'</urlset>'),encoding='utf-8')
(ROOT/'assets/approved-blogs.css').write_text('/* Preserve the complete approved photographs at their natural aspect ratio. */\n.approved-blog .reading-masthead img,.blog-story.approved-blog-card>img{width:100%;height:auto;max-width:100%;aspect-ratio:auto;object-fit:contain;align-self:center}\n',encoding='utf-8')
(OUT/'approved-content.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps([{'title':x['title'],'photo':x['photo']} for x in manifest],indent=2))
