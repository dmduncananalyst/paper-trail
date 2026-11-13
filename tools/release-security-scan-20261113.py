"""Read staged release blobs and report suspected secret paths/types, never values."""
from pathlib import Path
import hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/articles-20261113'
names=subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=ROOT).decode().split('\0')
names=[n for n in names if n]
assert names,'No staged release files to scan'
patterns={
 'private key':rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----',
 'GitHub token':rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,})\b',
 'Google API key':rb'\bAIza[A-Za-z0-9_-]{35}\b',
 'AWS access key':rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
 'service account credential':rb'"type"\s*:\s*"service_account"',
 'OAuth or session secret':rb'"(?:refresh_token|access_token|client_secret|session_token)"\s*:\s*"[^"\s]{15,}"'
}
findings=[];inventory=[]
for name in names:
    data=subprocess.check_output(['git','show',':'+name],cwd=ROOT)
    inventory.append({'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    if name.endswith(('.jpg','.png','.webp','.woff','.woff2')):continue
    for kind,pattern in patterns.items():
        if re.search(pattern,data):findings.append({'path':name,'exposure_type':kind})
result={'staged_files':len(names),'findings':findings,'inventory':inventory}
(OUT/'staged-security-review.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps({'staged_files':len(names),'findings':findings},indent=2))
if findings:raise SystemExit(1)
