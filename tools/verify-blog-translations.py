"""Offline static and local Chromium verification for all saved blog languages."""
from pathlib import Path
from urllib.parse import urlsplit, unquote, urljoin
import argparse, importlib.util, json, re, hashlib
import xml.etree.ElementTree as ET

spec=importlib.util.spec_from_file_location('blog_sync',Path(__file__).with_name('sync-blog-translations.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def require(condition, message):
    if not condition: raise AssertionError(message)

def static_checks():
    pages,pointer,fields,missing,inventory=m.inventory()
    require(inventory['missing_fields']==0,'Untranslated source fields remain')
    urls={node.text for node in ET.parse(m.ROOT/'sitemap-translations.xml').iter() if node.tag.endswith('}loc')}
    results=[]
    for lang in m.LANGUAGES:
        for name,source in pages.items():
            path=m.ROOT/lang/name; markup=path.read_text(encoding='utf-8')
            canonical=m.ORIGIN+lang+'/'+name
            require(f'rel="canonical" href="{canonical}"' in markup,'Canonical mismatch: '+str(path))
            require(f'data-static-locale="{lang}"' in markup,'Locale marker missing')
            require(name in pointer['routes'][lang],'Language route missing')
            require(canonical in urls,'Sitemap route missing')
            require(len(re.findall(r'<h1\b',markup))==1,'Heading hierarchy failure')
            require(len(re.findall(r'rel="alternate" hreflang=',markup))==11,'Language alternate count')
            notices=[(match.start(),match.end()) for match in re.finditer(r'<(?:p|small)\b[^>]*class="article-language"[^>]*>.*?</(?:p|small)>',source.markup,re.S)]
            for a,b,text,attribute in source.slots:
                if any(start<=a<end for start,end in notices): continue
                expected=m.html.escape(fields[m.key(text,lang)]['text'],quote=attribute)
                require(expected in markup,'Missing translated segment '+lang+'/'+name+': '+text[:60])
            base=re.search(r'<base\b[^>]*href="([^"]+)"',markup)
            document_base=urljoin(path.as_uri(),base[1] if base else '')
            for match in re.finditer(r'(?:href|src)="([^"]+)"',markup):
                value=m.html.unescape(match[1]); target=urlsplit(urljoin(document_base,value))
                if target.scheme=='file': require(Path(unquote(target.path.lstrip('/') if re.match(r'^/[A-Za-z]:',target.path) else target.path)).exists(),'Broken local link '+str(path)+': '+value)
            source_schemas=[json.loads(s[1]) for s in re.finditer(r'<script type="application/ld\+json">(.*?)</script>',source.markup,re.S)]
            schemas=[json.loads(s[1]) for s in re.finditer(r'<script type="application/ld\+json">(.*?)</script>',markup,re.S)]
            require(len(schemas)==len(source_schemas),'Schema count changed')
            if name!='blog.html':
                article=next((s for s in schemas if s.get('@type') in {'BlogPosting','Article'}),None)
                if article:
                    require(article['inLanguage']==lang,'Schema language mismatch')
                    require(article.get('mainEntityOfPage')==canonical,'Schema identity mismatch')
                    if 'articleBody' in article: require(bool(article['articleBody'].strip()),'Empty articleBody')
            for source_schema,schema in zip(source_schemas,schemas):
                require(schema.get('citation')==source_schema.get('citation'),'Sources changed')
            source_images=re.findall(r'<img\b[^>]*src="([^"]+)"',source.markup)
            output_images=re.findall(r'<img\b[^>]*src="([^"]+)"',markup)
            require(output_images[:len(source_images)]==source_images,'Original image assignment changed')
            results.append({'language':lang,'page':name,'status':'passed'})
    report={'pages':len(results),'blogs':len(pages)-1,'languages':len(m.LANGUAGES),'missing_fields':0,'checks':results}
    m.save_json(m.OUT/'static-checks.json',report)
    print(json.dumps({k:v for k,v in report.items() if k!='checks'}),flush=True)
    return pages,fields

def browser_checks(pages,fields,archives_only=False):
    from playwright.sync_api import sync_playwright
    results=[]; errors=[]
    with sync_playwright() as p:
        browser=p.chromium.connect_over_cdp('http://127.0.0.1:9264')
        context=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce')
        context.route(re.compile(r'^https?://'),lambda route:route.abort())
        page=context.new_page()
        page.on('pageerror',lambda error:errors.append(str(error)))
        selected={'blog.html':pages['blog.html']} if archives_only else pages
        for width in [320,390,834,1440]:
            page.set_viewport_size({'width':width,'height':1000})
            for lang in m.LANGUAGES:
                for name,source in selected.items():
                    page.goto((m.ROOT/lang/name).as_uri(),wait_until='load')
                    page.evaluate('''async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})))}''')
                    state=page.evaluate('''()=>({locale:document.documentElement.dataset.staticLocale,overflow:document.documentElement.scrollWidth>innerWidth+1,title:document.title,canonical:document.querySelector('link[rel="canonical"]').href,images:[...document.querySelectorAll('.reading-masthead img,.blog-story>img')].map(i=>{const b=i.getBoundingClientRect();return {src:decodeURI(new URL(i.src).pathname),loaded:i.complete&&i.naturalWidth>0,width:b.width,height:b.height,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight}}),paragraphs:[...document.querySelectorAll('.reading-spread p,.reading-spread h2')].map(e=>e.textContent.trim().replace(/\\s+/g,' ')),cards:[...document.querySelectorAll('.blog-story a')].map(a=>a.getAttribute('href')),chat:!!document.querySelector('dialog.chat'),email:!!document.querySelector('dialog.email-dialog')})''')
                    label=f'{lang}/{name} width {width}'
                    require(state['locale']==lang,'Browser locale mismatch '+label)
                    require(not state['overflow'],'Horizontal overflow '+label)
                    require(all(i['loaded'] for i in state['images']),'Broken photo '+label)
                    if name=='blog.html':
                        require(len(state['cards'])==len(pages)-1,'Missing archive cards '+label)
                        require(all(h.startswith(lang+'/') for h in state['cards']),'Archive links left English '+label)
                    else:
                        original=re.search(r'<div class="reading-spread">(.*?)</article>',source.markup,re.S)
                        if original:
                            expected=[]
                            for match in re.finditer(r'<(?:p|h2)\b[^>]*>(.*?)</(?:p|h2)>',original[1],re.S):
                                text=m.normal(m.html.unescape(re.sub('<[^>]+>','',match[1])))
                                expected.append(m.normal(fields[m.key(text,lang)]['text']) if m.eligible(text) else text)
                            require(state['paragraphs']==expected,'Rendered body differs from complete saved translations '+label)
                    for photo in state['images']:
                        if any(fragment in photo['src'] for fragment in ['End-of-Year Receipt Chaos.png','Sorting Receipts in a Cozy Home Office.png','Contractor Reviewing Receipts at Work Van.png','Golden Hour Home Office Bookkeeping.png','Warm Home Office Accounting Workspace.png']):
                            require(abs(photo['width']/photo['height']-photo['naturalWidth']/photo['naturalHeight'])<.015,'Distorted approved photo '+label)
                    if width in [390,1440] and lang in ['es','fa','hy','te','ar'] and (name=='blog.html' or name=='the-receipts-that-disappear-before-the-year-ends.html'):
                        page.screenshot(path=str(m.OUT/f'{lang}-{name[:-5]}-{width}.png'),full_page=True)
                    results.append({'language':lang,'page':name,'width':width,'status':'passed'})
                print(json.dumps({'width':width,'language':lang,'pages_checked':len(results)}),flush=True)
        # Exercise the existing language selector and links, without provider calls.
        for lang in m.LANGUAGES:
            page.goto((m.ROOT/'blog.html').as_uri(),wait_until='load')
            page.select_option('#language',lang)
            page.wait_for_url((m.ROOT/lang/'blog.html').as_uri())
            page.locator('.blog-story a').first.click()
            page.wait_for_url((m.ROOT/lang/'the-receipts-that-disappear-before-the-year-ends.html').as_uri())
        require(not errors,'Browser JavaScript errors: '+str(errors))
        context.close()
    m.save_json(m.OUT/('archive-browser-checks.json' if archives_only else 'browser-checks.json'),{'page_viewport_checks':len(results),'language_switch_checks':9,'javascript_errors':errors,'external_requests_blocked':True,'checks':results})
    print(json.dumps({'page_viewport_checks':len(results),'language_switch_checks':9,'javascript_errors':len(errors)}),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--browser',action='store_true');parser.add_argument('--archives-only',action='store_true');args=parser.parse_args()
    pages,fields=static_checks()
    if args.browser:browser_checks(pages,fields,args.archives_only)
