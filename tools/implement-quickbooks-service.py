"""Scoped QuickBooks service authoring; shared Google dispatch is explicitly opt-in.

Only the approved PDF copy, new service routes, overview cards and shared service
menu are changed. Provider accounting and uncertain-request guards are unchanged.
"""
from pathlib import Path
import argparse, hashlib, html, importlib.util, json, re, subprocess, sys
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from source_section_policy import Document
ROUTE = 'quickbooks-bookkeeping-services.html'
TITLE = 'QuickBooks Bookkeeping Services'
ORIGIN = 'https://www.papertrailusa.com/'
LANGS = ['en','es','fa','hy','zh-CN','ko','tl','te','ru','ar']
PHOTO = 'assets/photos/quickbooks-bookkeeping-services-20261108.webp'
ALT = 'A Black bookkeeper and Asian business owner reviewing financial records together at a laptop in a professional office'
BASE = ROOT / 'verification/quickbooks-service-20261108'
HEADINGS = [TITLE, 'Bookkeeping in Your Existing QuickBooks Account',
 'What Our QuickBooks Bookkeeping Service Covers', 'Transaction Review and Categorization',
 'Bank and Credit Card Reconciliation', 'Income and Expense Tracking', 'Financial Reports',
 'Accounts, Invoices, and Bills', 'Tax-Ready Bookkeeping Records',
 'Weekly, Monthly, and Bookkeeping Repair Options', 'Working With Your QuickBooks Records',
 'Your QuickBooks Account and Access', 'QuickBooks Bookkeeping for Businesses at Different Stages',
 'Request QuickBooks Bookkeeping Services']
PARAGRAPH_STARTS = ['Keep your bookkeeping organized', 'Whether you need ongoing',
 'If your business uses', 'Your business retains ownership', 'We review recorded',
 'We compare the transactions', 'We organize income', 'We prepare and review',
 'Where included in your selected', 'We organize the bookkeeping', 'The frequency and scope',
 'QuickBooks Bookkeeping Services is not', 'We begin by reviewing', 'We identify the bookkeeping',
 'For QuickBooks Online,', 'You should never provide', 'A business with current records',
 'Paper Trail reviews the scope', 'Tell us what QuickBooks product']

def read(p): return p.read_text(encoding='utf-8')
def save(p, s):
 p.parent.mkdir(parents=True, exist_ok=True)
 if not p.exists() or read(p) != s: p.write_text(s, encoding='utf-8', newline='')
def dump(p, v): save(p, json.dumps(v, ensure_ascii=False, indent=2)+'\n')
def pref(l): return '' if l=='en' else l+'/'
def esc(s): return html.escape(s, quote=True)
def module():
 spec=importlib.util.spec_from_file_location('saved', ROOT/'tools/paper-trail-translations.py')
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def source(pdf):
 lines=[]
 for page in PdfReader(pdf).pages:
  for line in page.extract_text().splitlines():
   if line.startswith('Paper Trail |') or line.strip().isdigit(): continue
   lines.append(line.strip())
 lines=lines[:next(i for i,l in enumerate(lines) if l.startswith('Implementation note:'))]
 blocks=[]
 for line in lines:
  if not line: continue
  if line in HEADINGS or line in ['Request a Quote','Book a Consultation']:
   blocks.append({'tag':'h1' if line==TITLE else 'h3' if line in HEADINGS[3:9] else 'h2' if line in HEADINGS else 'cta', 'text':line})
  elif any(line.startswith(s) for s in PARAGRAPH_STARTS): blocks.append({'tag':'p','text':line})
  else: blocks[-1]['text']+=' '+line
 assert [b['text'] for b in blocks if b['tag'].startswith('h')]==HEADINGS
 assert len([b for b in blocks if b['tag']=='p'])==19
 snapshot=BASE/'approved-copy.json'
 baseline=json.loads(read(snapshot)).get('baseline_revision') if snapshot.exists() else None
 baseline=baseline or subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()
 dump(snapshot, {'baseline_revision':baseline,'pdf_sha256':hashlib.sha256(Path(pdf).read_bytes()).hexdigest(),'blocks':blocks})
 return blocks

