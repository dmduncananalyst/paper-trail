"""Create portable preservation evidence after checking the original byte hashes."""
from pathlib import Path
import hashlib,json,subprocess,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/articles-20261113'
baseline=json.loads((OUT/'preservation-baseline.json').read_text(encoding='utf8'))
allowed={'blog.html','sitemap.xml','sitemap-translations.xml'}|{l+'/blog.html' for l in ['es','fa','hy','zh-CN','ko','tl','te','ru','ar']}
portable={}
for name,digest in baseline.items():
    if name in allowed:continue
    data=(ROOT/name).read_bytes()
    assert hashlib.sha256(data).hexdigest()==digest,name
    if name.endswith(('.html','.xml')):data=data.replace(b'\r\n',b'\n')
    portable[name]=hashlib.sha256(data).hexdigest()
(OUT/'preservation-portable.json').write_text(json.dumps(portable,indent=2)+'\n',encoding='utf8')
before={}
for name in ['sitemap.xml','sitemap-translations.xml']:
    raw=subprocess.check_output(['git','show','HEAD:'+name],cwd=ROOT)
    before[name]=[node.text for node in ET.fromstring(raw).iter() if node.tag.endswith('}loc')]
(OUT/'sitemap-baseline.json').write_text(json.dumps(before,indent=2)+'\n',encoding='utf8')
print('Preservation baseline verified and made portable; existing sitemap URLs recorded.')
