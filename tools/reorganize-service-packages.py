"""Reorganize approved HTML verbatim; only two new action labels need translation.

Source snapshots make regeneration and byte-for-byte section verification possible.
Never invokes the whole-site or blog rebuild. Paid dispatch is explicitly opt-in.
"""
from pathlib import Path
import argparse, hashlib, html, importlib.util, json, re, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from source_section_policy import Document

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'verification/navigation-reorganization-20261105'
LANGS = ['en','es','fa','hy','zh-CN','ko','tl','te','ru','ar']
KINDS = ['weekly-bookkeeping','monthly-bookkeeping','bookkeeping-repair','accounts-billing','financial-analysis','payroll']
NAMES = ['Weekly Bookkeeping','Monthly Bookkeeping','Bookkeeping Repair','Accounts & Billing','Financial Analysis','Payroll']
SERVICES = ['weekly-bookkeeping.html','paper-trail-monthly-bookkeeping.html','paper-trail-services.html','accounts-billing.html','financial-analysis.html','payroll.html']
ORIGIN = 'https://www.papertrailusa.com/'

def read(path): return path.read_text(encoding='utf-8')
def save(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or read(path) != text: path.write_text(text, encoding='utf-8', newline='')
def dump(path, obj): save(path, json.dumps(obj, ensure_ascii=False, indent=2)+'\n')
def sha(text): return hashlib.sha256(text.encode()).hexdigest()
def prefix(lang): return '' if lang == 'en' else lang+'/'
def nodes(text): return Document(text).nodes
def raw(text, node): return text[node['start']:node['end']]
def text(node): return ' '.join(''.join(node['text']).split())
def within(node, parent): return parent['start'] <= node['start'] < parent['end']
def first(ns, tag=None, cls=None):
    return next(n for n in ns if (not tag or n['tag']==tag) and (not cls or cls in n['attrs'].get('class','').split()))
def module():
    spec=importlib.util.spec_from_file_location('saved_translations',ROOT/'tools/paper-trail-translations.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def capture():
    path=BASE/'approved-source.json'
    if path.exists():
        source=json.loads(read(path))
        for lang in LANGS:
            if 'page_shell' not in source['languages'][lang]:
                s=read(ROOT/prefix(lang)/'packages.html')
                assert sha(s)==source['languages'][lang]['source_sha256']
                source['languages'][lang]['page_shell']=s
        dump(path,source)
        return source
    original_js=read(ROOT/'assets/navigation-ready.js')
    labels=json.loads(re.findall(r'const labels=(\{"en": \{"All Packages".*?\});',original_js)[-1])
    source={'languages':{},'preserved_files':{},'menu_labels':labels}
    for lang in LANGS:
        p=prefix(lang); markup=read(ROOT/p/'packages.html'); ns=nodes(markup)
        sections={k:raw(markup,next(n for n in ns if n['attrs'].get('id')==k)) for k in KINDS+['bundle-save']}
        extras=[raw(markup,n) for n in ns if n['attrs'].get('class')=='package-bottom' or 'data-payroll-boundary' in n['attrs']]
        source['languages'][lang]={'sections':sections,'extras':extras,'source_sha256':sha(markup),'page_shell':markup}
        for name in SERVICES+['all-bundles.html']:
            source['preserved_files'][p+name]=sha(read(ROOT/p/name))
    dump(path,source);return source

def fields_for_labels(translate):
    m=module(); fields=m.load_cache()
    newfile=ROOT/'assets/locales/service-package-actions.json'
    if newfile.exists(): fields.update(json.loads(read(newfile)))
    sources=['View Packages','View Bundles']
    missing={l:[s for s in sources if m.key(s,l) not in fields] for l in LANGS[1:]}
    missing={l:s for l,s in missing.items() if s}
    if missing and translate:
        ledger=m.private_path('DOMMYDOM_SHARED_BUDGET_DB','shared-usage.sqlite')
        budget=m.ExistingBudget(ledger) if ledger.exists() else m.Budget(ledger)
        report={'successful_characters':0,'failures':[],'google_calls':0,'actual_characters_sent':0}
        m.dispatch_jobs(missing,fields,report,budget,m.preflight())
        m.atomic(m.CACHE,m.encoded(fields))
        dump(BASE/'new-text-usage.json',report)
    pending=[(s,l) for l in LANGS[1:] for s in sources if m.key(s,l) not in fields]
    if pending: raise RuntimeError('Missing new action labels; use --translate-new-text for the authorized 225 source characters across nine languages')
    dump(newfile,{m.key(s,l):fields[m.key(s,l)] for l in LANGS[1:] for s in sources})
    receipts={}
    for lang in LANGS[1:]:
        for source in sources:
            field=fields[m.key(source,lang)]
            if field.get('receipt'):
                receipt=m.RECEIPTS/field['receipt']
                if receipt.exists():receipts[field['receipt']]=json.loads(read(receipt))
    usage=BASE/'new-text-usage.json'
    if receipts or not usage.exists():
        dump(usage,{'new_text':sources,'languages':LANGS[1:],'completed_provider_calls':len(receipts) if receipts else None,'source_characters_sent':sum(r['characters'] for r in receipts.values()) if receipts else None,'existing_package_sections_translated':0,'actual_provider_charge_usd':None})
    def label(s,l): return s if l=='en' else fields[m.key(s,l)]['text']
    return label

def shell(lang, route, title, main, template=None, styles=''):
    p=prefix(lang); s=template or read(ROOT/p/'notes.html')
    ns=nodes(s); old=first(ns,'main')
    if template is None:
        chat=first(ns,'div','page-conversation')
        main=main.replace('</main>',s[chat['start']:old['end']-len('</main>')]+'</main>')
    s=s[:old['start']]+main+s[old['end']:]
    if route.endswith('-packages.html'):
        s=re.sub(r'<body\b[^>]*>', '<body class="pt-preview pt-interior pt-packages">',s,count=1)
    s=re.sub(r'<link\b[^>]*rel="preload"[^>]*>', '', s)
    s=re.sub(r'<link\b[^>]*rel="alternate"[^>]*>', '', s)
    s=re.sub(r'<title>.*?</title>', '<title>'+html.escape(title)+' | Paper Trail</title>',s,flags=re.S)
    # Metadata describes the actual page; never carry Notes article/category schema.
    s=re.sub(r'<script type="application/ld\+json">.*?</script>','',s,flags=re.S)
    s=re.sub(r'(<meta\b[^>]*(?:name="description"|property="og:(?:title|description)"|name="twitter:(?:title|description)")[^>]*content=")[^"]*',lambda m:m[1]+html.escape(title,quote=True),s)
    s=re.sub(r'(<link\b[^>]*rel="canonical"[^>]*href=")[^"]*',lambda m:m[1]+ORIGIN+p+route,s)
    s=re.sub(r'(<meta\b[^>]*property="og:url"[^>]*content=")[^"]*',lambda m:m[1]+ORIGIN+p+route,s)
    alternatives=''.join('<link rel="alternate" hreflang="'+l+'" href="'+ORIGIN+prefix(l)+route+'" data-paper-trail-translation-alternate="true">' for l in LANGS)
    alternatives+='<link rel="alternate" hreflang="x-default" href="'+ORIGIN+route+'" data-paper-trail-translation-alternate="true">'
    css='<link rel="stylesheet" href="assets/billing-refinements.css"><link rel="stylesheet" href="assets/service-package-overviews.css">'
    s=s.replace('</head>',css+styles+alternatives+'</head>')
    return s

def preview(section):
    ns=nodes(section); plans=[n for n in ns if n['tag']=='article' and 'package-plan' in n['attrs'].get('class','').split()]
    result=[]
    for plan in plans:
        children=[n for n in ns if within(n,plan)]
        heading=first(children,'h3'); price=next((n for n in children if 'plan-price' in n['attrs'].get('class','').split()),None)
        prices=[price] if price else [n for n in children if n['tag']=='p' and not any(a['tag']=='a' for a in n['children'])]
        result.append('<div class="category-preview-tier">'+raw(section,heading)+''.join(raw(section,n) for n in prices)+'</div>')
    enterprise=next((n for n in ns if 'package-enterprise' in n['attrs'].get('class','').split()),None)
    if enterprise: result.append('<div class="category-preview-tier">'+raw(section,first([n for n in ns if within(n,enterprise)],'h3'))+'</div>')
    if not result:
        # Weekly and repair are approved custom quotes, not invented tiers.
        heading=first(ns,'h2'); result.append('<p>'+html.escape(text(heading))+'</p>')
        repair=next((n for n in ns if n['attrs'].get('class')=='repair-package-heading'),None)
        if repair:
            quote=first([n for n in ns if within(n,repair)],'span');result.append(raw(section,quote))
    return ''.join(result)

def build(source,label):
    menu={}
    for lang in LANGS:
        p=prefix(lang); original=source['languages'][lang]; labels=source['menu_labels'][lang]
        notes=read(ROOT/p/'notes.html'); ns=nodes(notes)
        nav=first(ns,'nav','pt-nav'); navnodes=[n for n in ns if within(n,nav)]
        menu[lang]={s:label(s,lang) for s in ['All Services','All Packages','Services','Packages']}
        menu[lang].update(labels)
        for key,route in [('Home','index.html'),('About','about.html'),('Notes','notes.html'),('Blog','blog.html'),('Contact Us','areas-we-serve.html')]:
            a=next((n for n in navnodes if n['tag']=='a' and n['attrs'].get('href','').endswith(route)),None)
            menu[lang][key]=text(a) if a else label(key,lang)
        cards=[]; servicecards=[]
        for kind,name,service in zip(KINDS,NAMES,SERVICES):
            section=original['sections'][kind]; route=kind+'-packages.html'
            title=labels[name]
            extras=''.join(e for e in original['extras'] if 'data-payroll-boundary' not in e or kind=='payroll')
            main='<main id="main" class="packages-main"><header class="packages-opening"><h1>'+html.escape(title)+' — '+html.escape(label('Packages',lang))+'</h1></header>'+section+extras+'</main>'
            styles=''.join(re.findall(r'<style\b[^>]*>.*?</style>',original['page_shell'],re.S))
            save(ROOT/p/route,shell(lang,route,title+' | '+label('Packages',lang),main,styles=styles))
            cards.append('<article class="category-overview-card" id="'+kind+'"><h2>'+html.escape(title)+'</h2><div class="category-preview">'+preview(section)+'</div><a class="action" href="'+p+route+'">'+html.escape(label('View Packages',lang))+'</a></article>')
            servicesource=read(ROOT/p/service); sn=nodes(servicesource); sm=first(sn,'main'); candidates=[n for n in sn if within(n,sm)]
            desc=next((n for n in candidates if n['tag']=='p' and n['attrs'].get('class')=='summary'),None)
            if desc is None: desc=first(candidates,'p')
            description=raw(servicesource,desc)
            servicecards.append('<article class="service-overview-card"><h2>'+html.escape(title)+'</h2>'+description+'<a class="action" href="'+p+service+'">'+html.escape(label('View Service',lang))+'</a></article>')
        bundle=original['sections']['bundle-save']; bn=nodes(bundle)
        bundlepreview=''
        for ident in ['bundle-1','bundle-2']:
            b=raw(bundle,next(n for n in bn if n['attrs'].get('id')==ident));bns=nodes(b)
            bundlepreview+='<section class="bundle-preview">'+raw(b,first(bns,'h2'))+preview(b)+'</section>'
        cards.append('<article class="category-overview-card" id="bundle-save"><h2>'+html.escape(labels['Bundle & Save'])+'</h2>'+bundlepreview+'<a class="action" href="'+p+'all-bundles.html">'+html.escape(label('View Bundles',lang))+'</a></article>')
        main='<main id="main" class="packages-main"><h1 class="center-title">'+html.escape(label('All Packages',lang))+'</h1><div class="package-overview-grid">'+''.join(cards)+'</div></main>'
        save(ROOT/p/'packages.html',shell(lang,'packages.html',label('All Packages',lang),main,template=original['page_shell']))
        # Reuse an approved professional photograph and its exact localized alt text.
        weekly=read(ROOT/p/SERVICES[0]); wn=nodes(weekly); img=first([n for n in wn if n['tag']=='img' and 'weekly-bookkeeping-20261031.webp' in n['attrs'].get('src','')])
        photo=raw(weekly,img)
        main='<main id="main"><h1 class="center-title">'+html.escape(label('All Services',lang))+'</h1><div class="services-intro-photo">'+photo+'</div><div class="topic-index services-overview">'+''.join(servicecards)+'</div></main>'
        save(ROOT/p/'all-services.html',shell(lang,'all-services.html',label('All Services',lang),main))
    save(ROOT/'assets/navigation-ready.js','window.PAPER_TRAIL_SERVICE_MENU='+json.dumps(menu,ensure_ascii=False)+';\n'+read(ROOT/'assets/service-package-navigation.js'))
    inventory=json.loads(read(ROOT/'tools/production-pages.json'))
    routes=['all-services.html']+[k+'-packages.html' for k in KINDS]
    inventory['english']=sorted(set(inventory['english']+routes))
    for l in LANGS[1:]: inventory['locales'][l]=sorted(set(inventory['locales'][l]+routes))
    dump(ROOT/'tools/production-pages.json',inventory)
    rfile=ROOT/'assets/translation-workflow/routes.js';rs=read(rfile); data=json.loads(rs[rs.index('=')+1:].strip().rstrip(';'))
    for l in LANGS[1:]:data[l]=sorted(set(data[l]+routes))
    save(rfile,'window.paperTrailTranslationRoutes='+json.dumps(data,ensure_ascii=False)+';\n')
    # Extend the saved release pointer without touching translated field content.
    pointerfile=ROOT/'assets/translation-workflow/current.json';pointer=json.loads(read(pointerfile))
    for l in LANGS[1:]:pointer['routes'][l]=sorted(set(pointer['routes'][l]+routes))
    dump(pointerfile,pointer)
    for mapname,langs in [('sitemap.xml',['en']),('sitemap-translations.xml',LANGS[1:])]:
        path=ROOT/mapname;s=read(path); additions=''
        if 'xmlns:xhtml=' not in s:s=s.replace('<urlset ','<urlset xmlns:xhtml="http://www.w3.org/1999/xhtml" ',1)
        for l in langs:
            for route in routes:
                url=ORIGIN+prefix(l)+route
                if '<loc>'+url+'</loc>' not in s:
                    additions+='<url><loc>'+url+'</loc>'+''.join('<xhtml:link rel="alternate" hreflang="'+a+'" href="'+ORIGIN+prefix(a)+route+'"/>' for a in LANGS)+'<xhtml:link rel="alternate" hreflang="x-default" href="'+ORIGIN+route+'"/></url>\n'
        save(path,s.replace('</urlset>',additions+'</urlset>'))
    verify(source)

def verify(source):
    import xml.etree.ElementTree as ET
    for path,digest in source['preserved_files'].items(): assert sha(read(ROOT/path))==digest,'Preserved source changed: '+path
    count=0; route_checks=0
    pointer=json.loads(read(ROOT/'assets/translation-workflow/current.json'))
    urls={n.text for name in ['sitemap.xml','sitemap-translations.xml'] for n in ET.parse(ROOT/name).iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
    for lang in LANGS:
        p=prefix(lang)
        for kind in KINDS:
            original=source['languages'][lang]['sections'][kind]
            output=read(ROOT/p/(kind+'-packages.html'))
            assert original in output, 'Section differs: '+lang+'/'+kind
            count+=1
        for route in ['all-services.html','packages.html']+[k+'-packages.html' for k in KINDS]:
            markup=read(ROOT/p/route); ns=nodes(markup); url=ORIGIN+p+route
            assert f'rel="canonical" href="{url}"' in markup and url in urls, 'SEO route mismatch: '+p+route
            alternate={n['attrs'].get('hreflang'):n['attrs'].get('href') for n in ns if n['tag']=='link' and n['attrs'].get('rel')=='alternate'}
            assert len(alternate)==11 and alternate['x-default']==ORIGIN+route,'Alternate count mismatch: '+p+route
            for language in LANGS:assert alternate[language]==ORIGIN+prefix(language)+route,'Alternate route mismatch'
            if lang!='en':assert route in pointer['routes'][lang],'Selector route missing'
            route_checks+=1
        services=read(ROOT/p/'all-services.html'); sn=nodes(services)
        servicecards=[n for n in sn if n['attrs'].get('class')=='service-overview-card']
        assert len(servicecards)==6
        for card,service in zip(servicecards,SERVICES):
            assert first([n for n in sn if within(n,card)],'a')['attrs']['href']==p+service,'Service card destination mismatch'
            description=first([n for n in sn if within(n,card)],'p')
            assert raw(services,description) in read(ROOT/p/service),'Service description differs from approved language source'
        packages=read(ROOT/p/'packages.html');pn=nodes(packages)
        cards=[n for n in pn if n['attrs'].get('class')=='category-overview-card']
        assert [n['attrs']['id'] for n in cards]==KINDS+['bundle-save'],'Package card order mismatch'
        for card,route in zip(cards,[k+'-packages.html' for k in KINDS]+['all-bundles.html']):
            assert first([n for n in pn if within(n,card)],'a')['attrs']['href']==p+route,'Package card destination mismatch'
    dump(BASE/'section-integrity.json',{'verbatim_sections':count,'unchanged_service_and_bundle_files':len(source['preserved_files']),'canonical_hreflang_and_selector_checks':route_checks,'sitemap_page_urls':len(urls),'section_sha256':{l:{k:sha(source['languages'][l]['sections'][k]) for k in KINDS} for l in LANGS}})
    print(json.dumps({'verbatim_sections':count,'preserved_files':len(source['preserved_files']),'seo_and_selector_checks':route_checks}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--translate-new-text',action='store_true');parser.add_argument('--verify',action='store_true');args=parser.parse_args()
    source=capture()
    if args.verify:verify(source)
    else:build(source,fields_for_labels(args.translate_new_text))