def content(blocks):
 def elem(b, cls=''): return '<'+b['tag']+(' class="'+cls+'"' if cls else '')+'>'+esc(b['text'])+'</'+b['tag']+'>'
 s='<header class="inner-opening service-opening"><div class="wrap opening-grid"><div class="opening-copy">'+elem(blocks[0])+''.join(elem(b,'summary' if i==0 else '') for i,b in enumerate(blocks[1:3]))+'</div><div class="opening-media"><div class="photo-frame"><img src="'+PHOTO+'" alt="'+ALT+'" width="1536" height="1024" loading="eager" decoding="async" fetchpriority="high" style="width:100%;height:auto;object-fit:contain;--image-intrinsic-ratio:auto 1536 / 1024;"></div></div></div></header>'
 i=3
 while i<len(blocks)-2:
  b=blocks[i]
  if b['text']==HEADINGS[2]:
   s+='<section class="service-work"><div class="service-work-heading">'+elem(b)+'</div><div class="work-board">';i+=1
   while i<len(blocks) and blocks[i]['tag']=='h3':
    s+='<section class="work-card">'+elem(blocks[i])+'<div class="section-copy">'+elem(blocks[i+1])+'</div></section>';i+=2
   s+='</div></section>'
  else:
   assert b['tag']=='h2';s+='<section class="scope-summary">'+elem(b)+'<div>';i+=1
   while i<len(blocks) and blocks[i]['tag']=='p':s+=elem(blocks[i]);i+=1
   s+='</div></section>'
 return s

