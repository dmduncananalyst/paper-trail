import urllib.request
urls=['https://www.revenue.state.mn.us/sites/default/files/2026-07/m4-inst-25.pdf','https://www.dor.ms.gov/sites/default/files/tax-forms/business/2025%20CIT%20INSTRUCTIONS%2083-100%20-%20Final%20%2001.14.2026.pdf']
for u in urls:
 try:
  with urllib.request.urlopen(u,timeout=25) as r: print(r.status,r.headers.get('Content-Type'),r.read(5),u)
 except Exception as e: print(type(e).__name__,str(e))
