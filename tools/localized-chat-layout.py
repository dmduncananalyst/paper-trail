from pathlib import Path

if 'id="conversation-dialog"' in Path('blog.html').read_text(encoding='utf-8'):raise SystemExit('Already applied. Preserve the saved files and use the locale bundle builder for future translation edits.')
import re,json
out=Path('verification/localized-chat-20261016');out.mkdir(exist_ok=True)
for n in ['assets/site.js','assets/design.js','assets/design.css','index.html','blog.html','notes.html']:(out/(Path(n).name+'.before.txt')).write_text(Path(n).read_text(encoding='utf-8'),encoding='utf-8')
# Reuse the existing approved chat, question sequence and delivery configuration on Blog.
home=Path('index.html').read_text(encoding='utf-8');dialog=re.search(r'<dialog id="conversation-dialog".*?</dialog>',home,re.S)[0];m=re.search(r'<script type="application/json" id="conversation-data">(.*?)</script>',home,re.S);config=json.loads(m[1]);config['page']='blog.html';config['topic']='Business bookkeeping'
p=Path('blog.html');s=p.read_text(encoding='utf-8');s=s.replace('<a class="action" href="areas-we-serve.html" data-i18n="mobileSupport">Get Bookkeeping Support</a>','<button class="action" type="button" data-open-chat aria-haspopup="dialog" aria-controls="conversation-dialog" data-i18n="mobileSupport">Get Bookkeeping Support</button>');s=s.replace('</main>',dialog+'<script type="application/json" id="conversation-data">'+json.dumps(config,ensure_ascii=False)+'</script></main>');p.write_text(s,encoding='utf-8')
p=Path('notes.html');s=p.read_text(encoding='utf-8');s,n=re.subn(r'<div class="notes-blog-button">.*?</div>','',s,count=1);assert n==1;p.write_text(s,encoding='utf-8')
p=Path('assets/design.css');s=p.read_text(encoding='utf-8');s+='''
/* Home Notes heading and universal service Notes card composition, phone only. */
@media(max-width:650px){
 .pt-home .home-notes>.section-label{display:flex;flex-direction:column;align-items:center;gap:18px}
 .pt-home .home-notes>.section-label>h2{position:static;transform:none;width:100%;margin:0;text-align:center}
 .pt-home .home-notes>.section-label>.action{position:static;inset:auto;transform:none;align-self:center;max-width:100%;margin:0}
 .pt-interior .service-notes .support-note-cards .photo-card{display:grid;grid-template-columns:43% minmax(0,1fr);gap:0;padding:0;align-items:stretch;border:1px solid #ccc;min-height:180px}
 .pt-interior .service-notes .support-note-cards .photo-card-copy{padding:20px 14px;gap:23px;align-items:center;justify-content:center;text-align:center}
 .pt-interior .service-notes .support-note-cards h3{font-size:23px;line-height:1.3;font-weight:500;margin:0}
 .pt-notes .topic-index{padding-bottom:8px}.pt-notes .page-conversation{padding-top:24px;padding-bottom:28px}
 .pt-blog .mobile-support{padding-bottom:28px}
}
.chat[dir=rtl] .chat-log,.chat[dir=rtl] .chat-status{text-align:right}
.chat[dir=rtl] .chat-compose input:not([type=email]):not([type=tel]){direction:rtl;text-align:right}
''';p.write_text(s,encoding='utf-8')
# Both page-local selectors share the same localized guided chat.
p=Path('assets/design.js');s=p.read_text(encoding='utf-8');s=s.replace("const note=document.createElement('p');note.className='chat-language-note';note.dataset.i18n='chatNotice';chat.querySelector('.chat-header').after(note)","const note=document.createElement('p');note.className='chat-language-note';note.dataset.i18n='chatNotice';chat.querySelector('.chat-header').after(note)");p.write_text(s,encoding='utf-8')
services=[]
for p in Path('.').glob('*.html'):
 s=p.read_text(encoding='utf-8')
 if 'related-section service-notes' in s:services.append({'page':p.name,'cards':s.count('class="photo-card"')})
(out/'service-card-inventory.json').write_text(json.dumps(services,indent=2),encoding='utf-8')
print('Layout targets:',len(services),'service pages, Blog chat, Home Notes heading, Notes Blog link.')
