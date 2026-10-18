"""Read-only Google configuration audit. Never dispatches a translation."""
from pathlib import Path
import sys,json,time,urllib.request,urllib.error
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root.parent/'sun-and-sage/scripts'))
from translation_pipeline.connection import access_token,private_path
from translation_pipeline.budget import ExistingBudget
project='project-2e0d7d9d-d482-4fcf-b6d'
out=root/'verification/dns-readiness-20261016';out.mkdir(parents=True,exist_ok=True)
report={'checked_at_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'translation_requests':0,'settings_changed':False,'approved_ongoing_sites':['dommydom','paper-trail']}
budget=ExistingBudget(private_path('DOMMYDOM_SHARED_BUDGET_DB','shared-usage.sqlite'),read_only=True)
status=budget.status();report['application_quote']=budget.quote(0)
report['sites_with_recorded_usage']=sorted({r['site'] for r in status['reservations']})
report['reservation_counts']={site:sum(r['site']==site for r in status['reservations']) for site in report['sites_with_recorded_usage']}
try:
 token=access_token()
 def get(url):
  with urllib.request.urlopen(urllib.request.Request(url,headers={'Authorization':'Bearer '+token,**({'x-goog-user-project':project} if url.startswith('https://billingbudgets.googleapis.com/') else {})}),timeout=35) as response:return json.load(response)
 for name,url in [('service','https://serviceusage.googleapis.com/v1/projects/'+project+'/services/translate.googleapis.com'),('billing','https://cloudbilling.googleapis.com/v1/projects/'+project+'/billingInfo'),('quotas','https://serviceusage.googleapis.com/v1beta1/projects/'+project+'/services/translate.googleapis.com/consumerQuotaMetrics?view=FULL&pageSize=200')]:
  try:
   data=get(url)
   if name=='service':report['translation_api_enabled']=data.get('state')=='ENABLED'
   elif name=='billing':
    report['billing_enabled']=data.get('billingEnabled') is True
    account=data.get('billingAccountName')
    if account:
     try:
      budgets=get('https://billingbudgets.googleapis.com/v1/'+account+'/budgets')
      report['billing_budgets']=[{'display_name':b.get('displayName'),'amount':b.get('amount'),'threshold_rules':b.get('thresholdRules'),'default_iam_notifications_enabled':not b.get('notificationsRule',b.get('allUpdatesRule',{})).get('disableDefaultIamRecipients',False),'notification_channels':b.get('notificationsRule',b.get('allUpdatesRule',{})).get('monitoringNotificationChannels',[]),'scope_filter':b.get('budgetFilter')} for b in budgets.get('budgets',[])]
     except urllib.error.HTTPError as e:report['billing_budgets_error']='HTTP '+str(e.code)
   else:
    report['quota_metrics']=data.get('metrics',[])
  except urllib.error.HTTPError as e:report[name+'_error']='HTTP '+str(e.code)
except Exception as e:report['account_verification_error']=type(e).__name__
report['limitation']='Application pause applies to coordinated callers. It is not an account-wide Google hard cap. Credits and invoice charges are not a live verified balance.'
(out/'cloud-configuration-checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['quota_metrics','billing_budgets']},indent=2))
