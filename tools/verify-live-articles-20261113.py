"""Read-only GitHub Pages release verification; no credentials or writes to GitHub."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin
import argparse,hashlib,html,json,re,subprocess,time,requests,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/articles-20261113'
ORIGIN='https://www.papertrailusa.com/'
REPO='https://api.github.com/repos/dmduncananalyst/paper-trail'
LANGS=['','es','fa','hy','zh-CN','ko','tl','te','ru','ar']
REJECTED=['how-much-does-a-bookkeeper-cost-for-small-businesses.html','why-every-small-business-needs-a-bookkeeper.html','how-to-choose-a-bookkeeper-for-your-small-business.html','what-to-look-for-when-hiring-a-bookkeeper-in-2025.html']
A=json.loads((OUT/'approved-content.json').read_text(encoding='utf8'))
def github(path):
    r=requests.get(REPO+path,headers={'Accept':'application/vnd.github+json'},timeout=45)
    r.raise_for_status();return r.json()
def report(path,value):
    path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf8')
def workflow(sha):
    runs=github('/actions/runs?head_sha='+sha)['workflow_runs']
    runs=[r for r in runs if r['path']=='.github/workflows/pages.yml']
    if not runs:return {'state':'waiting','commit':sha}
    run=runs[0]
    return {'state':run['status'],'conclusion':run['conclusion'],'commit':run['head_sha'],'url':run['html_url'],'id':run['id']}
def normalize(s):return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',s))).strip()
def page(route):
    url=ORIGIN+route;r=requests.get(url,timeout=60);r.raise_for_status()
    source=r.content.decode('utf8');local=(ROOT/route).read_text(encoding='utf8')
    def body(s):
        m=re.search(r'<article\b[^>]*class="[^"]*reading-feature.*?</article>',s,re.S)
        return normalize(m[0]) if m else None
    assert body(source)==body(local),route+': live full article differs'
    assert re.findall(r'<img\b[^>]*>',source)==re.findall(r'<img\b[^>]*>',local),route+': photograph or alt text differs'
    for pattern in [r'<title>(.*?)</title>',r'<meta name="description" content="([^"]*)"',r'<link rel="canonical" href="([^"]*)"',r'<script type="application/ld\+json">(.*?)</script>']:
        live=re.search(pattern,source,re.S);saved=re.search(pattern,local,re.S)
        assert live and saved and live[1]==saved[1],route+': live metadata differs'
    assert len(re.findall(r'rel="alternate" hreflang=',source))==11,route+': hreflang'
    return {'route':route,'status':r.status_code,'full_article_and_metadata':'match local verified source'}
def live(sha):
    state=workflow(sha)
    assert state['commit']==sha and state['conclusion']=='success',state
    deployments=github('/deployments?sha='+sha)
    deployments=[d for d in deployments if d['environment']=='github-pages']
    assert deployments,'No matching Pages deployment'
    statuses=github('/deployments/'+str(deployments[0]['id'])+'/statuses')
    assert statuses[0]['state']=='success',statuses[0]['state']
    routes=[(l+'/' if l else '')+a['slug'] for l in LANGS for a in A]
    oldarchive=subprocess.check_output(['git','show',sha+'^:blog.html'],cwd=ROOT).decode('utf8')
    oldcards=re.findall(r'<article\b[^>]*class="[^"]*\bblog-story\b[^"]*"[^>]*>.*?</article>',oldarchive,re.S)
    older=[html.unescape(re.findall(r'<a\b[^>]*href="([^"]+)"',c)[-1]) for c in oldcards]
    oldroutes=[(l+'/' if l else '')+s for l in LANGS for s in older]
    with ThreadPoolExecutor(max_workers=8) as pool:
        new=list(pool.map(page,routes));preserved=list(pool.map(page,oldroutes))
    maps={}
    for filename in ['sitemap.xml','sitemap-translations.xml']:
        r=requests.get(ORIGIN+filename,timeout=60);r.raise_for_status()
        maps[filename]={n.text for n in ET.fromstring(r.content).iter() if n.tag.endswith('}loc')}
        for slug in REJECTED:assert not any(u.endswith('/'+slug) for u in maps[filename]),slug
    for route in routes:
        assert ORIGIN+route in maps['sitemap-translations.xml' if '/' in route else 'sitemap.xml'],route
    images=[]
    for a in A:
        r=requests.get(ORIGIN+a['image'],timeout=60);r.raise_for_status()
        assert r.content==(ROOT/a['image']).read_bytes(),a['image']
        images.append({'image':a['image'],'status':r.status_code,'sha256':hashlib.sha256(r.content).hexdigest()})
    oldimages=set()
    for slug in older:
        s=(ROOT/slug).read_text(encoding='utf8')
        oldimages.update(re.findall(r'<img\b[^>]*src="(assets/(?:photos|blog-leads-20261103)/[^"]+)"',s))
    for path in oldimages:
        r=requests.get(ORIGIN+path,timeout=60);r.raise_for_status()
        assert r.content==(ROOT/path).read_bytes(),path+': prior photograph changed'
    archives=[]
    for lang in LANGS:
        route=(lang+'/' if lang else '')+'blog.html';r=requests.get(ORIGIN+route,timeout=60);r.raise_for_status()
        for a in A:
            target=(lang+'/' if lang else '')+a['slug']
            assert 'href="'+target+'"' in r.text,route+': missing '+target
        assert not any(slug in r.text for slug in REJECTED),route+': rejected URL'
        archives.append(route)
    result={'commit':sha,'workflow':state,'deployment_state':statuses[0]['state'],'deployment_url':statuses[0].get('environment_url'),'new_articles':len(new),'older_blog_pages_verified':len(preserved),'prior_photographs_verified':len(oldimages),'photographs':images,'archives':archives,'rejected_urls_absent':REJECTED,'publication_date':'2026-11-13','errors':[]}
    report(OUT/'live-verification.json',result)
    print(json.dumps(result,indent=2))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--commit',required=True);parser.add_argument('--status-only',action='store_true');args=parser.parse_args()
    if args.status_only:print(json.dumps(workflow(args.commit),indent=2))
    else:live(args.commit)
