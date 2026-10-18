from pathlib import Path
from urllib.parse import urlsplit
import sys,re
if len(sys.argv)!=2:raise SystemExit('Usage: python scripts/configure-domain.py https://your-actual-domain.com')
url=sys.argv[1].rstrip('/');parts=urlsplit(url)
if parts.scheme!='https' or not parts.netloc or parts.path or parts.query or parts.fragment:raise SystemExit('Supply an HTTPS origin without a path, query or fragment.')
root=Path(__file__).resolve().parents[1];public=root/'public' if (root/'public').exists() else root
old='https://www.papertrailusa.com'
for p in public.iterdir():
 if p.suffix in ['.html','.xml','.txt']:p.write_text(p.read_text().replace(old,url))
print('Updated canonical, structured-data and sitemap URLs. Rebuild and deploy to the intended domain.')
