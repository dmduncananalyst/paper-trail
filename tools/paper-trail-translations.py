"""Saved Google translations, explicit initial run and offline blog preparation.
Reuses DommyDom's provider and shared ledger. No Git or publishing operations.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlsplit,urlunsplit
from decimal import Decimal
import argparse,html,json,os,re,sys,time,uuid,tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'sun-and-sage/scripts'))
from translation_pipeline.pipeline import atomic as durable_atomic,encoded,digest,normal,google_translate,LOCALES
from translation_pipeline.workflow import Inventory as OriginalInventory,apply_edits,valid_value
from translation_pipeline.budget import Budget,ExistingBudget
from translation_pipeline.connection import private_path,access_token
PROJECT='project-2e0d7d9d-d482-4fcf-b6d'
BASE=Path('assets/translation-workflow');OUT=Path(tempfile.gettempdir())/'paper-trail-translation-restoration-20261026'
CACHE=ROOT/'.translation-cache/google-site-fields.json';RECEIPTS=ROOT/'.translation-cache/provider-responses'
ALLOCATION='paper-trail-initial-2026-10-16'
NOTICE=['Translation information','This page uses automatic translations from Google Translate. The original English text is authoritative.','This service may contain translations powered by Google. Google disclaims all warranties related to the translations, express or implied, including any warranties of accuracy, reliability, and any implied warranties of merchantability, fitness for a particular purpose and noninfringement.']
PROTECTED={'Paper Trail','PaperTrail','StartWeb7','Google','Google Translate','QuickBooks','Xero','Gmail','Microsoft 365 / Outlook'}
def atomic(path,data):
 path=Path(path)
 if path.suffix!='.html':return durable_atomic(path,data)
 # Derived HTML can be recreated from the durable provider receipts at no cost.
 # Keep atomic replacement, but avoid synchronous disk flushes for every copy.
 if path.exists() and path.read_bytes()==data:return
 path.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(prefix='.'+path.name,dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as stream:stream.write(data)
  for attempt in range(6):
   try:os.replace(tmp,path);break
   except PermissionError:
    if attempt==5:raise
    time.sleep(.1*(2**attempt))
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
def eligible(s):return bool(re.search('[A-Za-z]',s)) and s not in PROTECTED and not re.match(r'^(https?:|mailto:|tel:|[^\s]+@)',s)
def key(s,l):return digest(s)+'|'+l
class Inventory(OriginalInventory):
 def handle_starttag(self,t,a):
  if t=='select' and dict(a).get('id')=='language':a=list(a)+[('translate','no')]
  before=len(self.slots);super().handle_starttag(t,a);self.slots[before:]=[s for s in self.slots[before:] if eligible(s['source'])]
 def handle_data(self,s):
  before=len(self.slots);super().handle_data(s);self.slots[before:]=[x for x in self.slots[before:] if eligible(x['source'])]
def load_cache():
 fields=json.loads(CACHE.read_text(encoding='utf-8')) if CACHE.exists() else {}
 checkpoint=ROOT/BASE/'current.json'
 if checkpoint.exists():
  revision=json.loads(checkpoint.read_text(encoding='utf-8')).get('revision','')
  if re.fullmatch('[0-9a-f]{64}',revision):
   release=ROOT/BASE/'releases'/revision/'fields.json'
   if release.exists():
    saved=json.loads(release.read_text(encoding='utf-8'))
    if saved.get('provider')=='google':
     for k,v in saved.get('fields',{}).items():fields[k]=v
 for p in RECEIPTS.glob('*.json'):
  r=json.loads(p.read_text(encoding='utf-8'))
  for s,v in zip(r['sources'],r['values']):
   if valid_value(s,v):fields.setdefault(key(s,r['locale']),{'source':s,'locale':r['locale'],'text':v,'provider':'google','receipt':p.name})
 dom=ROOT.parent/'sun-and-sage/.translation-build-cache/dommydom-workflow-fields.json'
 if dom.exists():
  for k,v in json.loads(dom.read_text(encoding='utf-8')).items():
   if v.get('provenance')=='google' and valid_value(v['source'],v.get('text')):fields.setdefault(k,{**v,'provider':'google','reused_from':'dommydom'})
 for k,v in fields.items():
  if k!=key(v['source'],v['locale']) or v.get('provider') not in {'google','authored'} or not (valid_value(v['source'],v['text']) or (v['source']=='The' and v['locale']=='fa' and v['text']=='')):raise ValueError('Invalid saved translation result')
 return fields
def inventory():
 pages={p.relative_to(ROOT).as_posix():Inventory(p.read_text(encoding='utf-8')) for p in [*sorted(ROOT.glob('*.html')),*sorted((ROOT/'state-records').glob('*.html'))]}
 static_refs={s['source'] for inv in pages.values() for s in inv.slots};refs=set()
 def walk(v,k=''):
  if isinstance(v,dict):
   for k,x in v.items():walk(x,k)
  elif isinstance(v,list):
   for x in v:walk(x,k)
  elif isinstance(v,str) and k not in {'page','url','href','id','type'} and eligible(normal(v)):refs.add(normal(v))
 for inv in pages.values():
  for m in re.finditer(r'<script[^>]*id="conversation-data"[^>]*>(.*?)</script>',inv.markup,re.S):walk(json.loads(m[1]))
  def schema_refs(v):
   if isinstance(v,list):
    for x in v:schema_refs(x)
   elif isinstance(v,dict):
    for k,x in v.items():
     if k in {'name','description','headline','text','caption','alternativeHeadline'} and isinstance(x,str) and eligible(normal(x)):refs.add(normal(x))
     elif isinstance(x,(dict,list)):schema_refs(x)
  for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>',inv.markup,re.S):schema_refs(json.loads(m[1]))
 en=json.loads((ROOT/'assets/locales/home-blog/en.json').read_text(encoding='utf-8'))
 chat=json.loads((ROOT/'assets/locales/home-blog/chat.json').read_text(encoding='utf-8'))['en']
 refs.update(normal(s) for s in [*en.values(),*chat.values(),*NOTICE] if eligible(normal(s)))
 for name in ['site.js','design.js','hubspot.js','custom-quote.js']:
  if not (ROOT/'assets'/name).exists():continue
  text=(ROOT/'assets'/name).read_text(encoding='utf-8')
  quote_feedback=set(re.findall(r"(?:help\.textContent=(?:localized\()?|showProblem\()'((?:\\.|[^'\\\n])*)'",text)) if name=='custom-quote.js' else set()
  for v in re.findall(r"'((?:\\.|[^'\\\n])*)'",text):
   if not re.search(r'[A-Za-z]{2} [A-Za-z]{2}',v) or len(v)>650 or re.search(r'[{};=<>]|document\.|querySelector|\[|\]|var\(|rgb\(',v):continue
   if v.startswith(('what how can does',' | Paper Trail','Paper Trail inquiry')):continue
   if name=='hubspot.js' and not v.startswith(('Please ','Your note ','We could not ')):continue
   if name=='custom-quote.js' and v not in quote_feedback:continue
   v=re.sub(r'\\u([a-fA-F0-9]{4})',lambda m:chr(int(m[1],16)),v).replace("\\'","'").replace('\\n','\n')
   if eligible(normal(v)):refs.add(normal(v))
  if name=='design.js':
   for fragment in re.findall(r"\.innerHTML='([^']*)'",text):refs.update(s['source'] for s in Inventory('<body>'+fragment+'</body>').slots)
 runtime_refs=sorted(refs);refs.update(static_refs)
 fields=load_cache();missing={l:sorted(s for s in refs if key(s,l) not in fields) for l in LOCALES}
 report={'pages':len(pages),'locales':LOCALES,'source_strings':len(refs),'english_characters':sum(map(len,refs)),'candidate_fields':sum(map(len,missing.values())),'candidate_characters':sum(len(s) for a in missing.values() for s in a),'google_calls':0,'actual_characters_sent':0,'source_fingerprints':{n:digest(json.dumps([s['source'] for s in i.slots])) for n,i in pages.items()}}
 report['candidate_cost_usd']=str(Decimal(report['candidate_characters'])*20/1000000);report['_runtime_sources']=runtime_refs
 return pages,refs,fields,missing,report
class InitialBudget(ExistingBudget):
 def _quote(self,c,chars):
  s=json.loads(c.execute('SELECT data FROM snapshot WHERE id=1').fetchone()[0]);self.validate(s)
  row=c.execute('SELECT data FROM translation_funding WHERE id=?',(ALLOCATION,)).fetchone()
  if not row:return {'allowed':False,'reason':'Initial Paper Trail allocation missing','project':PROJECT}
  a=json.loads(row[0]);now=time.time();used=c.execute('SELECT coalesce(sum(r.chars),0) FROM reservations r JOIN translation_reservation_funding t ON t.reservation=r.id WHERE t.funding_id=?',(ALLOCATION,)).fetchone()[0]
  reserved=sum(r['chars'] for r in c.execute('SELECT * FROM reservations') if r['id'] not in s['included_reservations']);exposure=Decimal(s['opening_characters']+reserved+chars)*20/1000000
  protected=0
  for r in c.execute("SELECT id,data FROM translation_funding WHERE id!=? AND id!='ongoing'",(ALLOCATION,)).fetchall():
   f=json.loads(r['data'])
   if f.get('purpose')=='initial-dommydom':
    spent=c.execute('SELECT coalesce(sum(r.chars),0) FROM reservations r JOIN translation_reservation_funding t ON t.reservation=r.id WHERE t.funding_id=?',(r['id'],)).fetchone()[0];protected+=max(0,f['maximum_characters']-spent)
  protected=Decimal(protected)*20/1000000
  allowed=(a['purpose']=='initial-paper-trail' and a['project']==s['project']==PROJECT and now<a['dispatch_deadline'] and now<a['credit_evidence']['expires_at'] and used+chars<=a['maximum_characters'] and exposure+protected<=Decimal(a['credit_evidence']['reported_available_usd']))
  return {'allowed':allowed,'reason':'Within approved initial allocation' if allowed else 'Initial allocation or trial headroom exceeded','project':PROJECT,'characters':chars,'initial_reserved':used,'maximum_characters':a['maximum_characters'],'estimated_incremental_usd':str(Decimal(chars)*20/1000000),'conservative_total_exposure_usd':str(exposure),'protected_dommydom_usd':str(protected),'conservative_trial_headroom_usd':str(Decimal(a['credit_evidence']['reported_available_usd'])-exposure-protected)}
 def reserve(self,site,chars,request_id=None):
  if site!='paper-trail' or type(chars) is not int or chars<=0:raise ValueError('Paper Trail initial scope only')
  rid=request_id or uuid.uuid4().hex
  with self.db() as c:
   c.execute('BEGIN IMMEDIATE');q=self._quote(c,chars)
   if q['allowed']:c.execute('INSERT INTO reservations VALUES(?,?,?,?,?)',(rid,site,chars,time.time(),'reserved'));c.execute('INSERT INTO translation_reservation_funding VALUES(?,?)',(rid,ALLOCATION))
   c.commit();return {**q,'reservation':rid if q['allowed'] else None}
def preflight():
 token=access_token();headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'}
 def request(url,data=None):
  with urlopen(Request(url,headers=headers,data=None if data is None else json.dumps(data).encode()),timeout=30) as r:return json.load(r)
 service=request('https://serviceusage.googleapis.com/v1/projects/'+PROJECT+'/services/translate.googleapis.com');perms=request('https://cloudresourcemanager.googleapis.com/v1/projects/'+PROJECT+':testIamPermissions',{'permissions':['serviceusage.services.use']});billing=request('https://cloudbilling.googleapis.com/v1/projects/'+PROJECT+'/billingInfo')
 proof={'checked_at':time.time(),'translation_api_enabled':service.get('state')=='ENABLED','consumer_permission':'serviceusage.services.use' in perms.get('permissions',[]),'billing_enabled':billing.get('billingEnabled') is True,'translation_calls':0};proof['passed']=all(proof[k] for k in ['translation_api_enabled','consumer_permission','billing_enabled']);atomic(OUT/'preflight.json',encoded(proof))
 if not proof['passed']:raise ValueError('Existing Google prerequisites failed')
 return token
def install_initial(report,budget):
 if Decimal(report['candidate_cost_usd'])>Decimal('105.79'):raise ValueError('Exact dispatch exceeds quoted scope')
 with budget.db() as c:
  c.execute('BEGIN IMMEDIATE')
  if c.execute("SELECT count(*) FROM reservations WHERE result='reserved'").fetchone()[0]:raise ValueError('Another shared translation job is active')
  evidence=json.loads(c.execute("SELECT data FROM translation_funding WHERE id='dommydom-initial-2026-10-16'").fetchone()[0])['credit_evidence']
  a={'purpose':'initial-paper-trail','project':PROJECT,'maximum_characters':report['candidate_characters'],'source_fingerprints':report['source_fingerprints'],'approved_at':time.time(),'dispatch_deadline':min(time.time()+86400,evidence['expires_at']),'credit_evidence':evidence,'cash_overage_approved':False,'approval_basis':'Owner approved full Paper Trail translation after $105.78 estimate, saved results and Blog workflow; DommyDom retains priority.'}
  old=c.execute('SELECT data FROM translation_funding WHERE id=?',(ALLOCATION,)).fetchone()
  if old:
   if json.loads(old[0])['source_fingerprints']!=a['source_fingerprints']:raise ValueError('Initial approved content changed')
  else:c.execute('INSERT INTO translation_funding VALUES(?,?)',(ALLOCATION,json.dumps(a)))
  c.commit()
def dispatch_jobs(missing,fields,report,budget,token):
 from concurrent.futures import ThreadPoolExecutor,as_completed
 from threading import Event
 stopped=Event();jobs=[]
 for locale,values in missing.items():
  remaining=list(values)
  while remaining:
   chunk=[];count=0
   while remaining and len(chunk)<50 and count+len(remaining[0])<=4500:
    source=remaining.pop(0);chunk.append(source);count+=len(source)
   if not chunk:raise ValueError('Source exceeds existing request guard')
   jobs.append((locale,chunk,count))
 def worker(job):
  if stopped.is_set():return None
  locale,chunk,count=job;reservation=budget.reserve('paper-trail',count)
  if not reservation['allowed']:
   stopped.set();return {'called':False,'locale':locale,'sources':chunk,'error':reservation['reason']}
  outcome='uncertain';values=None;error=None
  try:
   values=google_translate(locale,chunk,PROJECT,token)
   receipt=reservation['reservation']+'.json'
   atomic(RECEIPTS/receipt,encoded({'locale':locale,'sources':chunk,'values':values,'characters':count,'received_at':time.time()}))
   outcome='complete' if all(valid_value(s,v) for s,v in zip(chunk,values)) else 'partial'
   if outcome=='partial':error='Empty nonarticle result; accepted siblings saved';stopped.set()
  except Exception as e:
   error=type(e).__name__+(' HTTP '+str(e.code) if hasattr(e,'code') else '');stopped.set()
  finally:budget.finish(reservation['reservation'],outcome)
  return {'called':True,'locale':locale,'sources':chunk,'values':values,'characters':count,'receipt':reservation['reservation']+'.json','error':error}
 with ThreadPoolExecutor(max_workers=1) as pool:
  for future in as_completed([pool.submit(worker,job) for job in jobs]):
   row=future.result()
   if row is None:continue
   locale=row['locale']
   if row['called']:
    report['google_calls']+=1;report['actual_characters_sent']+=row['characters']
    for source,value in zip(row['sources'],row.get('values') or []):
     if valid_value(source,value):
      fields[key(source,locale)]={'source':source,'locale':locale,'text':value,'provider':'google','receipt':row['receipt']};report['successful_characters']+=len(source)
   if row['error']:report['failures'].append({'locale':locale,'reason':row['error'],'source_hashes':[digest(x) for x in row['sources']]})
   if report['google_calls']%20==0:
    atomic(CACHE,encoded(fields));print(json.dumps({'calls':report['google_calls'],'sent':report['actual_characters_sent'],'locale':locale}),flush=True)
   atomic(OUT/'live-progress.json',encoded(report))

def run(mode,approve=False):
 pages,refs,fields,missing,report=inventory()
 if mode=='inventory':return report
 OUT.mkdir(parents=True,exist_ok=True);atomic(OUT/'inventory.json',encoded(report))
 if mode in ('live','refresh') and report['candidate_characters']:
  if not approve:raise ValueError('Explicit live approval required')
  ledger=private_path('DOMMYDOM_SHARED_BUDGET_DB','shared-usage.sqlite')
  # Current owner approval supersedes historical initial funding and custom caps.
  # New accounting records incremental usage, never an invented historical zero.
  budget=ExistingBudget(ledger) if ledger.exists() else Budget(ledger)
  quote=budget.quote(report['candidate_characters'])
  if not quote['allowed']:
   report.update(budget=quote,rendered=False,pending_fields=report['candidate_fields'],pending_characters=report['candidate_characters']);atomic(OUT/'latest.json',encoded(report));return report
  token=preflight()
  report.update(successful_characters=0,failures=[])
  dispatch_jobs(missing,fields,report,budget,token)
  atomic(CACHE,encoded(fields));report['budget']=budget.quote(0);atomic(OUT/('attempt-'+str(int(time.time()))+'.json'),encoded(report))
 fields=load_cache();pending=[{'locale':l,'source_sha256':digest(s),'characters':len(s)} for l in LOCALES for s in refs if key(s,l) not in fields];report['pending_fields']=len(pending);report['pending_characters']=sum(x['characters'] for x in pending);atomic(OUT/'pending.json',encoded(pending))
 if not pending:build_saved(pages,refs,fields,report)
 else:report['rendered']=False
 atomic(OUT/'latest.json',encoded(report));return report
def install_runtime(markup,revision):
 # Reuse the established ten-language selector on new approved English pages.
 original=(ROOT/'index.html').read_text(encoding='utf-8') if (ROOT/'index.html').exists() else ''
 choices=re.search(r'<select\b[^>]*id="language"[^>]*>(.*?)</select>',original,re.S)
 if choices:markup=re.sub(r'(<select\b[^>]*id="language"[^>]*>).*?(</select>)',lambda m:m[1]+choices[1]+m[2],markup,flags=re.S)
 markup=re.sub(r'<script[^>]*data-paper-trail-translation-routing="true"[^>]*></script>','',markup);markup=re.sub(r'<link[^>]*data-paper-trail-translation-style="true"[^>]*>','',markup)
 markup=re.sub(r'(assets/locales/home-blog/current\.js)(?:\?[^"\s>]*)?',r'\1?v='+revision,markup)
 if 'assets/locales/home-blog/current.js' not in markup:markup=markup.replace('</head>','<script src="assets/locales/home-blog/current.js?v='+revision+'"></script></head>',1)
 tags='<script src="assets/translation-workflow/routes.js?v='+revision+'" data-paper-trail-translation-routing="true"></script><script src="assets/translation-workflow/navigation.js?v='+revision+'" data-paper-trail-translation-routing="true"></script><link rel="stylesheet" href="assets/translation-workflow/display.css?v='+revision+'" data-paper-trail-translation-style="true">';markup=markup.replace('</head>',tags+'</head>',1)
 for asset in ['site.js','design.js']:markup=re.sub(r'(assets/'+re.escape(asset)+r')(?:\?[^"\s>]*)?',r'\1?v='+revision,markup)
 return markup
def alternates(markup,name,english_url):
 markup=re.sub(r'<link[^>]*data-paper-trail-translation-alternate="true"[^>]*>','',markup)
 urls={'en':english_url,**{l:'https://www.papertrailusa.com/'+l+'/'+name for l in LOCALES},'x-default':english_url}
 links=''.join('<link rel="alternate" hreflang="'+l+'" href="'+html.escape(url,quote=True)+'" data-paper-trail-translation-alternate="true">' for l,url in urls.items())
 return markup.replace('</head>',links+'</head>',1)
def build_saved(pages,refs,fields,report):
 from source_section_policy import clean as clean_citation_sections
 checkpoint=ROOT/BASE/'current.json'
 previous=json.loads(checkpoint.read_text(encoding='utf-8')) if checkpoint.exists() else {}
 previous_fingerprints=previous.get('source_fingerprints',{})
 def complete_selector(markup):
  selector=re.search(r'<select\b[^>]*id="language"[^>]*>(.*?)</select>',markup,re.S)
  return not selector or len(re.findall(r'<option\b',selector[1]))==10
 origin='https://www.papertrailusa.com';revision=digest(json.dumps({k:v['text'] for k,v in fields.items()},sort_keys=True));routes={l:list(pages) for l in LOCALES};atomic(ROOT/BASE/'releases'/revision/'fields.json',encoded({'provider':'google','fields':fields}))
 en=json.loads((ROOT/'assets/locales/home-blog/en.json').read_text(encoding='utf-8'));ui={'en':en};chat=json.loads((ROOT/'assets/locales/home-blog/chat.json').read_text(encoding='utf-8'))
 chat.setdefault('en',{}).update({s:s for s in report['_runtime_sources']})
 for l in LOCALES:
  ui[l]={k:fields[key(normal(s),l)]['text'] for k,s in en.items()}
  chat.setdefault(l,{}).update({s:fields[key(s,l)]['text'] for s in report['_runtime_sources'] if s not in chat.get(l,{})})
 bundle='/* Permanently saved Google results. No visitor provider calls. */\nwindow.PAPER_TRAIL_LOCALES='+json.dumps(ui,ensure_ascii=True)+';\nwindow.PAPER_TRAIL_CHAT_LOCALES='+json.dumps(chat,ensure_ascii=True)+';\n';atomic(ROOT/'assets/locales/home-blog/current.js',bundle.encode())
 for l in LOCALES:atomic(ROOT/'assets/locales/home-blog'/(l+'.json'),encoded(ui[l]))
 atomic(ROOT/'assets/locales/home-blog/chat.json',encoded(chat));atomic(ROOT/'assets/locales/home-blog/provider-current.json',encoded({'revision':revision,'provider':'google','workflow':'whole-site'}))
 generated=[]
 for name,inv in pages.items():
  english_url=re.search(r'<link rel="canonical" href="([^"]+)"',inv.markup)[1]
  for l in LOCALES:
   target=ROOT/l/name
   if previous_fingerprints.get(name)==report['source_fingerprints'].get(name) and target.exists() and complete_selector(target.read_text(encoding='utf-8')):continue
   edits=[]
   for slot in inv.slots:
    raw=inv.markup[slot['start']:slot['end']];value=html.escape(fields[key(slot['source'],l)]['text'],quote=slot['kind']!='text')
    if slot['kind']=='text':value=re.sub(r'\S[\s\S]*\S|\S',lambda _:value,raw,count=1)
    edits.append((slot['start'],slot['end'],value))
   markup=apply_edits(inv.markup,edits);markup=re.sub(r'<base\b[^>]*>','',markup);markup=markup.replace('<head>','<head><base href="'+('../'*len(Path(name).parts))+'">',1);markup=re.sub(r'<html\b[^>]*>','<html lang="'+l+'-x-mtfrom-en" dir="ltr" data-static-locale="'+l+'">',markup,count=1)
   markup=re.sub(r'<p\b[^>]*class="translation-notice"[^>]*>.*?</p>','',markup,flags=re.S)
   markup=re.sub(r'<(?:p|small)\b[^>]*class="article-language"[^>]*>.*?</(?:p|small)>','',markup,flags=re.S)
   def link(m):
    u=urlsplit(html.unescape(m[2]));target=u.path.lstrip('/') or name
    if not u.scheme and not u.netloc and target in pages:return m[1]+html.escape(urlunsplit(('', '',l+'/'+target,u.query,u.fragment)),quote=True)+m[3]
    return m[0]
   markup=re.sub(r'(<a\b[^>]*\bhref=")([^"]*)(")',link,markup);canonical=origin+'/'+l+'/'+name;markup=re.sub(r'<link rel="canonical" href="[^"]+"\s*/?>','<link rel="canonical" href="'+canonical+'">',markup);markup=re.sub(r'(<meta property="og:url" content=")[^"]+(")',lambda m:m[1]+canonical+m[2],markup)
   og={'es':'es_US','fa':'fa_IR','hy':'hy_AM','zh-CN':'zh_CN','ko':'ko_KR','tl':'tl_PH','te':'te_IN','ru':'ru_RU','ar':'ar_SA'}[l]
   markup=re.sub(r'(<meta property="og:locale" content=")[^"]+(")',lambda m:m[1]+og+m[2],markup)
   body_match=re.search(r'<div class="reading-spread">(.*?)(?:<section class="reference-list">|</article>)',markup,re.S)
   translated_body='\n\n'.join(normal(html.unescape(re.sub('<[^>]+>','',m[1]))) for m in re.finditer(r'<(?:p|h2)\b[^>]*>(.*?)</(?:p|h2)>',body_match[1],re.S)) if body_match else None
   def schema(m):
    def walk(v):
     if isinstance(v,list):return [walk(x) for x in v]
     if not isinstance(v,dict):return v
     d={k:walk(x) for k,x in v.items()}
     for k in ['name','description','headline','text','caption','alternativeHeadline']:
      if isinstance(d.get(k),str):d[k]=fields.get(key(normal(d[k]),l),{}).get('text',d[k])
     if d.get('@type') in ['Article','BlogPosting'] and translated_body:d['articleBody']=translated_body
     if d.get('@type') in ['WebPage','Article','BlogPosting','FAQPage']:d['inLanguage']=l
     for k in ['url','@id','mainEntityOfPage']:
      if d.get(k)==origin+'/'+name or (d.get('@type') in ['WebPage','Article','BlogPosting','FAQPage'] and d.get(k)==english_url):d[k]=canonical
     return d
    return '<script type="application/ld+json">'+json.dumps(walk(json.loads(m[1])),ensure_ascii=True)+'</script>'
   markup=re.sub(r'<script type="application/ld\+json">(.*?)</script>',schema,markup,flags=re.S);markup=alternates(install_runtime(markup,revision),name,english_url);labels=[html.escape(fields[key(s,l)]['text']) for s in NOTICE]
   credit='<aside class="translation-credit" lang="'+l+'-x-mtfrom-en"><a href="https://translate.google.com/" target="_blank" rel="noopener"><img src="assets/google-translate-attribution.png" alt="Powered by Google Translate" width="150" height="20"></a><details><summary>'+labels[0]+'</summary><p>'+labels[1]+'</p><p>'+labels[2]+'</p></details></aside>';markup=markup.replace('</main>',credit+'</main>',1);markup=markup.replace('</head>','<link rel="alternate machine-translated-from" hreflang="en" href="'+english_url+'"></head>',1)
   markup=clean_citation_sections(markup,l+'/'+name)
   path=ROOT/l/name;atomic(path,markup.encode());generated.append(path.relative_to(ROOT).as_posix())
  if previous_fingerprints.get(name)!=report['source_fingerprints'].get(name) or not complete_selector(inv.markup):atomic(ROOT/name,alternates(install_runtime(inv.markup,revision),name,english_url).encode())
 production_path=ROOT/'tools/production-pages.json'
 production=json.loads(production_path.read_text(encoding='utf-8'))
 for locale in LOCALES:production['locales'][locale]=sorted(set(production['locales'].get(locale,[]))|set(pages))
 atomic(production_path,encoded(production))
 atomic(ROOT/BASE/'routes.js',('window.paperTrailTranslationRoutes='+json.dumps(routes)+';\n').encode());atomic(ROOT/BASE/'current.json',encoded({'revision':revision,'provider':'google','routes':routes,'source_fingerprints':report['source_fingerprints'],'source_pages':len(pages)}))
 receipts=[json.loads(p.read_text(encoding='utf-8')) for p in RECEIPTS.glob('*.json')]
 ledger=ExistingBudget(private_path('DOMMYDOM_SHARED_BUDGET_DB','shared-usage.sqlite'),read_only=True)
 records=[r for r in ledger.status()['reservations'] if r['site']=='paper-trail' and r['result']!='reserved']
 calls=len(records);sent=sum(r['chars'] for r in records);successful=sum(r['characters'] for r in receipts)
 manifest=json.loads((ROOT/'assets/locales/home-blog/manifest.json').read_text(encoding='utf-8'));manifest.update(status='Saved Google translations. No visitor API calls. Native speaker review pending.',provider='google',workflow='whole-site',revision=revision,source_pages=list(pages),google_calls=calls,google_characters_sent=sent,successful_characters_saved=successful,languages=['en']+LOCALES)
 manifest.update(usage_scope='Restored incremental ledger only; historical account usage and charges remain unknown',actual_charges_usd=None)
 manifest['fields']={k:{'source':s,'source_sha256':digest(s),'origin':'google','provider_verified':True} for k,s in en.items()}
 manifest['guided_chat']={'file':'chat.json','languages':['en']+LOCALES,'phrases_per_language':len(chat['en']),'origin':'google','speaker_review':'pending'}
 atomic(ROOT/'assets/locales/home-blog/manifest.json',encoded(manifest));report.update(revision=revision,rendered=True,generated_pages=len(generated),generated=generated,total_google_calls=calls,total_google_characters_sent=sent,successful_google_characters_saved=successful,conservative_api_cost_usd=str(Decimal(sent)*20/1000000))
 urls=[origin+'/'+l+'/'+n for l in LOCALES for n,i in pages.items() if not re.search(r'<meta name="robots" content="[^"]*noindex',i.markup)];atomic(ROOT/'sitemap-translations.xml',('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+html.escape(u)+'</loc></url>' for u in urls)+'</urlset>').encode())
 robots=ROOT/'robots.txt';line='Sitemap: '+origin+'/sitemap-translations.xml'
 if robots.exists():
  text=robots.read_text(encoding='utf-8')
  if line not in text:atomic(robots,(text.rstrip()+'\n'+line+'\n').encode())
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--mode',choices=['inventory','prepare','live','refresh'],default='inventory');p.add_argument('--approve-google-calls',action='store_true');a=p.parse_args()
 if a.mode=='inventory':print(json.dumps({k:v for k,v in run(a.mode).items() if k!='_runtime_sources'},indent=2));return
 lock=ROOT/'.translation-cache/full-site.lock';lock.parent.mkdir(exist_ok=True);fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.close(fd)
 try:
  report=run(a.mode,a.approve_google_calls);print(json.dumps({k:v for k,v in report.items() if k not in ['generated','source_fingerprints','_runtime_sources']},indent=2))
 finally:lock.unlink(missing_ok=True)
if __name__=='__main__':main()
