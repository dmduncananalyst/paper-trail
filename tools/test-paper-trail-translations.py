"""Offline tests for cache reuse, changed blogs, and the shared initial limit."""
from pathlib import Path
from unittest.mock import patch
import importlib.util,json,tempfile,time,unittest
spec=importlib.util.spec_from_file_location('pt_translations',Path(__file__).with_name('paper-trail-translations.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
from translation_pipeline.budget import Budget

class CacheAndBlog(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='pt-offline-');self.addCleanup(self.tmp.cleanup);root=Path(self.tmp.name)
  original=m.ROOT
  for name in ['index.html','blog.html','assets/site.js','assets/design.js','assets/hubspot.js','assets/locales/home-blog/en.json','assets/locales/home-blog/chat.json']:
   p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((original/name).read_bytes())
  for k,v in {'ROOT':root,'CACHE':root/'.translation-cache/fields.json','RECEIPTS':root/'.translation-cache/receipts','OUT':root/'verification'}.items():
   p=patch.object(m,k,v);p.start();self.addCleanup(p.stop)
  self.root=root
 def save_all(self):
  _,refs,_,_,_=m.inventory();fields={m.key(s,l):{'source':s,'locale':l,'text':l+' '+s,'provider':'google'} for s in refs for l in m.LOCALES};m.atomic(m.CACHE,m.encoded(fields));return refs
 def test_repeat_reuses_all_results_without_dispatch(self):
  self.save_all();_,_,_,_,report=m.inventory();self.assertEqual(report['candidate_characters'],0);self.assertEqual(report['candidate_fields'],0)
 def test_new_article_and_listing_reuse_identical_title(self):
  self.save_all();title='Vendor Payments Before Month Close';body='Keep each supplier invoice connected to its approved payment.'
  (self.root/'new-blog.html').write_text('<html><head><title>'+title+'</title></head><body><h1>'+title+'</h1><p>'+body+'</p></body></html>')
  p=self.root/'blog.html';p.write_text(p.read_text(encoding='utf-8').replace('</main>','<article><h2>'+title+'</h2><p>'+body+'</p></article></main>'),encoding='utf-8')
  _,_,_,_,report=m.inventory();self.assertEqual(report['candidate_characters'],9*(len(title)+len(body)));self.assertEqual(report['candidate_fields'],18)
 def test_response_receipt_recovers_without_compacted_cache(self):
  m.atomic(m.RECEIPTS/'saved.json',m.encoded({'locale':'es','sources':['An invoice record'],'values':['Un registro de factura'],'characters':17}));fields=m.load_cache();self.assertEqual(fields[m.key('An invoice record','es')]['text'],'Un registro de factura')
 def test_public_release_recovers_without_private_cache(self):
  revision='a'*64;source='Saved recovery label';k=m.key(source,'es')
  m.atomic(self.root/m.BASE/'current.json',m.encoded({'revision':revision}))
  m.atomic(self.root/m.BASE/'releases'/revision/'fields.json',m.encoded({'provider':'google','fields':{k:{'source':source,'locale':'es','text':'Etiqueta guardada','provider':'google'}}}))
  self.assertEqual(m.load_cache()[k]['text'],'Etiqueta guardada')
 def test_stale_source_is_not_a_cache_hit(self):
  self.save_all();p=self.root/'index.html';p.write_text(p.read_text(encoding='utf-8').replace('About Paper Trail','Paper Trail Company Information'),encoding='utf-8');_,_,_,missing,_=m.inventory();self.assertTrue(all('Paper Trail Company Information' in v for v in missing.values()))

class InitialLimits(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='pt-budget-fixture-');self.addCleanup(self.tmp.cleanup);self.path=Path(self.tmp.name)/'budget.sqlite';base=Budget(self.path);now=time.time()
  s={'mode':'shared-counter','project':m.PROJECT,'period_start':now-15*86400,'period_end':now+15*86400,'approved_at':now-100,'report_reference':'OFFLINE fixture','opening_characters':500000,'all_jobs_use_counter':True,'included_reservations':[],'price_per_million':'20','soft_usd':'12','hard_usd':'15'};base.reconcile(s)
  with base.db() as c:
   c.execute('CREATE TABLE translation_funding(id TEXT PRIMARY KEY,data TEXT)');c.execute('CREATE TABLE translation_reservation_funding(reservation TEXT PRIMARY KEY,funding_id TEXT)')
   c.execute('INSERT INTO translation_funding VALUES(?,?)',('dommydom-initial-2026-10-16',json.dumps({'purpose':'initial-dommydom','project':m.PROJECT,'maximum_characters':1000,'credit_evidence':{'expires_at':now+86400,'reported_available_usd':'300'}})))
  self.initial=m.InitialBudget(self.path);m.install_initial({'candidate_cost_usd':'0.024','candidate_characters':1200,'source_fingerprints':{'fixture':'hash'}},self.initial)
 def test_cap_and_uncertain_usage_cannot_be_reset(self):
  self.assertFalse(self.initial.reserve('paper-trail',1201)['allowed']);r=self.initial.reserve('paper-trail',1200);self.assertTrue(r['allowed']);self.initial.finish(r['reservation'],'uncertain');self.assertFalse(self.initial.reserve('paper-trail',1)['allowed'])
 def test_dommydom_priority_is_preserved(self):
  q=self.initial.quote(1);self.assertEqual(q['protected_dommydom_usd'],'0.02')
 def test_other_sites_cannot_use_paper_trail_initial_allocation(self):
  with self.assertRaises(ValueError):self.initial.reserve('dommydom',10)
 def test_quoted_cost_cannot_be_exceeded(self):
  with self.assertRaises(ValueError):m.install_initial({'candidate_cost_usd':'106.00'},self.initial)

if __name__=='__main__':unittest.main()
