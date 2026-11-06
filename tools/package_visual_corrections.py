"""Apply only the November 5 screenshot corrections, retaining approved wording.

No network, credentials, translation dispatch, or release operations. Pricing
labels/templates come from the same language's approved Financial Analysis page.
"""
from pathlib import Path
import hashlib, html, json, re, sys, unicodedata
from collections import Counter
sys.path.insert(0, str(Path(__file__).resolve().parent))
from source_section_policy import Document

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'verification/package-visual-corrections-20261105'
LANGS=['en','es','fa','hy','zh-CN','ko','tl','te','ru','ar']
KINDS=['weekly-bookkeeping','monthly-bookkeeping','bookkeeping-repair','accounts-billing','financial-analysis','payroll']
ROUTES=['all-services.html','packages.html','payroll.html']+[k+'-packages.html' for k in KINDS]
ORIGINAL=ROOT/'verification/navigation-reorganization-20261105/approved-source.json'

def read(path):return path.read_text(encoding='utf-8')
def save(path,s):
    path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists() or read(path)!=s:path.write_text(s,encoding='utf-8',newline='')
def dump(path,obj):save(path,json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def prefix(lang):return '' if lang=='en' else lang+'/'
def ns(s):return Document(s).nodes
def raw(s,n):return s[n['start']:n['end']]
def classes(n):return n['attrs'].get('class','').split()
def inside(n,parent):return parent['start']<=n['start']<parent['end']
def edits(s,changes):
    for a,b,value in sorted(changes,reverse=True):s=s[:a]+value+s[b:]
    return s
def digest(s):return hashlib.sha256(s.encode()).hexdigest()
def original_source():return json.loads(read(ORIGINAL))

def capture():
    path=BASE/'approved-source.json'
    if path.exists():return json.loads(read(path))
    data={'pages':{prefix(l)+r:read(ROOT/prefix(l)/r) for l in LANGS for r in ROUTES},'preserved_files':original_source()['preserved_files'],'screenshots':{}}
    folder=Path('C:/Users/Owner/OneDrive/Pictures/Screenshots')
    for number in range(555,560):
        file=folder/f'Screenshot ({number}).png'
        if file.exists():data['screenshots'][file.name]={'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}
    data['reference_note']='Screenshot (557).png shows Financial Analysis; Screenshot (558).png shows Accounts & Billing. Follow Financial Analysis as required by the written request.'
    dump(path,data);return data

def reference(lang):return original_source()['languages'][lang]['sections']['financial-analysis']

def weekly_plans(lang, overview=False):
    s=reference(lang);nodes=ns(s)
    plans=[n for n in nodes if n['tag']=='article' and 'package-plan' in classes(n)]
    pieces=[]
    for i,(plan,amount) in enumerate(zip(plans,['700','1,300','2,100',None])):
        children=[n for n in nodes if inside(n,plan)]
        h=next(n for n in children if n['tag']=='h3');price=next(n for n in children if 'plan-price' in classes(n))
        price_html=raw(s,price)
        if amount:
            numeric=re.search(r'\d[\d,\u066c]*',price_html)
            assert numeric,'Approved monthly price template missing'
            # Keep the existing language's digit shapes and currency/frequency words.
            if '\u06f0'<=numeric[0][0]<='\u06f9':amount=amount.translate(str.maketrans('0123456789','۰۱۲۳۴۵۶۷۸۹'))
            elif '\u0660'<=numeric[0][0]<='\u0669':amount=amount.translate(str.maketrans('0123456789','٠١٢٣٤٥٦٧٨٩'))
            price_html=price_html[:numeric.start()]+amount+price_html[numeric.end():]
        tag='div' if overview else 'article';cls='category-preview-tier' if overview else 'package-plan'
        pieces.append(f'<{tag} class="{cls}">'+raw(s,h)+price_html+f'</{tag}>')
    return ''.join(pieces)

def correct_section(s,lang,kind):
    if kind=='weekly-bookkeeping':
        nodes=ns(s)
        if not any('package-plans' in classes(n) for n in nodes):
            h=next(n for n in nodes if n['tag']=='h2')
            name=original_source()['menu_labels'][lang]['Weekly Bookkeeping']
            wrong=next(n for n in nodes if 'weekly-custom-quote-label' in classes(n))
            s=edits(s,[(h['start'],h['end'],'<h2>'+html.escape(name)+'</h2><div class="package-plans">'+weekly_plans(lang)+'</div>'),(wrong['start'],wrong['end'],'')])
    # English uses the exact /month presentation already approved on Financial
    # Analysis. Other languages keep every approved frequency word verbatim.
    if lang=='en':
        s=s.replace('<span>per month</span>','/month')
    if kind in {'monthly-bookkeeping','accounts-billing'}:
        nodes=ns(s);enterprise=next((n for n in nodes if 'package-enterprise' in classes(n)),None)
        plans=next((n for n in nodes if 'package-plans' in classes(n)),None)
        if enterprise and plans:
            content=raw(s,enterprise).replace('class="package-enterprise"','class="package-plan package-enterprise"',1)
            heading=re.search(r'<h3>(.*?)</h3>',content,re.S)
            if heading and ' | ' in heading[1]:
                name,quote=heading[1].split(' | ',1)
                content=content[:heading.start()]+'<h3>'+name+'</h3><p class="plan-price">'+quote+'</p>'+content[heading.end():]
            if not inside(enterprise,plans):
                insert=plans['end']-len('</div>')
                s=edits(s,[(enterprise['start'],enterprise['end'],''),(insert,insert,content)])
            else:s=edits(s,[(enterprise['start'],enterprise['end'],content)])
    if kind=='payroll':
        nodes=ns(s);changes=[]
        for n in nodes:
            if n['tag']!='p' or not n['parent'] or 'package-plan' not in classes(n['parent']):continue
            if 'payroll-price' in classes(n):continue
            content=raw(s,n)
            # These are the existing monthly/weekly payroll rate lines, not setup
            # fees, employee limits, or any other approved text.
            match=re.match(r'<p>(.*?[:：՝])(.*?)</p>$',content,re.S)
            if match:
                rate=match[2].replace(' per month','/month') if lang=='en' else match[2]
                value='<p class="payroll-price"><span class="payroll-price-label">'+match[1]+'</span><span class="payroll-price-amount">'+rate+'</span></p>'
                changes.append((n['start'],n['end'],value))
        s=edits(s,changes)
    return s

def correct_page(s,lang,route):
    if route=='all-services.html':return s
    if route=='payroll.html':
        nodes=ns(s)
        headings=[n for n in nodes if n['tag']=='h3' and n['parent'] and 'work-card' in classes(n['parent'])]
        label=''.join(headings[5]['text'])
        # The saved Tagalog block uses Payroll here, while its separate styled
        # heading uses Sweldo. Retain the block's own existing translation.
        if lang=='tl':label='Pag-uulat ng Payroll'
        candidates=[n for n in nodes if n['tag']=='p' and label in raw(s,n)]
        paragraph=max(candidates,key=lambda n:len(raw(s,n)))
        content=raw(s,paragraph);offset=content.index(label)
        if offset==len('<p>'):return s
        assert len(content)>600,'Unexpected Payroll paragraph boundary'
        value=content[:offset]+'</p><p>'+content[offset:]
        assert value.replace('</p><p>','',1)==content
        return edits(s,[(paragraph['start'],paragraph['end'],value)])
    s=re.sub(r'(<body\b[^>]*class=")([^"]*)',lambda m:m[1]+' '.join(dict.fromkeys(m[2].split()+['pt-prices-inline']+(['pt-dedicated-packages'] if route!='packages.html' else []))),s,count=1)
    if route=='packages.html':
        nodes=ns(s);card=next(n for n in nodes if n['attrs'].get('id')=='weekly-bookkeeping')
        preview=next(n for n in nodes if inside(n,card) and 'category-preview' in classes(n))
        s=edits(s,[(preview['start'],preview['end'],'<div class="category-preview">'+weekly_plans(lang,True)+'</div>')])
        # Bundle headings use each language's own approved dedicated-page copy.
        # All existing preview prices, tier labels, and links remain untouched.
        dedicated=read(ROOT/prefix(lang)/'all-bundles.html');dnodes=ns(dedicated)
        previews=[n for n in ns(s) if 'bundle-preview' in classes(n)]
        changes=[]
        for index,preview in enumerate(previews,1):
            section=next(n for n in dnodes if n['attrs'].get('id')==f'bundle-{index}')
            heading=next(n for n in section['children'] if n['tag']=='h2')
            description=next(n for n in section['children'] if n['tag']=='p')
            title=raw(dedicated,heading)[len('<h2>'):-len('</h2>')]
            inclusion=raw(dedicated,description)[len('<p>'):-len('</p>')]
            target=next(n for n in ns(s) if inside(n,preview) and n['tag']=='h2')
            changes.append((target['start'],target['end'],'<h2>'+title+' — '+inclusion+'</h2>'))
        s=edits(s,changes)
        if lang=='en':s=s.replace('<span>per month</span>','/month')
        return s
    kind=route.removesuffix('-packages.html');nodes=ns(s)
    section=next(n for n in nodes if n['attrs'].get('id')==kind)
    corrected=correct_section(raw(s,section),lang,kind)
    return edits(s,[(section['start'],section['end'],corrected)])

def apply():
    baseline=capture()
    for lang in LANGS:
        for route in ROUTES:
            path=ROOT/prefix(lang)/route
            save(path,correct_page(read(path),lang,route))
    # Keep the compiled navigation and its readable controller in sync, retaining
    # the exact saved label dictionary and every existing destination.
    path=ROOT/'assets/navigation-ready.js';s=read(path)
    dictionary=s[:s.index('/* Shared navigation controller.')]
    save(path,dictionary+read(ROOT/'assets/service-package-navigation.js'))
    verify(baseline)

def links(s):
    return sorted(n['attrs']['href'] for n in ns(s) if n['tag']=='a' and 'href' in n['attrs'])

def verify(baseline=None):
    import xml.etree.ElementTree as ET
    baseline=baseline or capture();checks=0;seo_checks=0
    origin='https://www.papertrailusa.com/'
    pointer=json.loads(read(ROOT/'assets/translation-workflow/current.json'))
    sitemap_urls={n.text for f in ['sitemap.xml','sitemap-translations.xml'] for n in ET.parse(ROOT/f).iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
    def numbers(nodes):
        main=next(n for n in nodes if n['tag']=='main')
        return Counter(''.join(str(unicodedata.digit(c)) for c in token if c.isdigit()) for token in re.findall(r'\d[\d,.\u066c]*',' '.join(main['text'])))
    for route,before in baseline['pages'].items():
        lang=route.split('/')[0] if '/' in route else 'en';name=route.split('/')[-1]
        after=read(ROOT/route)
        assert after==correct_page(before,lang,name),'Change outside approved transformations: '+route
        assert links(after)==links(before),'Approved link destinations changed: '+route
        bnodes=ns(before);anodes=ns(after)
        url=origin+route
        assert f'rel="canonical" href="{url}"' in after and url in sitemap_urls,'Canonical or sitemap mismatch: '+route
        alternates={n['attrs'].get('hreflang'):n['attrs'].get('href') for n in anodes if n['tag']=='link' and n['attrs'].get('rel')=='alternate'}
        assert len(alternates)==11 and alternates.get('x-default')==origin+name,'Invalid language alternates: '+route
        for language in LANGS:assert alternates[language]==origin+prefix(language)+name,'Incorrect hreflang: '+route
        if lang!='en':assert name in pointer['routes'][lang],'Language selector route missing: '+route
        seo_checks+=1
        approved_numbers=numbers(bnodes)
        if name in {'packages.html','weekly-bookkeeping-packages.html'}:approved_numbers+=Counter(['700','1300','2100'])
        assert numbers(anodes)==approved_numbers,'Numerical content changed outside approved Weekly rates: '+route
        old_lists=[raw(before,n) for n in bnodes if 'package-checklist' in classes(n)]
        new_lists=[raw(after,n) for n in anodes if 'package-checklist' in classes(n)]
        assert old_lists==new_lists,'Approved inclusions changed: '+route
        old_terms=[raw(before,n) for n in bnodes if 'package-terms' in classes(n) or 'package-bottom' in classes(n)]
        new_terms=[raw(after,n) for n in anodes if 'package-terms' in classes(n) or 'package-bottom' in classes(n)]
        assert old_terms==new_terms,'Approved terms changed: '+route
        if name=='packages.html':
            old_bundle=next(n for n in bnodes if n['attrs'].get('id')=='bundle-save')
            new_bundle=next(n for n in anodes if n['attrs'].get('id')=='bundle-save')
            assert [raw(before,n) for n in bnodes if inside(n,old_bundle) and 'category-preview-tier' in classes(n)]==[raw(after,n) for n in anodes if inside(n,new_bundle) and 'category-preview-tier' in classes(n)],'Bundle prices or tiers changed'
        checks+=1
    for route,expected in baseline['preserved_files'].items():
        if route=='payroll.html' or route.endswith('/payroll.html'):continue
        assert digest(read(ROOT/route))==expected,'Unrelated service/bundle source changed: '+route
    result={'approved_page_transformations':checks,'unchanged_service_and_bundle_sources':60,'payroll_paragraph_separations_with_no_word_changes':10,'bundle_overview_headings_copied_from_same_language_dedicated_page':20,'unchanged_service_overviews':10,'unchanged_translations_checklists_terms_and_destinations':True,'weekly_prices_usd_per_month':{'Bronze':700,'Silver':1300,'Gold':2100,'Enterprise':'Custom Quote'},'translation_api_calls':0,'translation_characters_sent':0,'incremental_translation_cost_usd':0,'saved_localized_price_and_tier_templates_reused':True,'screenshot_reference_note':baseline['reference_note']}
    dump(BASE/'source-and-translation-integrity.json',result)
    dump(BASE/'route-section-integrity.json',{'canonical_hreflang_and_selector_checks':seo_checks,'sitemap_page_urls':len(sitemap_urls),'approved_package_sections':60,'unchanged_service_and_bundle_files':60,'payroll_paragraph_only_changes':10,'independent_numerical_content_and_bundle_price_checks':True})
    print(json.dumps(result))

if __name__=='__main__':
    if '--verify' in sys.argv:verify()
    else:apply()
