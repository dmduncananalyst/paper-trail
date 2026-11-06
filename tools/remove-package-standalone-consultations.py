"""Remove only the November 6 redundant pricing-section consultation controls.

No translation, network, security-configuration, Git, or release operations.
"""
from pathlib import Path
import hashlib, json, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from source_section_policy import Document

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'verification/package-consultation-removal-20261106'
LANGUAGES=['','es/','fa/','hy/','zh-CN/','ko/','tl/','te/','ru/','ar/']
KINDS=['weekly-bookkeeping','monthly-bookkeeping','bookkeeping-repair','accounts-billing','financial-analysis','payroll']
ROUTES=[language+kind+'-packages.html' for language in LANGUAGES for kind in KINDS]
def read(path):return path.read_text(encoding='utf-8')
def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists() or read(path)!=value:path.write_text(value,encoding='utf-8',newline='')
def dump(path,value):save(path,json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def sha(value):return hashlib.sha256(value.encode()).hexdigest()
def classes(node):return set(node['attrs'].get('class','').split())
def ancestors(node):
    while node:
        yield node
        node=node['parent']
def redundant(source):
    found=[]
    for node in Document(source).nodes:
        if node['tag']!='details' or 'package-consultation' not in classes(node):continue
        parents=list(ancestors(node['parent']))
        # Shared contact/inline controls and all card-contained buttons are out
        # of scope. The screenshot control belongs to the pricing section only.
        if not any('pricing-category' in classes(p) for p in parents):continue
        if any(classes(p)&{'package-plan','package-enterprise','repair-package'} for p in parents):continue
        if 'inline-consultation' in classes(node):continue
        found.append(node)
    return found
def corrected(source):
    for node in sorted(redundant(source),key=lambda n:n['start'],reverse=True):
        source=source[:node['start']]+source[node['end']:]
    return source
def capture():
    path=BASE/'approved-source.json'
    if path.exists():return json.loads(read(path))
    inventory=json.loads(read(ROOT/'tools/production-pages.json'))
    all_routes=inventory['english']+[language+'/'+name for language,names in inventory['locales'].items() for name in names]
    data={'pages':{route:read(ROOT/route) for route in ROUTES},'outside_scope_sha256':{route:sha(read(ROOT/route)) for route in all_routes if route not in ROUTES}}
    shot=Path('C:/Users/Owner/OneDrive/Pictures/Screenshots/Screenshot (561).png')
    data['reference']={'filename':shot.name,'sha256':hashlib.sha256(shot.read_bytes()).hexdigest()}
    dump(path,data)
    return data
def verify(baseline):
    removed=0;changed=[];cards=0;retained=0
    for route,before in baseline['pages'].items():
        after=read(ROOT/route)
        assert after==corrected(before),'Change exceeds the approved removal: '+route
        assert not redundant(after),'Standalone pricing consultation remains: '+route
        removed+=len(redundant(before))
        if after!=before:changed.append(route)
        def preserved_fragments(source):
            result=[]
            for node in Document(source).nodes:
                if classes(node)&{'package-plan','package-enterprise','repair-package','package-terms','package-bottom','page-conversation'}:
                    result.append(source[node['start']:node['end']])
            return result
        assert preserved_fragments(before)==preserved_fragments(after),'Card, terms, or shared contact control changed: '+route
        for node in Document(after).nodes:
            if classes(node)&{'package-plan','repair-package'}:cards+=1
            if node['tag']=='details' and 'package-consultation' in classes(node):retained+=1
    for route,expected in baseline['outside_scope_sha256'].items():
        assert sha(read(ROOT/route))==expected,'Unrelated page changed: '+route
    assert removed==40 and len(changed)==40,'Unexpected redundant-control inventory'
    result={'dedicated_pages_checked':60,'languages':10,'standalone_controls_removed':removed,'changed_pages':changed,'already_correct_pages':20,'unchanged_pricing_and_repair_cards':cards,'retained_consultation_controls':retained,'unchanged_other_pages':len(baseline['outside_scope_sha256']),'translation_api_requests':0,'forms_submitted':0}
    dump(BASE/'source-and-translation-integrity.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='changed_pages'}))
    return result
if __name__=='__main__':
    baseline=capture()
    if '--verify' not in sys.argv:
        for route,before in baseline['pages'].items():
            current=read(ROOT/route)
            assert current in {before,corrected(before)},'Unreviewed local edit: '+route
            save(ROOT/route,corrected(before))
    verify(baseline)
