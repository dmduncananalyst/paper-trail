from pathlib import Path
import json
out=Path('verification/mobile-refinements-20261016');out.mkdir(exist_ok=True)
p=Path('assets/design.css');s=p.read_text(encoding='utf-8');(out/'design-before.css').write_text(s,encoding='utf-8')
s+='''
/* Owner requested mobile refinements. Desktop layout remains unchanged. */
@media(max-width:650px){
 .pt-preview .pt-nav{align-items:stretch;grid-auto-rows:minmax(52px,auto)}
 .pt-preview .pt-nav>a,.pt-preview .pt-nav .nav-family>a{display:flex;align-items:center;justify-content:center;height:100%;min-height:52px;padding:6px 0;text-align:center;line-height:1.4}
 .pt-preview .pt-nav .nav-family{display:flex;align-items:stretch;min-width:0}
 .pt-preview .pt-nav .nav-family>a{width:100%}
 .conversation-section>.wrap.conversation-invitation{display:flex;justify-content:center;width:100%;max-width:100%;margin-inline:auto;text-align:center}
 .page-conversation,.home-conversation,.all-service-notes,.reading-actions{display:flex;justify-content:center;align-items:center;flex-wrap:wrap;text-align:center}
 .pt-preview main>.action{display:flex;width:fit-content;max-width:100%;margin-inline:auto}
 .pt-contact .contact-main>h1{font-size:clamp(20px,6vw,26px)!important;white-space:nowrap;text-align:center;letter-spacing:-.035em}
 .pt-contact .contact-methods{align-items:center;text-align:center}
 .pt-contact .contact-methods>button,.pt-contact .contact-methods>a{margin-inline:auto;max-width:100%}
 .pt-topic .topic-stories .blog-story h2,.pt-topic .topic-main>h1,.pt-reading .reading-masthead h1,.pt-reading .reading-column h2{text-align:center}
 .pt-blog .publication-date,.pt-reading .publication-date{text-align:center}
 .pt-about .about-service-choices>a>img{height:100%;width:100%;align-self:stretch;object-fit:cover;object-position:center 30%}
 .pt-interior .service-notes .support-note-cards .photo-card{grid-template-columns:43% minmax(0,1fr);min-height:180px;align-items:stretch}
 .pt-interior .service-notes .support-note-cards .photo-card-copy{padding:16px 12px;gap:16px;justify-content:center;text-align:center}
 .pt-interior .service-notes .support-note-cards h3{font-size:18px;line-height:1.35;margin:0}
 .pt-interior .service-notes .support-note-cards .card-action{font-size:18px;min-height:44px;padding:8px 16px;margin:0}
 .pt-interior .service-notes .support-note-cards .photo-frame.card-photo{position:relative;height:100%;min-height:180px;align-self:stretch;overflow:hidden}
 .pt-interior .service-notes .support-note-cards .photo-frame.card-photo img{position:absolute;inset:0;display:block;width:100%!important;height:100%!important;object-fit:cover!important;object-position:center 35%}
 .pt-home .home-note[href="what-business-expenses-should-i-be-tracking.html"]>img{object-position:82% 15%}
}
'''
p.write_text(s,encoding='utf-8')
changed=[]
for p in list(Path('.').glob('*.html'))+list(Path('state-records').glob('*.html')):
 s=p.read_text(encoding='utf-8');t=s.replace('Nationwide, based out of Los Angeles.','Nationwide-Based Out Of Los Angeles')
 if s!=t:p.write_text(t,encoding='utf-8');changed.append(p.as_posix())
p=Path('assets/locales/home-blog/en.json');d=json.loads(p.read_text(encoding='utf-8'));d['location']='Nationwide-Based Out Of Los Angeles';p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
locales={p.stem:json.loads(p.read_text(encoding='utf-8')) for p in Path('assets/locales/home-blog').glob('*.json') if p.stem!='manifest'}
Path('assets/locales/home-blog/current.js').write_text('/* Saved authored Home and Blog drafts. No provider calls. */\nwindow.PAPER_TRAIL_LOCALES='+json.dumps(locales,ensure_ascii=False)+';\n',encoding='utf-8')
(out/'changes.json').write_text(json.dumps({'shared_wording_only':changed,'mobile_styles_only':'All new CSS rules are inside max-width:650px. No Notes page styles changed. Home Notes changes limited to one photo object-position.','wording':'Nationwide-Based Out Of Los Angeles'},indent=2),encoding='utf-8')
print('Applied mobile CSS and exact shared location wording.')
