"""Read-only HTTP checks for cited state sources, no translation services."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlparse
import json

root=Path(__file__).resolve().parents[1]
folder=root/'verification/state-guides/research'
urls={}
for filename in ['pilots.json','additional-a.json','additional-b.json','additional-c.json']:
    path=folder/filename
    if not path.exists():continue
    for state in json.loads(path.read_text(encoding='utf-8-sig')).get('pilots',[]):
        for source in state['sources']:
            urls.setdefault(source['url'],set()).add(state['state'])
def check(url):
    host=urlparse(url).hostname or ''
    if 'google' in host:
        return {'url':url,'status':'Skipped, forbidden provider host','states':sorted(urls[url])}
    try:
        req=Request(url,headers={'User-Agent':'PaperTrailLocalContentReview/1.0'})
        with urlopen(req,timeout=18) as response:
            response.read(1024)
            result={'url':url,'status':response.status,'resolved_url':response.url,'content_type':response.headers.get('Content-Type','')}
    except HTTPError as error:
        result={'url':url,'status':error.code,'detail':str(error)}
    except Exception as error:
        result={'url':url,'status':'Access not verified','detail':str(error)}
    result['states']=sorted(urls[url])
    return result
with ThreadPoolExecutor(max_workers=6) as executor:
    results=list(executor.map(check,sorted(urls)))
report={'checked_on':'2026-10-16','method':'Read-only GET, first 1024 bytes. Access check only, not claim verification. Some government sites restrict automated access.','results':results}
(root/'verification/visual-corrections/source-link-checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'sources':len(results),'http_success':sum(isinstance(x['status'],int) and 200<=x['status']<400 for x in results),'not_found':[x['url'] for x in results if x['status'] in [404,410]],'access_unverified':sum(not isinstance(x['status'],int) or x['status']>=400 for x in results)}))