def run(args):
 m=module(); blocks=source(args.pdf) if args.pdf else json.loads(read(BASE/'approved-copy.json'))['blocks']
 body=content(blocks); excerpt=blocks[1]['text']
 template=read(ROOT/'outsourced-bookkeeping.html')
 actions=re.search(r'<div class="service-inquiry-actions.*?</details><a class="action"[^>]*>Request a Quote</a></div>',template)[0]
 body+='<section id="conversation" class="conversation-section"><div class="wrap conversation-invitation">'+actions+'</div></section>'
 inv=m.Inventory('<body>'+body+'</body>')
 sources=sorted({s['source'] for s in inv.slots}|{TITLE, TITLE+' | Paper Trail',excerpt,'View Service'})
 fields=m.load_cache();saved=ROOT/'assets/locales/quickbooks-service.json'
 if saved.exists():fields.update(json.loads(read(saved)))
 missing={l:[s for s in sources if m.key(s,l) not in fields] for l in LANGS[1:]}
 report={'scope':'QuickBooks service only','candidate_fields':sum(map(len,missing.values())), 'candidate_characters':sum(len(s) for a in missing.values() for s in a),'google_calls':0,'actual_characters_sent':0,'successful_characters':0,'failures':[]}
 report['estimated_incremental_usd']=str(report['candidate_characters']*20/1000000)
 print(json.dumps(report),flush=True)
 if report['candidate_fields'] and not args.refresh: return
 if report['candidate_fields']:
  ledger=m.private_path('DOMMYDOM_SHARED_BUDGET_DB','shared-usage.sqlite');budget=m.ExistingBudget(ledger) if ledger.exists() else m.Budget(ledger)
  m.dispatch_jobs(missing,fields,report,budget,m.preflight());m.atomic(m.CACHE,m.encoded(fields))
  dump(BASE/'translation-usage.json',report)
  if report['failures']: raise RuntimeError('Translation incomplete; inspect durable receipts before any retry')
 assert all(m.key(s,l) in fields for l in LANGS[1:] for s in sources)
 dump(saved,{m.key(s,l):fields[m.key(s,l)] for l in LANGS[1:] for s in sources})
 def tr(s,l):return s if l=='en' else fields[m.key(s,l)]['text']
 alternatives=''.join('<link rel="alternate" hreflang="'+l+'" href="'+ORIGIN+pref(l)+ROUTE+'" data-paper-trail-translation-alternate="true">' for l in LANGS+['x-default']).replace('/x-default/','/')
 for l in LANGS:
  shell=read(ROOT/pref(l)/'outsourced-bookkeeping.html');translated=body
  if l!='en':
   edits=[]
   for slot in inv.slots:
    value=esc(tr(slot['source'],l));raw=inv.markup[slot['start']:slot['end']]
    if slot['kind']=='text':value=re.sub(r'\S[\s\S]*\S|\S',lambda _:value,raw,count=1)
    edits.append((slot['start'],slot['end'],value))
   translated=m.apply_edits(inv.markup,edits)[len('<body>'):-len('</body>')]
   translated=re.sub(r'href="request-a-custom-quote.html"', 'href="'+l+'/request-a-custom-quote.html"',translated)
  start=shell.index('<main id="main">')+len('<main id="main">');end=shell.index('<dialog id="conversation-dialog"',start)
  shell=shell[:start]+translated+shell[end:]
  shell=re.sub(r'<title>.*?</title>','<title>'+esc(tr(TITLE+' | Paper Trail',l))+'</title>',shell)
  shell=re.sub(r'<script type="application/ld\+json">.*?</script>','',shell,flags=re.S)
  shell=re.sub(r'<link\b[^>]*rel="alternate"[^>]*>','',shell)
  shell=re.sub(r'(<link rel="canonical" href=")[^"]+',lambda x:x[1]+ORIGIN+pref(l)+ROUTE,shell)
  shell=re.sub(r'(<meta\b[^>]*(?:name="description"|property="og:description"|name="twitter:description")[^>]*content=")[^"]*',lambda x:x[1]+esc(tr(excerpt,l)),shell)
  shell=re.sub(r'(<meta\b[^>]*(?:property="og:title"|name="twitter:title")[^>]*content=")[^"]*',lambda x:x[1]+esc(tr(TITLE,l)),shell)
  shell=re.sub(r'(<meta\b[^>]*property="og:url"[^>]*content=")[^"]*',lambda x:x[1]+ORIGIN+pref(l)+ROUTE,shell)
  shell=shell.replace('assets/photos/outsourced-bookkeeping-20261027.webp',PHOTO)
  # Keep existing chat behavior and saved localized answers; correct page context.
  shell=shell.replace('"page": "outsourced-bookkeeping.html"','"page": "'+ROUTE+'"')
  shell=re.sub(r'("topic":\s*")[^"]*',lambda x:x[1]+tr(TITLE,l),shell)
  schema={'@context':'https://schema.org','@type':'Service','name':tr(TITLE,l),'description':tr(excerpt,l),'url':ORIGIN+pref(l)+ROUTE,'provider':{'@type':'Organization','name':'Paper Trail','url':ORIGIN}}
  shell=shell.replace('</head>',alternatives+'<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=True)+'</script></head>')
  save(ROOT/pref(l)/ROUTE,shell)
  path=ROOT/pref(l)/'all-services.html';overview=read(path)
  overview=re.sub(r'<h2><a href="'+re.escape(pref(l)+ROUTE)+r'">(.*?)</a></h2>',r'<h2>\1</h2>',overview)
  save(path,overview)
  if ROUTE not in overview:
   card='<article class="service-overview-card"><h2>'+esc(tr(TITLE,l))+'</h2><p class="summary">'+esc(tr(excerpt,l))+'</p><a class="action" href="'+pref(l)+ROUTE+'">'+esc(tr('View Service',l))+'</a></article>'
   overview=overview.replace('</article></div><div class="page-conversation">','</article>'+card+'</div><div class="page-conversation">',1)
   assert ROUTE in overview;save(path,overview)
 for name in ['assets/service-package-navigation.js','assets/navigation-ready.js']:
  path=ROOT/name;s=read(path)
  s=s.replace("'Financial Analysis', 'Payroll'];","'Financial Analysis', 'Payroll', '"+TITLE+"'];")
  s=s.replace("'financial-analysis.html', 'payroll.html'];","'financial-analysis.html', 'payroll.html', '"+ROUTE+"'];")
  if name.endswith('navigation-ready.js'):
   match=re.search(r'window.PAPER_TRAIL_SERVICE_MENU=(.*?);\n',s);labels=json.loads(match[1])
   for l in LANGS:labels[l][TITLE]=tr(TITLE,l)
   s=s[:match.start()]+'window.PAPER_TRAIL_SERVICE_MENU='+json.dumps(labels,ensure_ascii=False)+';\n'+s[match.end():]
  save(path,s)
 pointerpath=ROOT/'assets/translation-workflow/current.json';pointer=json.loads(read(pointerpath))
 for l in LANGS[1:]:pointer['routes'][l]=sorted(set(pointer['routes'][l])|{ROUTE})
 pointer['source_fingerprints'][ROUTE]=m.digest(json.dumps([s['source'] for s in m.Inventory(read(ROOT/ROUTE)).slots]))
 pointer['source_pages']=len(pointer['source_fingerprints'])
 dump(pointerpath,pointer)
 save(ROOT/'assets/translation-workflow/routes.js','window.paperTrailTranslationRoutes='+json.dumps(pointer['routes'])+';\n')
 inventorypath=ROOT/'tools/production-pages.json';inventory=json.loads(read(inventorypath))
 inventory['english']=sorted(set(inventory['english'])|{ROUTE})
 for l in LANGS[1:]:inventory['locales'][l]=sorted(set(inventory['locales'][l])|{ROUTE})
 dump(inventorypath,inventory)
 for name,languages in [('sitemap.xml',['en']),('sitemap-translations.xml',LANGS[1:])]:
  path=ROOT/name;s=read(path)
  map_alternates=''.join('<xhtml:link rel="alternate" hreflang="'+lang+'" href="'+ORIGIN+pref(lang)+ROUTE+'"/>' for lang in LANGS+['x-default']).replace('/x-default/','/')
  for l in languages:
   url=ORIGIN+pref(l)+ROUTE
   entry='<url><loc>'+url+'</loc>'+map_alternates+'</url>'
   if '<loc>'+url+'</loc>' not in s:s=s.replace('</urlset>',entry+'\n</urlset>')
   else:s=re.sub(r'<url><loc>'+re.escape(url)+r'</loc>.*?</url>',lambda _:entry,s)
  save(path,s)
 print('Built ten service routes; only scoped overview, menu, route and sitemap integrations changed.')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--pdf');p.add_argument('--refresh',action='store_true');run(p.parse_args())
