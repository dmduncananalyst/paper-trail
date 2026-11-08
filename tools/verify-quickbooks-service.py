"""Verify approved copy, scoped changes, saved translations, SEO and browser behavior.
Disposable browser profiles and screenshots stay in system TEMP. No form submits.
"""
from pathlib import Path
import argparse, hashlib, html, json, re, subprocess, sys, tempfile
import xml.etree.ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parent))
from source_section_policy import Document, inappropriate_spans
import importlib.util
spec=importlib.util.spec_from_file_location('qb',Path(__file__).with_name('implement-quickbooks-service.py'))
q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)

def check():
 fields=json.loads(q.read(q.ROOT/'assets/locales/quickbooks-service.json'));m=q.module()
 snapshot=json.loads(q.read(q.BASE/'approved-copy.json'));blocks=snapshot['blocks'];baseline=snapshot['baseline_revision']
 def tr(s,l):return s if l=='en' else fields[m.key(s,l)]['text']
 urls={n.text for f in ['sitemap.xml','sitemap-translations.xml'] for n in ET.parse(q.ROOT/f).iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
 for l in q.LANGS:
  print('Checking saved copy and SEO: '+l,flush=True)
  route=q.pref(l)+q.ROUTE;s=q.read(q.ROOT/route);ns=Document(s).nodes
  main=s[s.index('<main id="main">'):s.index('<dialog id="conversation-dialog"')]
  actual=[' '.join(''.join(n['text']).split()) for n in Document(main).nodes if n['tag'] in {'h1','h2','h3','p'}]
  assert actual==[tr(b['text'],l) for b in blocks if b['tag']!='cta'], 'Approved copy mismatch: '+l
  assert 'Implementation note:' not in s and 'Source check:' not in s
  assert not inappropriate_spans(s,route)
  assert 'rel="canonical" href="'+q.ORIGIN+route+'"' in s and q.ORIGIN+route in urls
  mapfile='sitemap.xml' if l=='en' else 'sitemap-translations.xml'
  entry=next(n for n in ET.parse(q.ROOT/mapfile).getroot() if n.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text==q.ORIGIN+route)
  assert len(entry.findall('{http://www.w3.org/1999/xhtml}link'))==11
  alternates={n['attrs'].get('hreflang'):n['attrs'].get('href') for n in ns if n['tag']=='link' and n['attrs'].get('rel')=='alternate'}
  assert len(alternates)==11 and alternates['x-default']==q.ORIGIN+q.ROUTE
  for language in q.LANGS:assert alternates[language]==q.ORIGIN+q.pref(language)+q.ROUTE
  assert q.PHOTO in main and main.count('<img ')==1
  assert 'request-a-custom-quote.html' in main
  for url in ['https://calendar.app.google/CFU1yh6iQrCjEUZ2A','https://calendar.app.google/RuynVGfwUfYNiDnp9']:assert url in main
  overview=q.read(q.ROOT/q.pref(l)/'all-services.html')
  # Strip the one approved new card and prove every prior overview byte remains.
  stripped=re.sub(r'<article class="service-overview-card"><h2>'+re.escape(html.escape(tr(q.TITLE,l),quote=True))+r'</h2>.*?<a class="action" href="'+re.escape(q.pref(l)+q.ROUTE)+r'">.*?</article>','',overview,flags=re.S)
  old=subprocess.check_output(['git','show',baseline+':'+q.pref(l)+'all-services.html'],cwd=q.ROOT).decode()
  assert stripped.replace('\r\n','\n')==old.replace('\r\n','\n'),'Existing cards changed: '+l
  if l!='en':
   for b in blocks:
    if b['tag']=='p':assert tr(b['text'],l)!=b['text'],'English paragraph: '+l
 # All existing service, package and bundle sources remain byte-identical to HEAD.
 protected=['weekly-bookkeeping.html','paper-trail-monthly-bookkeeping.html','paper-trail-services.html','accounts-billing.html','financial-analysis.html','payroll.html','packages.html','all-bundles.html']+[k+'-packages.html' for k in ['weekly-bookkeeping','monthly-bookkeeping','bookkeeping-repair','accounts-billing','financial-analysis','payroll']]
 for l in q.LANGS:
  print('Checking protected service/package sources: '+l,flush=True)
  for name in protected:
   route=q.pref(l)+name;old=subprocess.check_output(['git','show',baseline+':'+route],cwd=q.ROOT)
   assert (q.ROOT/route).read_bytes().replace(b'\r\n',b'\n')==old.replace(b'\r\n',b'\n'),'Unrelated source changed: '+route
 print(json.dumps({'approved_copy_and_heading_order':True,'full_language_versions':10,'existing_overviews_preserved':10,'protected_service_package_bundle_files':len(protected)*10,'canonical_hreflang_sitemap_checks':True,'english_paragraph_fallbacks':0}))

def browser(origin):
 from playwright.sync_api import sync_playwright
 out=Path(tempfile.mkdtemp(prefix='paper-trail-quickbooks-browser-'));results=[]
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
  context=b.new_context();page=context.new_page();errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  def route(request):
   if not request.request.url.startswith(origin):route_action='abort'
   else:route_action='continue_'
   getattr(request,route_action)()
  context.route('**/*',route)
  for width in [1440,768,390]:
   page.set_viewport_size({'width':width,'height':1000})
   for l in q.LANGS:
    print('Browser: '+l+' '+str(width)+'px',flush=True)
    context.clear_cookies();page.goto(origin+'/'+q.pref(l)+q.ROUTE);page.wait_for_function('document.readyState==="complete"&&document.querySelector(".pt-nav").dataset.organizedNavigation')
    page.evaluate('async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>{i.loading="eager";return i.decode().catch(()=>{})}))}')
    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+2'),f'Overflow {l} {width}'
    page.wait_for_function('[...document.images].every(i=>i.complete&&i.naturalWidth>0)',timeout=15000)
    broken=page.evaluate('[...document.images].filter(i=>!i.naturalWidth).map(i=>i.src)')
    assert not broken,f'Broken image {l} {width}: {broken}'
    nav=page.locator('#navigation-services a[href$="/'+q.ROUTE+'"]');assert nav.count()==1
    assert page.locator('#navigation-packages a[href$="/'+q.ROUTE+'"]').count()==0
    page.locator('.pt-nav > .nav-family > a').first.focus();page.keyboard.press('ArrowDown');assert nav.is_visible()
    page.keyboard.press('Escape')
    details=page.locator('main details.package-consultation');details.locator('summary').click();assert details.get_attribute('open') is not None
    assert details.locator('a').count()==2;details.locator('summary').click()
    assert page.locator('main a[href$="request-a-custom-quote.html"]').count()==1
    if l in ['en','ar']:page.screenshot(path=str(out/f'{l}-{width}.png'),full_page=True)
    # Exercise actual language switching and preserve the dedicated route.
    nextlang='es' if l=='en' else 'en';page.select_option('#language',nextlang)
    page.wait_for_url(origin+'/'+q.pref(nextlang)+q.ROUTE)
    page.evaluate('localStorage.setItem("paper-trail-language","'+l+'")')
    page.goto(origin+'/'+q.pref(l)+'all-services.html');page.wait_for_load_state('networkidle')
    card=page.locator('.service-overview-card').filter(has=page.locator('a[href$="'+q.ROUTE+'"]'))
    assert card.count()==1
    for selector in ['h2','a.action']:
     if selector=='h2':card.click(position={'x':20,'y':20})
     else:card.locator(selector).click()
     page.wait_for_url(origin+'/'+q.pref(l)+q.ROUTE)
     page.go_back();page.wait_for_load_state('networkidle')
    results.append({'width':width,'locale':l,'overflow':False,'images':True,'services_menu':True,'card_and_button':True,'language_switch':True,'consultation':True})
  assert not errors,errors
  b.close()
 (out/'results.json').write_text(json.dumps(results,indent=2))
 print(json.dumps({'browser_cases':len(results),'javascript_errors':errors,'screenshots_and_report':str(out),'customer_forms_submitted':0}))

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--browser',action='store_true');parser.add_argument('--origin',default='http://127.0.0.1:8798');args=parser.parse_args()
 check()
 if args.browser:browser(args.origin)
