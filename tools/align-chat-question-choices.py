from pathlib import Path
import json,re
# Narrow, reversible correction authorized by the owner's request to audit every chat.
# Preserve each original choices array; add explicit question-specific choices only
# to the seven files inspected in the preceding read-only audit.
fixes={
'areas-we-serve.html':['Overdue books','Account balances','Monthly records','Invoices and bills'],
'can-several-months-be-corrected-at-once.html':['Overdue periods','Incorrect balances','Missing records'],
'how-long-does-it-take-to-bring-overdue-books-current.html':['Overdue periods','Missing statements','Unfinished reconciliations'],
'past-due-bookkeeping-questions.html':['Overdue periods','Missing records','Unfinished reconciliations'],
'past-due-bookkeeping.html':['Overdue periods','Missing records','Unfinished reconciliations'],
'what-should-i-do-if-my-bookkeeping-is-several-months-behind.html':['Unfinished months','Missing records','Unreconciled accounts'],
'why-does-my-bank-balance-not-match-my-books.html':['Missing transactions','Duplicate entries','Opening balance','I am not sure']}
backup={}
for name,issues in fixes.items():
 p=Path(name);s=p.read_text(encoding='utf-8');m=re.search(r'<script[^>]+id="conversation-data"[^>]*>(.*?)</script>',s,re.S);assert m
 d=json.loads(m[1]);backup[name]=d.copy();d['issueChoices']=issues
 if name!='areas-we-serve.html':d['intakePeriodChoices']=d['choices']
 s=s[:m.start(1)]+json.dumps(d,ensure_ascii=False)+s[m.end(1):];p.write_text(s,encoding='utf-8')
Path('verification/follow-up-20261016/question-choice-before.json').write_text(json.dumps(backup,indent=2),encoding='utf-8')
