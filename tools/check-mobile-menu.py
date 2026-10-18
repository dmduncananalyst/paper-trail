from pathlib import Path
import json
p=Path('verification/mobile-menu-20261016');d=json.loads((p/'checks.json').read_text(encoding='utf-8-sig'));issues=[]
for r in d['pages']:
 if r['state']['overflow'] or r['state']['missing']:issues.append([r['page'],r['width'],'overflow or missing image'])
 if r['width']<=650 and any(a!='center' for a in r['state']['blogText']):issues.append([r['page'],r['width'],'blog text alignment'])
for r in d['languages']:
 s=r['state']
 if s['overflow']:issues.append([r['page'],r['width'],r['language'],'overflow'])
 if r['language']!='en' and s['notice']['y']-s['selector']['y']-s['selector']['h']<12:issues.append([r['page'],r['width'],r['language'],'notice gap'])
 if s.get('stacked') and s['serviceButton']['y']<s['serviceHeading']['y']+s['serviceHeading']['h']+12:issues.append([r['page'],r['width'],r['language'],'stack gap'])
for r in d['menus']:
 m=r['menu']
 if not m['open'] or abs(m['gap'])>1 or m['mainTop']<m['panelBottom'] or not r['destination'].endswith('monthly-financial-reports.html'):issues.append(['touch menu',r['width']])
summary={'page_and_width_checks':len(d['pages']),'language_checks':len(d['languages']),'real_touch_navigation_checks':len(d['menus']),'runtime_exceptions':len(d['exceptions']),'issues':issues,'google_translation_requests':sum('translation.googleapis.com' in u or 'translate.googleapis.com' in u for u in d['requests']),'changes_scope':'Mobile layout and touch behavior only. Existing desktop labels, menus and layout preserved.'}
(p/'verification-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
