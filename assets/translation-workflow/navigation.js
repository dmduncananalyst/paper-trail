/* Saved static translations only. No Google calls, credentials, or metering. */
(() => {
  'use strict';
  const routes=window.paperTrailTranslationRoutes||{};
  const root=new URL('.',document.baseURI),current=new URL(location.href);
  let path=decodeURI(current.pathname.slice(root.pathname.length))||'index.html';
  const staticLocale=document.documentElement.dataset.staticLocale;
  if(staticLocale&&path.startsWith(staticLocale+'/'))path=path.slice(staticLocale.length+1);
  let stored='en';try{stored=localStorage.getItem('paper-trail-language')||'en'}catch{}
  const requested=staticLocale||current.searchParams.get('lang')||stored;
  const language=requested==='en'||routes[requested]?.includes(path)?requested:'en';
  const destination=(locale,page)=>new URL((locale==='en'?'':locale+'/')+page,root);
  if(!staticLocale&&language!=='en'&&routes[language]?.includes(path)){
    const url=destination(language,path);url.hash=current.hash;url.search=current.search;url.searchParams.delete('lang');location.replace(url);return;
  }
  try{localStorage.setItem('paper-trail-language',language)}catch{}
  document.addEventListener('change',event=>{
    const select=event.target;if(select.id!=='language')return;
    const next=select.value;if(next!=='en'&&!routes[next]?.includes(path))return;
    event.stopImmediatePropagation();try{localStorage.setItem('paper-trail-language',next)}catch{}
    const url=destination(next,path);url.hash=current.hash;url.search=current.search;url.searchParams.delete('lang');location.assign(url);
  },true);
  document.addEventListener('click',event=>{
    if(event.defaultPrevented||event.button||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;
    const a=event.target.closest('a[href]');if(!a||a.target==='_blank'||a.hasAttribute('download'))return;
    if(a.parentElement?.classList.contains('nav-family')&&matchMedia('(max-width:650px)').matches)return;
    const url=new URL(a.href);if(url.protocol!==root.protocol||url.host!==root.host||!url.pathname.startsWith(root.pathname))return;
    const page=decodeURI(url.pathname.slice(root.pathname.length))||'index.html';
    if(Object.keys(routes).some(l=>page.startsWith(l+'/')))return;
    if(language!=='en'&&routes[language]?.includes(page)){
      event.preventDefault();const target=destination(language,page);target.hash=url.hash;target.search=url.search;location.assign(target);
    }
  },true);
})();
