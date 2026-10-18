"""Build the local screenshot handoff without network calls."""
from pathlib import Path
import html,json
root=Path(__file__).resolve().parents[1]
out=root/'verification/google-translation-20261016'
def read(name):return json.loads((out/name).read_text(encoding='utf-8-sig'))
b=read('browser-checks.json');c=read('chat-flow-checks.json')
manifest=json.loads((root/'assets/locales/home-blog/manifest.json').read_text(encoding='utf-8'))
static=read('static-checks.json') if (out/'static-checks.json').exists() else None
parts=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Paper Trail saved Google translations review</title><style>body{font:17px/1.6 system-ui;margin:32px auto;padding:0 24px;max-width:1150px;color:#222}a{color:#165b77}img{max-width:100%;height:auto;border:1px solid #bbb}figure{margin:20px 0}summary{cursor:pointer;font-weight:600}nav{display:flex;flex-wrap:wrap;gap:16px}.gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:24px}code{overflow-wrap:anywhere}</style><h1>Paper Trail saved Google translations</h1><p>Local review only. No commit, push, or publication was performed.</p><p>192 English pages translated into nine languages, producing 1,728 saved language pages. Google Translate attribution appears at the bottom, before the footer. The globe and selector now appear in every page header, to the left of the phone number. Visits and language switching do not call the translation API.</p><p>5,223,994 characters sent in 1,234 requests, including a failed 4,471 character request retained in the conservative cost calculation. Estimated API charge before credits: <strong>$104.48</strong>. Another 252 characters were reused from saved Google results. This is usage accounting, not a live billing statement. Existing shared monthly allowance and Dami Dom priority were preserved.</p>']
parts.append(f'<p>Original translation browser checks: {len(b["layouts"])} page, language, and width combinations. Complete translated Home and Blog chat flows: {len(c["checks"])}. No observed overflow, missing images, JavaScript exceptions, or browser translation API requests in these checks. The latest header and button corrections have a separate review below.</p>')
parts[0]=parts[0].replace('5,223,994 characters sent in 1,234 requests',f'{manifest["google_characters_sent"]:,} characters sent in {manifest["google_calls"]:,} requests')
if static:parts.append('<p>Offline audit: '+str(static['translated_pages'])+' translated pages, '+str(static['local_links_checked'])+' local links, '+str(static['media_references_checked'])+' media references. Issues: '+str(len(static['issues']))+'.</p>')
parts.append('<p>The 50 state pages and their 450 translated copies remain unapproved drafts, retain noindex, and are excluded from the sitemaps. Translation does not verify legal claims. Native speaker review of machine translation remains pending.</p><nav><a href="../../Paper-Trail-Saved-Google-Translations.txt">Saving and future Blog workflow</a><a href="static-checks.json">Full offline checks</a><a href="browser-checks.json">Browser checks</a><a href="chat-flow-checks.json">Chat checks</a><a href="navigation-checks.json">Mobile menu navigation checks</a><a href="offline-repeat-check.json">Saved translation reuse check</a><a href="../state-content-replacement-20261016/review.html">State factual review</a></nav><h2>Saved pages</h2>')
for code,name in [('es','Spanish'),('fa','Persian'),('hy','Armenian'),('zh-CN','Chinese'),('ko','Korean'),('tl','Tagalog'),('te','Telugu'),('ru','Russian'),('ar','Arabic')]:
 parts.append('<p>'+name+': '+ ' | '.join('<a href="../../'+code+'/'+page+'">'+label+'</a>' for page,label in [('index.html','Home'),('blog.html','Blog'),('monthly-financial-reports.html','Service'),('state-records/california.html','State draft')])+'</p>')
if (out/'city-row-checks.json').exists():
 parts.append('<h2>Single line city row</h2><p>City links stay on one line at 14 to 15 pixels. On narrow screens, the row scrolls horizontally so every city remains readable and accessible.</p><p><a href="city-row-checks.json">City row checks</a></p><div class="gallery">')
 for width in [390,834,1280,1440]:
  file=f'screenshots/city-row-en-{width}.png'
  parts.append(f'<figure><a href="{file}"><img loading="lazy" src="{file}" alt="Single line city row at {width} pixels"></a><figcaption>{width} pixels</figcaption></figure>')
 parts.append('</div>')
if (out/'footer-correction-checks.json').exists():
 parts.append('<h2>Latest footer correction</h2><p>First row: Home, About, Services, Notes, Nationwide, phone, and email. The second row retains all ten cities. The third row retains the existing copyright and website credit.</p><p><a href="footer-correction-checks.json">Footer layout checks</a></p><div class="gallery">')
 for width in [390,834,1440]:
  for code in ['en','es']:
   file=f'screenshots/footer-{code}-{width}.png'
   parts.append(f'<figure><a href="{file}"><img loading="lazy" src="{file}" alt="{code} footer at {width} pixels"></a><figcaption>{code}, {width} pixels</figcaption></figure>')
 parts.append('</div>')
if (out/'header-correction-checks.json').exists():
 latest=read('header-correction-checks.json')
 parts.append('<h2>Latest header, attribution, and button corrections</h2><p>The selector and globe now appear on every page, to the left of the phone number. The Google badge is centered. The two service actions form a vertical stack, with 28 to 32 pixels after the cards and 20 pixels between the buttons.</p><p><a href="header-correction-checks.json">Latest layout measurements</a></p><div class="gallery">')
 for width in [390,834,1440]:
  for kind,code,label in [('header-en-index','en','English header'),('buttons-es','es','Spanish bottom actions'),('centered-google-credit','es','Centered Google Translate credit')]:
   file=f'screenshots/{kind}-{width}.png'
   if (out/file).exists():parts.append(f'<figure><a href="{file}"><img loading="lazy" src="{file}" alt="{label} at {width} pixels"></a><figcaption>{label}, {width} pixels</figcaption></figure>')
 parts.append('</div>')
parts.append('<h2>Translation screenshots before the latest header correction</h2><p>390 pixels, phone. 834 pixels, iPad. 1440 pixels, desktop. See the latest correction screenshots above for the current selector placement.</p>')
for width in [390,834,1440]:
 parts.append('<h3>'+str(width)+' pixels</h3><div class="gallery">')
 for code,page,label in [('es','credit','Spanish Blog with Google credit'),('hy','index','Armenian Home'),('fa','monthly-financial-reports','Persian service')]:
  file=f'screenshots/{code}-{page}-{width}.png'
  parts.append(f'<figure><a href="{file}"><img loading="lazy" src="{file}" alt="{html.escape(label)} at {width} pixels"></a><figcaption>{label}</figcaption></figure>')
 parts.append('</div>')
parts.append('<h2>Translated chat review screens</h2><div class="gallery">')
for code in ['es','fa','hy','zh-CN','ko','tl','te','ru','ar']:
 file=f'screenshots/{code}-chat-review.png'
 parts.append(f'<details><summary>{code}</summary><a href="{file}"><img loading="lazy" src="{file}" alt="{code} translated chat review"></a></details>')
parts.append('</div><h2>Mobile dropdown menus</h2><div class="gallery">')
for code in ['es','fa','hy','zh-CN','ko','tl','te','ru','ar']:
 file=f'screenshots/{code}-mobile-menu.png'
 if (out/file).exists():parts.append(f'<details><summary>{code}</summary><a href="{file}"><img loading="lazy" src="{file}" alt="{code} open mobile dropdown"></a></details>')
parts.append('</div></html>');(out/'review.html').write_text(''.join(parts),encoding='utf-8')
print('Wrote',out/'review.html')

