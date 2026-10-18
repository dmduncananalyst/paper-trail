from pathlib import Path
p=Path('assets/design.js');s=p.read_text(encoding='utf-8')
a=s.index('const header=document.querySelector');b=s.index("const tabs=[",a)
old=s[a:b];Path('verification/mobile-refinements-20261016/menu-before.js').write_text(old,encoding='utf-8')
s=s[:a]+'''const header=document.querySelector('.pt-header'),families=[...document.querySelectorAll('.nav-family')],panels=new Map();
const mobileNav=()=>matchMedia('(max-width:650px)').matches;
function hideMenus(){families.forEach(g=>{g.querySelector(':scope>a').setAttribute('aria-expanded','false');panels.get(g).hidden=true});header.style.removeProperty('--mobile-menu-space');header.style.removeProperty('--mobile-menu-top')}
function positionMobileMenu(g){if(!mobileNav())return;header.style.removeProperty('--mobile-menu-space');const a=g.querySelector(':scope>a'),panel=panels.get(g);header.style.setProperty('--mobile-menu-top',(a.getBoundingClientRect().bottom-header.getBoundingClientRect().top)+'px');const extra=Math.max(0,panel.getBoundingClientRect().bottom-header.getBoundingClientRect().bottom+12);header.style.setProperty('--mobile-menu-space',extra+'px')}
function showMenu(g){hideMenus();panels.get(g).hidden=false;g.querySelector(':scope>a').setAttribute('aria-expanded','true');positionMobileMenu(g)}
families.forEach((g,i)=>{const a=g.querySelector(':scope>a'),panel=g.querySelector('.nav-panel');panel.id='service-strip-'+i;panel.hidden=true;header.append(panel);panels.set(g,panel);a.setAttribute('aria-controls',panel.id);g.addEventListener('mouseenter',()=>{if(!mobileNav())showMenu(g)});a.addEventListener('pointerdown',e=>{if(!mobileNav()&&e.pointerType==='touch')a.dataset.wasOpen=String(!panel.hidden)});a.addEventListener('click',e=>{if(mobileNav()){e.preventDefault();if(panel.hidden)showMenu(g);else hideMenus();return}if(matchMedia('(hover:none)').matches){if(a.dataset.wasOpen==='false'||a.getAttribute('aria-expanded')!=='true'){e.preventDefault();showMenu(g)}delete a.dataset.wasOpen}})});
header.addEventListener('focusin',e=>{if(mobileNav())return;const g=e.target.closest('.nav-family');if(g)showMenu(g);else if(!e.target.closest('.nav-panel'))hideMenus()});header.addEventListener('mouseleave',()=>{if(!mobileNav()&&!header.contains(document.activeElement))hideMenus()});header.addEventListener('focusout',e=>{if(!mobileNav()&&!header.contains(e.relatedTarget))hideMenus()});document.querySelectorAll('.pt-nav>a').forEach(a=>{a.addEventListener('mouseenter',()=>{if(!mobileNav())hideMenus()})});
document.addEventListener('keydown',e=>{if(e.key==='Escape'){const open=families.find(g=>g.querySelector(':scope>a').getAttribute('aria-expanded')==='true');if(open){open.querySelector(':scope>a').focus();hideMenus()}}});document.addEventListener('click',e=>{if(!header.contains(e.target))hideMenus()});
addEventListener('resize',()=>{const open=families.find(g=>g.querySelector(':scope>a').getAttribute('aria-expanded')==='true');if(open)positionMobileMenu(open)});
''' +s[b:]
# Keep translated service titles and their buttons from colliding, only on phones.
insert='''function fitMobileServices(){const label=document.querySelector('.home-services .section-label');if(!label)return;const h=label.querySelector('h2'),button=label.querySelector('.action');if(!h||!button)return;const range=document.createRange();range.selectNodeContents(h);const needed=range.getBoundingClientRect().width+button.getBoundingClientRect().width+24;label.classList.toggle('mobile-stacked',matchMedia('(max-width:650px)').matches&&needed>label.clientWidth)}
addEventListener('resize',fitMobileServices);document.addEventListener('preview-language',()=>requestAnimationFrame(fitMobileServices));document.fonts.ready.then(fitMobileServices);requestAnimationFrame(fitMobileServices);
'''
s=s.replace("const phoneDialog=document.createElement('dialog');",insert+"const phoneDialog=document.createElement('dialog');")
p.write_text(s,encoding='utf-8')
p=Path('assets/design.css');s=p.read_text(encoding='utf-8');s+='''
/* Mobile menu persistence, localized labels and support spacing. */
.mobile-support,.mobile-label{display:none}
@media(max-width:650px){
 .pt-preview .pt-header{padding-bottom:var(--mobile-menu-space,0px)}
 .pt-preview .pt-header>.nav-panel{position:absolute;inset:auto 18px auto 18px;inset-block-start:var(--mobile-menu-top,100%);margin:0;z-index:20;max-height:55dvh;overflow-y:auto;background:#fff;border:1px solid #ccc;padding:12px;box-shadow:0 8px 15px rgb(0 0 0 / .12)}
 .pt-blog .blog-story h2,.pt-blog .blog-story .blog-preview{text-align:center}
 .pt-about .about-services{padding-bottom:12px}.pt-about .scope-boundary{margin-bottom:12px}
 .pt-interior .conversation-section{padding-top:12px;padding-bottom:28px}
 .pt-home .home-conversation{padding-top:18px;padding-bottom:28px}
 .mobile-label{display:inline}.desktop-label{display:none}
 .pt-blog .mobile-support{display:block;text-align:center;padding:22px 0 30px}
 .pt-blog .mobile-support>p{font-size:16px;line-height:1.8;max-width:540px;margin:0 auto 20px}
 .page-language{row-gap:18px;padding-bottom:12px}
 .page-language .translation-notice{margin:0;line-height:1.7}
 .home-services .section-label.mobile-stacked{display:flex;flex-direction:column;align-items:center;gap:18px}
 .home-services .section-label.mobile-stacked>h2{position:static;transform:none;width:100%;text-align:center;margin:0}
 .home-services .section-label.mobile-stacked>.action{position:static;inset:auto;transform:none;align-self:center;margin:0;max-width:100%}
}
''';p.write_text(s,encoding='utf-8')
