import json,re
from pathlib import Path
p=Path('verification/state-guides/research/additional-b.json');d=json.loads(p.read_text(encoding='utf8'))
for code,title,url,claims in [('MT','Montana Reimbursable Employers','https://uid.dli.mt.gov/employers/reimbursable-employers',['Reimbursement status distinct from regular employer contributions and quarterly wage reporting.']),('NM','New Mexico Quarterly Wage And Contribution Report','https://www.dws.state.nm.us/Portals/0/DM/Business/ES903_AB_Employers_Quarterly_Wage_Contribution_Report.pdf',['Total, excess and taxable wages and contribution calculation.'])]:
 x=next(x for x in d['pilots'] if x['code']==code);sid=code+str(len(x['sources'])+1)
 x['sources'].append({'id':sid,'title':title,'url':url,'claims':claims,'checked_on':'2026-10-16','verification':'Official agency content inspected in current web results.'})
 next(s for s in x['sections'] if s['heading']=='Unemployment Contributions And Wage Reports')['source_ids'].append(sid)
# Current specialist scope is now applicability and record retention, not omission of UI discussion.
for x in d['pilots']:
 x['quality_review']['currency']='Income and entity tax and employer unemployment reporting separately checked October 16, 2026. No rate or filing deadline assumed.'
 x['quality_review']['review_depth']='Individual income and employer sections explain actual state taxes, conditional applicability, liability reconciliations and annual handoff evidence.'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
paras={};bad=[]
for x in d['pilots']:
 ids={s['id'] for s in x['sources']}
 for s in x['sections']:
  assert set(s['source_ids'])<=ids
  for t in s['paragraphs']:paras.setdefault(t,[]).append(x['code'])
 assert sum(s['heading']=='Business Income And Entity Tax Records' for s in x['sections'])==1
 assert sum(s['heading']=='Unemployment Contributions And Wage Reports' for s in x['sections'])==1
 print(x['code'],sum(len(t.split()) for s in x['sections'] for t in s['paragraphs']),len(x['sources']))
assert not [a for a,b in paras.items() if len(b)>1]
print('Total body words',sum(len(t.split()) for x in d['pilots'] for s in x['sections'] for t in s['paragraphs']))
print('Total sources',sum(len(x['sources']) for x in d['pilots']))
print('All references and distinct paragraphs pass')
