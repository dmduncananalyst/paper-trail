(()=>{
const box=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height}}, shown=e=>e.getClientRects().length&&getComputedStyle(e).visibility!=='hidden';
const w=document.documentElement.clientWidth;
return {url:location.pathname,lang:document.documentElement.lang,dir:document.documentElement.dir,h1:document.querySelector('h1')?.innerText,uiReady:!!window.paperTrailUI,
width:innerWidth,clientWidth:w,scrollWidth:document.documentElement.scrollWidth,
selectorCount:document.querySelectorAll('#language').length,selectorInHeader:!!document.querySelector('.pt-header #language'),selectorInMenu:!!document.querySelector('.pt-nav #language'),
relocatedMenuPanels:document.querySelectorAll('.pt-header>.nav-panel').length,menuItems:[...document.querySelectorAll('.pt-nav>a,.nav-family>a')].map(e=>e.textContent.trim()),
notice:(()=>{const e=document.querySelector('.translation-notice');if(!e)return null;return {shown:!!shown(e),text:e.textContent,lines:Math.round(e.getBoundingClientRect().height/parseFloat(getComputedStyle(e).lineHeight)),fontSize:getComputedStyle(e).fontSize}})(),
headerGeometry:box(document.querySelector('.pt-header')),navGeometry:box(document.querySelector('.pt-nav')),controlGeometry:document.querySelector('#language')?box(document.querySelector('#language')):null,languageGeometry:document.querySelector('.page-language')?box(document.querySelector('.page-language')):null,
notesIcons:[...document.querySelectorAll('.home-note-copy .note-emblem')].map(e=>({icon:box(e),copy:box(e.parentElement)})),heroActions:[...document.querySelectorAll('.opening-copy>.action,.hero-copy>.action,.about-content>div>.action')].map(e=>({label:e.textContent.trim(),button:box(e),container:box(e.parentElement)})),
overflow:[...document.querySelectorAll('main *,header *,footer *,.page-language *')].filter(e=>shown(e)&&!e.closest('svg')&&!(e.tagName==='VIDEO'&&getComputedStyle(e.parentElement).overflow==='hidden')&&e.getBoundingClientRect().width>0&&(e.getBoundingClientRect().right>w+2||e.getBoundingClientRect().left< -2)).slice(0,10).map(e=>({tag:e.tagName,class:e.className,text:e.textContent.slice(0,50)})),
videos:[...document.querySelectorAll('video')].map(v=>({src:v.querySelector('source')?.getAttribute('src')||v.getAttribute('src'),rect:box(v),frame:box(v.parentElement),fit:getComputedStyle(v).objectFit,sourceWidth:v.videoWidth,sourceHeight:v.videoHeight,paused:v.paused,ready:v.readyState})),
cards:[...document.querySelectorAll('.work-card')].map(c=>({heading:c.querySelector('h2,h3')?.textContent,rect:box(c),textRect:box(c.lastElementChild)})),
notes:[...document.querySelectorAll('.support-note-cards .photo-card')].map(c=>({rect:box(c),photo:box(c.querySelector('img')),copy:box(c.querySelector('.photo-card-copy')),title:c.querySelector('h3')?.textContent,action:c.querySelector('.card-action')?.textContent})),
flags:document.querySelectorAll('.state-mosaic li').length,flagLinks:document.querySelectorAll('.state-mosaic a').length,
missingImages:[...document.images].filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.getAttribute('src')),
localeGaps:window.paperTrailUI?.localeGaps(),dialogOpen:!!document.querySelector('dialog[open]')};
})()
