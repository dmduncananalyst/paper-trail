"""Add useful supporting detail to the service cards with large empty areas."""
from pathlib import Path
from html import escape
import re
import json

root=Path(__file__).resolve().parents[1]
copy={
('paper-trail-services.html','Financial Reports'):[
'A report is easier to review when its balances can be traced to a statement or supporting schedule. Identify the reporting period, the accounts included and the information still missing. That separates an unexplained number from a balance that has actually been checked.',
'Keep the original report and the revised version with the correction record. Comparing the same reporting dates and accounting basis helps show the effect of a change without confusing it with activity from a different month.',
'Where a missing statement or an unanswered transaction question affects the figures, identify the limitation with the report. The owner and tax professional can then see which information is supported and which part of the review remains open.'],
('paper-trail-monthly-bookkeeping.html','Financial Reports'):[
'Read the income statement alongside the balance sheet and the supporting account schedules. A customer payment can reduce an existing receivable, while a loan payment can affect both a liability and interest expense. The bank withdrawal alone does not explain those differences.',
'Use the same closing date and reporting basis when comparing months. Preserve the report version supplied to the owner so later changes can be explained against the information previously reviewed, rather than relying on memory.',
'Keep follow up items specific. A missing card receipt, an unapplied customer payment and a supplier credit each need different evidence. Recording the responsible person and the next action makes the monthly conversation more useful than a general request to check the books.'],
('balancing-corrections.html','Completed Periods'):[
'Keep the earlier reconciliation report and the statement used to complete it. If a later correction changes that period, retain the connection between the original entry, the adjustment and the updated balance.',
'Review connected accounts as well. Moving a payment between bank accounts can affect two reconciliations, so closing one difference does not establish that the other account is correct.'],
('transaction-categorization.html','Uncertain Transactions'):[
'A useful query includes the original description and a specific question about business purpose. Ask whether a payment settled an existing bill, bought an asset or reimbursed someone. The answer should determine the supported category rather than the category being chosen merely to finish a batch.',
'Keep the explanation with the underlying receipt or invoice. A vendor name can identify who received the money while still leaving the purpose unclear, especially where the same supplier provides several kinds of goods or services.',
'For a payment covering several purchases, preserve the invoice detail and identify the parts that need separate treatment. If the owner cannot supply enough information, retain that limitation for review instead of creating a confident description that the evidence does not support.'],
('past-due-bookkeeping.html','Unresolved Transactions'):[
'Use a separate query list for the missing information, with the transaction date, amount and the document or explanation needed. A payment awaiting a receipt should remain distinguishable from an account with an entire statement missing.',
'Resolve connected activity together. A customer deposit may relate to an invoice entered in another month, while a card payment may settle purchases already recorded. Preserve those links when rebuilding earlier periods.'],
('year-end-bookkeeping.html','Year-End Handoff'):[
'Group the handoff by reporting period and account, with reconciliations and supporting documents next to the balances they explain. Include the version of the reports supplied so later questions refer to the same figures.',
'Separate completed work from items awaiting an owner response or a tax professional decision. Asset purchases, outstanding loans and unresolved customer balances should remain visible with the evidence available for each item.'],
('tax-ready-bookkeeping.html','Reports and Supporting Records'):[
'Connect significant balances to their supporting schedules, such as unpaid invoices, supplier bills, loans and asset purchases. The report total and the detailed list should use the same reporting date.',
'Keep unusual transactions and unanswered questions in the handoff. A clear description of what is known, what is missing and which document supports an entry is more useful than an unexplained figure presented as final.'],
('income-expense-tracking.html','Period Comparisons'):[
'Compare the same reporting periods and identify changes in how transactions were recorded. A payment received this month may settle an older invoice, so a change in deposits does not necessarily describe a change in current sales.',
'Retain a short explanation for significant variations, with the invoice or transaction detail behind it. That gives later reviews a factual starting point without assuming every unusual month will repeat.'],
('bank-credit-card-balancing.html','Account Review'):[
'Maintain an account list that includes inactive accounts, replacement cards and accounts with only occasional activity. Keep each statement and its ending balance connected to the correct account, rather than treating a quiet account as one that no longer needs review.',
'Follow transfers through both sides of the records. A payment from checking to a business card should agree with the corresponding credit on the card account. Different posting dates can explain timing, but they should not hide an amount that never arrived.',
'For an unresolved difference, preserve the statement line, bookkeeping entry and the question still open. This makes the next review specific and allows a later correction to be traced without reopening unrelated transactions or losing the earlier reconciliation evidence.'],
('monthly-financial-reports.html','Financial Comparisons'):[
'Choose the comparison that fits the question. The previous month may help explain a recent change, while the same month in an earlier year may provide better context for seasonal activity. Keep the accounting basis and reporting dates consistent before interpreting the difference.',
'Trace a significant movement back to the underlying records. Changes in unpaid invoices, supplier bills or inventory can affect the financial picture even when the bank balance looks familiar. A cash movement and an operating result should not be treated as interchangeable explanations.',
'Preserve the report version discussed with the owner and a short explanation of the material changes. If a later correction alters an earlier period, identify the revised figures. Comparisons become less useful when one month includes corrections that the other version does not reflect.'],
('monthly-bookkeeping-review.html','Unresolved Items'):[
'Give each open item a clear description, the evidence needed and a person responsible for responding. Distinguish a missing invoice from an unmatched payment or a transaction whose business purpose is still unclear.',
'Carry unresolved items forward with their original references rather than recreating them as a new list each month. When an item is resolved, retain the supporting document and the explanation of the resulting change so the next review can follow the decision.']}
changed=[]
for (filename,heading),paragraphs in copy.items():
 p=root/filename;t=p.read_text(encoding='utf-8')
 pattern=r'(<h3>'+re.escape(heading)+r'</h3><div class="section-copy">)(.*?)(</div></section>)'
 def add(match):
  if 'follow-up-copy' in match[2]:return match[0]
  return match[1]+match[2]+''.join('<p class="follow-up-copy">'+escape(s)+'</p>' for s in paragraphs)+match[3]
 t,n=re.subn(pattern,add,t,count=1,flags=re.S)
 assert n==1,(filename,heading)
 t=t.replace('<h3>Year-End Handoff</h3>','<h3>Year End Handoff</h3>')
 p.write_text(t,encoding='utf-8');changed.append({'file':filename,'heading':heading,'paragraphs_added':len(paragraphs)})
(root/'verification/follow-up-20261016/card-copy-changes.json').write_text(json.dumps(changed,indent=2),encoding='utf-8')
print('Balanced supporting copy on',len(changed),'service pages.')
