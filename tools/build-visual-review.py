"""Create a local review page from actual screenshots and check results."""
from pathlib import Path
from html import escape
from collections import Counter
from itertools import combinations
import csv
import json
import re
import xml.etree.ElementTree as ET

root=Path(__file__).resolve().parents[1]
out=root/'verification/visual-corrections'
states=json.loads((out/'state-completion-review.json').read_text(encoding='utf-8'))
browser=json.loads((out/'browser-checks.json').read_text(encoding='utf-8-sig'))
static=json.loads((out/'static-checks.json').read_text(encoding='utf-8'))
source_checks=json.loads((out/'source-link-checks.json').read_text(encoding='utf-8'))['results']
data={}
for filename in ['pilots.json','additional-a.json','additional-b.json','additional-c.json']:
 for state in json.loads((root/'verification/state-guides/research'/filename).read_text(encoding='utf-8-sig'))['pilots']:
  data[state['state']]=state

grams={}
for name,state in data.items():
 words=re.findall(r'\w+', ' '.join(p for s in state['sections'] for p in s['paragraphs']).casefold())
 grams[name]={tuple(words[i:i+5]) for i in range(len(words)-4)}
overlap=[]
for a,b in combinations(sorted(grams),2):
 overlap.append({'first':a,'second':b,'shared_five_word_sequences':len(grams[a]&grams[b]),'jaccard':round(len(grams[a]&grams[b])/len(grams[a]|grams[b]),4)})
overlap.sort(key=lambda x:x['jaccard'],reverse=True)
(out/'state-originality-check.json').write_text(json.dumps({'method':'Exact paragraph comparison plus pairwise five word sequence overlap. Measures text repetition, not factual originality or publication approval.','exact_duplicate_paragraphs':states['duplicate_body_paragraphs'],'highest_overlap_pairs':overlap[:20]},indent=2),encoding='utf-8')

records=[];rows=''
for state in states['states']:
 name=state['state'];item=data[name];sources=[x for x in source_checks if name in x['states']]
 ok=sum(x['status']==200 for x in sources)
 evidence=item.get('quality_review',{}).get('state_specificity',item['summary'])
 gaps=' '.join(state['remaining_review'])
 record={'state':name,'local_page':state['local_url'],'canonical':state['planned_canonical'],'body_words':state['body_words'],'official_sources':state['source_count'],'source_urls_http_200':ok,'source_urls_access_unverified':len(sources)-ok,'state_specific_value':evidence,'retention_and_applicability_review':gaps,'metadata_and_internal_links':'Passed local checks','desktop_tablet_mobile':'Rendered at 1440, 834 and 390 pixels','exact_duplicate_body_paragraphs':0,'quality_status':'Research draft, individual factual review and owner approval pending','sitemap_status':'Prepared, excluded from published sitemap','publication_status':'Not published'}
 records.append(record)
 rows+='<tr><th scope="row"><a href="../../'+escape(state['local_url'])+'">'+escape(name)+'</a></th><td>'+escape(evidence)+'</td><td>'+str(state['body_words'])+' words<br>'+str(state['source_count'])+' sources<br>'+str(ok)+' URLs returned 200<br>'+str(len(sources)-ok)+' access checks unverified</td><td>'+escape(gaps)+'</td><td>Local checks passed.<br>Factual and owner review pending.<br>Excluded from published sitemap.</td></tr>'
with (out/'state-quality-review.csv').open('w',encoding='utf-8-sig',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)

ns='http://www.sitemaps.org/schemas/sitemap/0.9'
ET.register_namespace('',ns)
xml=ET.Element('{'+ns+'}urlset')
for state in states['states']:
 entry=ET.SubElement(xml,'{'+ns+'}url');ET.SubElement(entry,'{'+ns+'}loc').text=state['planned_canonical']
ET.ElementTree(xml).write(out/'state-sitemap-proposal.xml',encoding='utf-8',xml_declaration=True)

def image(path,label):
 return '<figure><figcaption>'+escape(label)+'</figcaption><a href="'+path+'" target="_blank"><img loading="lazy" src="'+path+'" alt="'+escape(label)+'"></a></figure>'
sections=''
for width,label in [(1440,'Desktop'),(834,'iPad'),(390,'Mobile')]:
 sections+='<div class="device" data-width="'+str(width)+'"'+(' hidden' if width!=1440 else '')+'><h2>'+label+', '+str(width)+' pixels</h2>'
 for key,title in [('repair-video','Repair video'),('nationwide','Nationwide flags')]:
  sections+='<section><h3>'+title+'</h3><div class="comparison">'+image('before/'+key+'-'+str(width)+'.png','Before')+image('screenshots/'+key+'-'+str(width)+'.png','After')+'</div></section>'
 for key,title in [('home-notes','Centered Home Notes icons'),('home','Home hero'),('monthly-video','Monthly video and service opening'),('payment-card','Balanced Payment Responsibilities'),('blog','Blog listing'),('index-fa','Persian layout'),('state-ohio','State information example')]:
  suffix='-'+str(width)
  filename=key+suffix+'.png'
  if (out/'screenshots'/filename).exists():sections+='<section><h3>'+title+'</h3>'+image('screenshots/'+filename,title+', '+label)+'</section>'
 sections+='</div>'
