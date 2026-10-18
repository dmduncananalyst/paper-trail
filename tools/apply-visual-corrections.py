"""Local, targeted changes from the October 16 visual correction brief."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
css = root / 'assets/design.css'
if '/* October 16 visual corrections.' in css.read_text(encoding='utf-8'):
    raise SystemExit('This one-time correction pass is already applied.')
css.write_text(css.read_text(encoding='utf-8') + '''
/* October 16 visual corrections. Keep the existing media frame geometry. */
.pt-interior .hero.video-hero .video-frame.repair-footage video{position:absolute;width:309.18%;height:309.18%;max-width:none;left:50%;top:50%;transform:translate(-50%,-50%);object-fit:fill}
.pt-header,.pt-nav,.header-tools,.page-language{direction:ltr!important}
.rtl-content [data-i18n]{direction:rtl;unicode-bidi:plaintext}
.page-language{min-height:48px}
.pt-home .home-note-copy>.pt-icon,.pt-home .home-note-copy>.note-emblem{align-self:center;margin-inline:auto}
.pt-home .about-content>div{text-align:center}
.pt-interior .opening-copy>.action,.pt-interior .opening-copy>.btn{display:table;margin-inline:auto}
.pt-interior .hero-copy>.action,.pt-interior .hero-copy>.btn{display:table;margin-inline:auto}
.pt-service-directory .service-opening .hero-copy{display:flex;flex-direction:column;align-items:center;justify-content:center}
.pt-service-directory .service-opening h1{align-self:stretch;margin-bottom:30px}
.pt-service-directory .service-opening .summary{margin:0 0 16px}
.pt-service-directory .service-opening .hero-copy>.action{margin-top:0}
.state-mosaic{grid-template-columns:repeat(5,minmax(0,1fr));gap:14px}
.state-mosaic li{padding:0;display:block;background:#f6f6f6}
.state-mosaic li>a,.state-mosaic li>.state-entry{display:flex;flex-direction:column;align-items:center;gap:10px;padding:15px 12px;text-decoration:none;color:#202020;height:100%}
.state-mosaic img{width:100%;height:108px;object-fit:contain;max-width:210px}
.state-mosaic .state-name{font-size:16px;min-height:24px;line-height:1.4}
.state-mosaic .state-action{font-size:12px;line-height:1.5;text-decoration:underline;text-underline-offset:4px;min-height:24px}
.state-mosaic a:hover,.state-mosaic a:focus-visible{background:#e6e6e6;outline-offset:3px}
.publication-date{font-size:14px;line-height:1.6;color:#505050;margin:0 0 18px}
.publication-date.missing{font-style:italic}
@media(max-width:980px){.state-mosaic{grid-template-columns:repeat(4,minmax(0,1fr))}.state-mosaic img{height:100px}}
@media(max-width:650px){.state-mosaic{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.state-mosaic img{height:92px}.state-mosaic li>a,.state-mosaic li>.state-entry{padding:13px 10px}.state-mosaic .state-name{font-size:15px}.state-mosaic .state-action{font-size:11px}.page-language{min-height:66px}.pt-service-directory .service-opening h1{margin-bottom:26px}}
''', encoding='utf-8')

js = root / 'assets/design.js'
t = js.read_text(encoding='utf-8')
t = t.replace("document.documentElement.dir=rtl?'rtl':'ltr';", "document.documentElement.dir='ltr';document.body.classList.toggle('rtl-content',rtl);")
js.write_text(t, encoding='utf-8')

p=root/'paper-trail-services.html'
t=p.read_text(encoding='utf-8').replace('<div class="video-frame">','<div class="video-frame repair-footage">',1)
p.write_text(t,encoding='utf-8')

p=root/'accounts-payable-receivable.html'
t=p.read_text(encoding='utf-8')
pattern=r'(<h3>Payment Responsibilities</h3><div class="section-copy">)(.*?)(</div></section>)'
def expand(m):
    return m[1]+m[2]+'<p>Keep the approval record with the invoice and payment reference. If an invoice is disputed, record the amount in question and who is resolving it, rather than treating it as approved for payment. Reconcile payment confirmations to the bank statement so an authorized payment, a scheduled payment and a cleared payment remain distinguishable.</p>'+m[3]
t,count=re.subn(pattern,expand,t,count=1,flags=re.S)
assert count==1
p.write_text(t,encoding='utf-8')

# No historical date is present in the source or original article snapshots.
# Explicitly flag missing dates instead of manufacturing publication events.
posts=['catch-up-bookkeeping-overdue-books.html','profit-vs-cash-flow-business-money.html','tax-ready-bookkeeping-records.html']
date='<p class="publication-date missing">Publication date unavailable</p>'
for name in posts:
 p=root/name;t=p.read_text(encoding='utf-8')
 start=t.index('<main');at=t.index('</h1>',start)+5
 t=t[:at]+date+t[at:];p.write_text(t,encoding='utf-8')
p=root/'blog.html';t=p.read_text(encoding='utf-8')
t=re.sub(r'(<h2 data-i18n="blogTitle\d">.*?</h2>)',r'\1'+date,t)
p.write_text(t,encoding='utf-8')

# Remove the obsolete public placeholder. Only real local destinations are linked.
p=root/'nationwide-bookkeeping.html';t=p.read_text(encoding='utf-8')
t=re.sub(r'<p class="state-review-status">.*?</p>','',t,flags=re.S)
t=re.sub(r'<li><img([^>]+)><span>([^<]+)</span></li>',r'<li><div class="state-entry"><img\1><span class="state-name">\2</span></div></li>',t)
p.write_text(t,encoding='utf-8')

for p in root.glob('*.html'):
 t=p.read_text(encoding='utf-8')
 t=t.replace('assets/design.css?v=corrections-4','assets/design.css?v=visual-20261016').replace('assets/design.js?v=corrections-4','assets/design.js?v=visual-20261016')
 p.write_text(t,encoding='utf-8')
print('Targeted visual changes applied. Blog dates remain explicitly unverified.')