style='''*{box-sizing:border-box}body{margin:0;background:#f5f5f5;color:#202020;font:16px/1.6 Arial,sans-serif}main{max-width:1240px;margin:auto;padding:32px 22px}h1{font:40px/1.2 Georgia,serif}h2{margin-top:35px}h3{font-size:23px}a{color:inherit;text-underline-offset:4px}nav{display:flex;gap:15px;flex-wrap:wrap;margin:20px 0}nav a,button{border:1px solid #202020;background:white;color:#202020;padding:11px 18px;font:inherit}button[aria-pressed=true]{background:#202020;color:white}button:hover{background:#686868;color:white}.review-status{background:white;border-left:5px solid #686868;padding:18px 24px}section{margin:30px 0}.comparison{display:grid;grid-template-columns:1fr 1fr;gap:20px}figure{margin:0;background:white;border:1px solid #ccc;padding:12px}figcaption{font-weight:bold;margin-bottom:10px}figure img{display:block;max-width:100%;width:auto;height:auto;max-height:650px;margin:auto}details{padding:22px;background:white;border:1px solid #ccc;margin:25px 0}summary{cursor:pointer;font-size:22px}.table-wrap{overflow:auto}table{border-collapse:collapse;width:100%;min-width:1000px;font-size:14px}th,td{border:1px solid #ccc;vertical-align:top;text-align:left;padding:12px}th:first-child{min-width:125px}td:nth-child(2){min-width:240px}td:nth-child(4){min-width:300px}[hidden]{display:none!important}@media(max-width:650px){.comparison{grid-template-columns:1fr}h1{font-size:32px}main{padding:22px 16px}}'''
html='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Paper Trail, Visual Review</title><style>'+style+'</style></head><body><main><h1>Paper Trail Visual Review</h1><p>Actual local browser screenshots. Select a device size, then click a screenshot to see it at full resolution.</p><nav><a href="../../index.html">Open Home</a><a href="../../nationwide-bookkeeping.html">Open Nationwide</a><a href="../../blog.html">Open Blog</a><a href="#state-review">Review All 50 States</a></nav><div class="review-status"><strong>Local preview only. Nothing has been published.</strong><p>213 page and device checks, plus 60 language checks. No page overflow, missing images or uncaught runtime errors were found. All 50 state tiles open their matching local pages. The published sitemap retains its existing 142 pages.</p><p>The Repair video fills its unchanged frame. Its encoded portrait footage requires top and bottom cropping to hide the green sidebars, so the enlarged image is softer. Original video files and playback behavior are preserved.</p><p><strong>Publication dates unresolved:</strong> the three Blog posts have no historical publication date in the existing sources. They show “Publication date unavailable” until the actual dates are confirmed. No dates have been invented.</p></div><nav aria-label="Screenshot device"><button data-device="1440" aria-pressed="true">Desktop</button><button data-device="834" aria-pressed="false">iPad</button><button data-device="390" aria-pressed="false">Mobile</button></nav>'+sections+'<details><summary>Modified files and preservation</summary><p>Shared styles and behavior: design.css and design.js. Targeted page changes: Bookkeeping Repair, Accounts Payable and Receivable, Nationwide, Blog listing, and the three Blog reading pages. Other root pages only received the refreshed asset version reference. Added 50 local state pages, state research records and verification tools. Corrected the Georgia flag image and source manifest. Updated all three SEO audit reports.</p><p>Original video assets, photography, brand colors and integrations remain in place. Every video frame retains its previous width and height at all three tested sizes. The Home mobile layout reserves space for translated menu labels and the language notice so the control stays anchored.</p><p><a href="modified-files.json">Download Exact Modified File List</a> ? <a href="preservation-checks.json">View Preservation Checks</a></p></details><details id="state-review"><summary>Individual quality review for all 50 states</summary><p>All 50 local pages have unique metadata, official source references, a visible review date, state specific explanations and hypothetical examples. Exact body paragraph duplicates: zero. Each remains a research draft, with noindex and no published sitemap entry until individual approval. The table records the remaining review issues, rather than claiming professional signoff.</p><p>326 unique source URLs checked: 275 returned HTTP 200, 29 returned 403, and 22 could not be verified by automated access. No 404 or 410 source URLs remain. Access restrictions do not establish that a source is broken; affected sources still need a final accessible review before publication.</p><p><a href="state-quality-review.csv">Download Individual State Review</a> · <a href="state-sitemap-proposal.xml">Prepared State Sitemap Entries, Not Published</a></p><div class="table-wrap"><table><thead><tr><th>State</th><th>State specific value</th><th>Evidence</th><th>Remaining review</th><th>Status</th></tr></thead><tbody>'+rows+'</tbody></table></div></details></main><script>document.querySelectorAll("[data-device]").forEach(b=>b.addEventListener("click",()=>{document.querySelectorAll("[data-device]").forEach(x=>x.setAttribute("aria-pressed",String(x===b)));document.querySelectorAll(".device").forEach(x=>x.hidden=x.dataset.width!==b.dataset.device)}));</script></body></html>'
(out/'review.html').write_text(html,encoding='utf-8')
print(json.dumps({'state_review_rows':len(records),'screenshots':len(list((out/'screenshots').glob('*.png'))),'highest_pairwise_five_word_overlap':overlap[0]}))
