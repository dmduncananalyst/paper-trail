/* The complete menu is in the HTML. Never hide it during navigation. */
document.documentElement.dataset.navigationReady='true';

/* Direct Financial Analysis navigation uses saved Google labels and existing locales. */
(()=>{
  const labels={"en": "Financial Analysis", "es": "An\u00e1lisis financiero", "fa": "\u062a\u062d\u0644\u06cc\u0644 \u0645\u0627\u0644\u06cc", "hy": "\u0556\u056b\u0576\u0561\u0576\u057d\u0561\u056f\u0561\u0576 \u057e\u0565\u0580\u056c\u0578\u0582\u056e\u0578\u0582\u0569\u0575\u0578\u0582\u0576", "zh-CN": "\u8d22\u52a1\u5206\u6790", "ko": "\uc7ac\ubb34 \ubd84\uc11d", "tl": "Pagsusuri sa Pananalapi", "te": "\u0c06\u0c30\u0c4d\u0c25\u0c3f\u0c15 \u0c35\u0c3f\u0c36\u0c4d\u0c32\u0c47\u0c37\u0c23", "ru": "\u0424\u0438\u043d\u0430\u043d\u0441\u043e\u0432\u044b\u0439 \u0430\u043d\u0430\u043b\u0438\u0437", "ar": "\u0627\u0644\u062a\u062d\u0644\u064a\u0644 \u0627\u0644\u0645\u0627\u0644\u064a"};
  const requested=document.documentElement.dataset.staticLocale||'en';
  const locale=labels[requested]?requested:'en';
  const destination=new URL('../'+(locale==='en'?'':locale+'/')+'financial-analysis.html',document.currentScript.src).href;
  const insert=()=>{
    const nav=document.querySelector('.pt-nav');
    if(!nav||nav.querySelector('[data-financial-analysis-navigation]'))return;
    const link=document.createElement('a');
    link.href=destination;
    link.textContent=labels[locale];
    link.lang=locale;
    link.dataset.financialAnalysisNavigation='true';
    if(location.pathname.endsWith('/financial-analysis.html'))link.setAttribute('aria-current','page');
    const packages=[...nav.children].find(item=>item.matches('a')&&new URL(item.href).pathname.endsWith('/packages.html'));
    nav.insertBefore(link,packages||null);
  };
  insert();
  new MutationObserver(insert).observe(document.documentElement,{childList:true,subtree:true});
})();

/* Approved Weekly Bookkeeping entry using saved labels for existing languages. */
(()=>{const locale=document.documentElement.dataset.staticLocale||document.documentElement.lang||'en';const weeklyLabels={"en": "Weekly Bookkeeping", "es": "Contabilidad semanal", "fa": "\u062d\u0633\u0627\u0628\u062f\u0627\u0631\u06cc \u0647\u0641\u062a\u06af\u06cc", "hy": "\u0547\u0561\u0562\u0561\u0569\u0561\u056f\u0561\u0576 \u0570\u0561\u0577\u057e\u0561\u057a\u0561\u0570\u0578\u0582\u0569\u0575\u0578\u0582\u0576", "zh-CN": "\u6bcf\u5468\u8bb0\u8d26", "ko": "\uc8fc\uac04 \uc7a5\ubd80 \uc815\ub9ac", "tl": "Lingguhang Pagbabayad ng Aklat", "te": "\u0c35\u0c3e\u0c30\u0c2a\u0c41 \u0c2c\u0c41\u0c15\u0c4d\u200c\u0c15\u0c40\u0c2a\u0c3f\u0c02\u0c17\u0c4d", "ru": "\u0415\u0436\u0435\u043d\u0435\u0434\u0435\u043b\u044c\u043d\u043e\u0435 \u0432\u0435\u0434\u0435\u043d\u0438\u0435 \u0431\u0443\u0445\u0433\u0430\u043b\u0442\u0435\u0440\u0441\u043a\u043e\u0433\u043e \u0443\u0447\u0435\u0442\u0430", "ar": "\u0645\u0633\u0643 \u0627\u0644\u062f\u0641\u0627\u062a\u0631 \u0627\u0644\u0623\u0633\u0628\u0648\u0639\u064a"};if(!weeklyLabels[locale])return;const insert=()=>{const nav=document.querySelector('.pt-nav');if(!nav||nav.querySelector('[data-weekly-navigation]'))return;const repair=nav.querySelector('a[href$="paper-trail-services.html"]');if(!repair)return;const link=document.createElement('a');link.href=new URL('weekly-bookkeeping.html',nav.querySelector('a[href$="index.html"]').href).href;link.textContent=weeklyLabels[locale];link.dataset.weeklyNavigation='true';nav.insertBefore(link,repair.closest('.nav-family')||repair)};insert();new MutationObserver(insert).observe(document.documentElement,{childList:true,subtree:true});})();

/* Approved Payroll service navigation; saved translations only. */
(()=>{const labels={"es": "N\u00f3mina de sueldos", "fa": "\u062d\u0642\u0648\u0642 \u0648 \u062f\u0633\u062a\u0645\u0632\u062f", "hy": "\u0531\u0577\u056d\u0561\u057f\u0561\u057e\u0561\u0580\u0571", "zh-CN": "\u5de5\u8d44\u5355", "ko": "\uae09\uc5ec", "tl": "Sweldo", "te": "\u0c2a\u0c47\u0c30\u0c4b\u0c32\u0c4d", "ru": "\u0420\u0430\u0441\u0447\u0435\u0442 \u0437\u0430\u0440\u0430\u0431\u043e\u0442\u043d\u043e\u0439 \u043f\u043b\u0430\u0442\u044b", "ar": "\u0643\u0634\u0648\u0641 \u0627\u0644\u0645\u0631\u062a\u0628\u0627\u062a", "en": "Payroll"};const locale=document.documentElement.dataset.staticLocale||"en";const insert=()=>{const nav=document.querySelector(".pt-nav");if(!nav||nav.querySelector("[data-payroll-navigation]"))return;const anchor=nav.querySelector('a[href$="packages.html"]'),home=nav.querySelector('a[href$="index.html"]');if(!home)return;const link=document.createElement("a");link.href=new URL("payroll.html",home.href).href;link.textContent=labels[locale]||labels.en;link.dataset.payrollNavigation="true";nav.insertBefore(link,anchor||null)};insert();new MutationObserver(insert).observe(document.documentElement,{childList:true,subtree:true})})();

/* Balance only the existing navigation row distribution; keep labels and design. */
(()=>{
 let queued=false,lastNav,lastKey='';
 function balance(){
  queued=false;const nav=document.querySelector('.pt-header .pt-nav');if(!nav)return;
  const items=[...nav.children].filter(e=>!e.hasAttribute('data-nav-row-break'));
  if(items.length<2)return;
  // A percent height on wrapped flex links stretches each row beyond the header.
  nav.querySelectorAll(':scope>a,:scope>.nav-family>a').forEach(a=>a.style.height='auto');
  const style=getComputedStyle(nav),gap=parseFloat(style.columnGap)||0;
  const width=nav.clientWidth-parseFloat(style.paddingLeft)-parseFloat(style.paddingRight);
  if(width<=0)return;
  const key=[width,style.font,style.columnGap,items.map(e=>e.textContent).join('|')].join('~');
  if(nav===lastNav&&key===lastKey)return;lastNav=nav;lastKey=key;
  nav.querySelectorAll('[data-nav-row-break]').forEach(e=>e.remove());
  nav.style.removeProperty('row-gap');
  items.forEach(e=>{e.style.removeProperty('margin-block-start');e.style.removeProperty('max-width')});
  const rowGap=parseFloat(getComputedStyle(nav).rowGap)||0;
  let widths=items.map(e=>e.getBoundingClientRect().width);
  function partition(){
   const n=items.length,total=widths.reduce((a,b)=>a+b,0);
   for(let count=1;count<=Math.floor(n/2);count++){
    const target=(total+gap*(n-count))/count,memo=new Map();
    function solve(start,rows){
     if(!rows)return start===n?{cost:0,ends:[]}:null;
     const key=start+':'+rows;if(memo.has(key))return memo.get(key);
     let best=null,used=0;
     for(let end=start;end<n;end++){
      used+=widths[end]+(end>start?gap:0);if(used>width+.5)break;
      if(end-start+1<2||n-end-1<(rows-1)*2)continue;
      const rest=solve(end+1,rows-1);if(!rest)continue;
      const cost=(used-target)**2+rest.cost;
      if(!best||cost<best.cost)best={cost,ends:[end+1,...rest.ends]};
     }
     memo.set(key,best);return best;
    }
    const result=solve(0,count);if(result)return result.ends;
   }
   return null;
  }
  let ends=partition();
  if(!ends){
   // At narrow widths, wrap long labels within the existing font and gaps.
   const cap=Math.max(1,(width-2*gap)/3);
   items.forEach(e=>e.style.maxWidth=cap+'px');widths=items.map(e=>e.getBoundingClientRect().width);ends=partition();
  }
  if(!ends){items.forEach(e=>e.style.removeProperty('max-width'));return}
  if(ends.length===1)return;
  // A zero-height flex break adds no spacing. Existing row gap is applied once
  // to the following row, avoiding the doubled gap of a separate flex line.
  nav.style.rowGap='0px';let start=0;
  ends.forEach((end,row)=>{
   if(row){const br=document.createElement('span');br.dataset.navRowBreak='true';br.setAttribute('aria-hidden','true');br.style.cssText='flex:0 0 100%;height:0;padding:0;margin:0;pointer-events:none';nav.insertBefore(br,items[start]);}
   for(let i=start;i<end;i++)if(row)items[i].style.marginBlockStart=rowGap+'px';
   start=end;
  });
 }
 function schedule(){if(!queued){queued=true;requestAnimationFrame(balance)}}
 new MutationObserver(schedule).observe(document.documentElement,{childList:true,subtree:true,characterData:true});
 addEventListener('resize',schedule);addEventListener('DOMContentLoaded',schedule);
 document.fonts?.ready.then(()=>{lastKey='';schedule()});schedule();
})();

/* Approved Packages destinations and direct Bundle & Save link, using saved translations. */
(()=>{const labels={"en": {"All Packages": "All Packages", "Weekly Bookkeeping": "Weekly Bookkeeping", "Monthly Bookkeeping": "Monthly Bookkeeping", "Accounts & Billing": "Accounts & Billing", "Bookkeeping Repair": "Bookkeeping Repair", "Financial Analysis": "Financial Analysis", "Payroll": "Payroll", "Bundle & Save": "Bundle & Save"}, "es": {"All Packages": "Todos los paquetes", "Weekly Bookkeeping": "Contabilidad semanal", "Monthly Bookkeeping": "Contabilidad mensual", "Accounts & Billing": "Cuentas y facturaci\u00f3n", "Bookkeeping Repair": "Reparaci\u00f3n de contabilidad", "Financial Analysis": "An\u00e1lisis financiero", "Payroll": "N\u00f3mina de sueldos", "Bundle & Save": "Paquete y ahorra"}, "fa": {"All Packages": "\u0647\u0645\u0647 \u0628\u0633\u062a\u0647\u200c\u0647\u0627", "Weekly Bookkeeping": "\u062d\u0633\u0627\u0628\u062f\u0627\u0631\u06cc \u0647\u0641\u062a\u06af\u06cc", "Monthly Bookkeeping": "\u062d\u0633\u0627\u0628\u062f\u0627\u0631\u06cc \u0645\u0627\u0647\u0627\u0646\u0647", "Accounts & Billing": "\u062d\u0633\u0627\u0628\u200c\u0647\u0627 \u0648 \u0635\u0648\u0631\u062a\u062d\u0633\u0627\u0628", "Bookkeeping Repair": "\u062a\u0639\u0645\u06cc\u0631 \u062d\u0633\u0627\u0628\u062f\u0627\u0631\u06cc", "Financial Analysis": "\u062a\u062d\u0644\u06cc\u0644 \u0645\u0627\u0644\u06cc", "Payroll": "\u062d\u0642\u0648\u0642 \u0648 \u062f\u0633\u062a\u0645\u0632\u062f", "Bundle & Save": "\u0628\u0633\u062a\u0647\u200c\u0628\u0646\u062f\u06cc \u0648 \u0630\u062e\u06cc\u0631\u0647"}, "hy": {"All Packages": "\u0532\u0578\u056c\u0578\u0580 \u0583\u0561\u0569\u0565\u0569\u0576\u0565\u0580\u0568", "Weekly Bookkeeping": "\u0547\u0561\u0562\u0561\u0569\u0561\u056f\u0561\u0576 \u0570\u0561\u0577\u057e\u0561\u057a\u0561\u0570\u0578\u0582\u0569\u0575\u0578\u0582\u0576", "Monthly Bookkeeping": "\u0531\u0574\u057d\u0561\u056f\u0561\u0576 \u0570\u0561\u0577\u057e\u0561\u057a\u0561\u0570\u0578\u0582\u0569\u0575\u0578\u0582\u0576", "Accounts & Billing": "\u0540\u0561\u0577\u056b\u057e\u0576\u0565\u0580 \u0587 \u057e\u0573\u0561\u0580\u0578\u0582\u0574\u0576\u0565\u0580", "Bookkeeping Repair": "\u0540\u0561\u0577\u057e\u0561\u057a\u0561\u0570\u0561\u056f\u0561\u0576 \u0570\u0561\u0577\u057e\u0561\u057c\u0574\u0561\u0576 \u057e\u0565\u0580\u0561\u0576\u0578\u0580\u0578\u0563\u0578\u0582\u0574", "Financial Analysis": "\u0556\u056b\u0576\u0561\u0576\u057d\u0561\u056f\u0561\u0576 \u057e\u0565\u0580\u056c\u0578\u0582\u056e\u0578\u0582\u0569\u0575\u0578\u0582\u0576", "Payroll": "\u0531\u0577\u056d\u0561\u057f\u0561\u057e\u0561\u0580\u0571", "Bundle & Save": "\u0553\u0561\u0569\u0565\u0569\u0561\u057e\u0578\u0580\u0565\u056c \u0587 \u056d\u0576\u0561\u0575\u0565\u056c"}, "zh-CN": {"All Packages": "\u6240\u6709\u5957\u9910", "Weekly Bookkeeping": "\u6bcf\u5468\u8bb0\u8d26", "Monthly Bookkeeping": "\u6bcf\u6708\u8bb0\u8d26", "Accounts & Billing": "\u8d26\u6237\u4e0e\u8d26\u5355", "Bookkeeping Repair": "\u7c3f\u8bb0\u4fee\u590d", "Financial Analysis": "\u8d22\u52a1\u5206\u6790", "Payroll": "\u5de5\u8d44\u5355", "Bundle & Save": "\u6346\u7ed1\u8d2d\u4e70\u66f4\u4f18\u60e0"}, "ko": {"All Packages": "\ubaa8\ub4e0 \ud328\ud0a4\uc9c0", "Weekly Bookkeeping": "\uc8fc\uac04 \uc7a5\ubd80 \uc815\ub9ac", "Monthly Bookkeeping": "\uc6d4\ubcc4 \uc7a5\ubd80 \uc815\ub9ac", "Accounts & Billing": "\uacc4\uc815 \ubc0f \uccad\uad6c", "Bookkeeping Repair": "\ud68c\uacc4 \uc218\ub9ac", "Financial Analysis": "\uc7ac\ubb34 \ubd84\uc11d", "Payroll": "\uae09\uc5ec", "Bundle & Save": "\ubb36\uc74c \uc0c1\ud488 \ud560\uc778"}, "tl": {"All Packages": "Lahat ng Pakete", "Weekly Bookkeeping": "Lingguhang Pagbabayad ng Aklat", "Monthly Bookkeeping": "Buwanang Pagbabayad ng Aklat", "Accounts & Billing": "Mga Account at Pagsingil", "Bookkeeping Repair": "Pagkukumpuni ng Bookkeeping", "Financial Analysis": "Pagsusuri sa Pananalapi", "Payroll": "Sweldo", "Bundle & Save": "Mag-bundle at Magtipid"}, "te": {"All Packages": "\u0c05\u0c28\u0c4d\u0c28\u0c3f \u0c2a\u0c4d\u0c2f\u0c3e\u0c15\u0c47\u0c1c\u0c40\u0c32\u0c41", "Weekly Bookkeeping": "\u0c35\u0c3e\u0c30\u0c2a\u0c41 \u0c2c\u0c41\u0c15\u0c4d\u200c\u0c15\u0c40\u0c2a\u0c3f\u0c02\u0c17\u0c4d", "Monthly Bookkeeping": "\u0c28\u0c46\u0c32\u0c35\u0c3e\u0c30\u0c40 \u0c2c\u0c41\u0c15\u0c4d\u200c\u0c15\u0c40\u0c2a\u0c3f\u0c02\u0c17\u0c4d", "Accounts & Billing": "\u0c16\u0c3e\u0c24\u0c3e\u0c32\u0c41 & \u0c2c\u0c3f\u0c32\u0c4d\u0c32\u0c3f\u0c02\u0c17\u0c4d", "Bookkeeping Repair": "\u0c2c\u0c41\u0c15\u0c4d\u0c15\u0c40\u0c2a\u0c3f\u0c02\u0c17\u0c4d \u0c30\u0c3f\u0c2a\u0c47\u0c30\u0c4d", "Financial Analysis": "\u0c06\u0c30\u0c4d\u0c25\u0c3f\u0c15 \u0c35\u0c3f\u0c36\u0c4d\u0c32\u0c47\u0c37\u0c23", "Payroll": "\u0c2a\u0c47\u0c30\u0c4b\u0c32\u0c4d", "Bundle & Save": "\u0c2c\u0c02\u0c21\u0c3f\u0c32\u0c4d \u0c1a\u0c47\u0c38\u0c3f \u0c06\u0c26\u0c3e \u0c1a\u0c47\u0c38\u0c41\u0c15\u0c4b\u0c02\u0c21\u0c3f"}, "ru": {"All Packages": "\u0412\u0441\u0435 \u043f\u0430\u043a\u0435\u0442\u044b", "Weekly Bookkeeping": "\u0415\u0436\u0435\u043d\u0435\u0434\u0435\u043b\u044c\u043d\u043e\u0435 \u0432\u0435\u0434\u0435\u043d\u0438\u0435 \u0431\u0443\u0445\u0433\u0430\u043b\u0442\u0435\u0440\u0441\u043a\u043e\u0433\u043e \u0443\u0447\u0435\u0442\u0430", "Monthly Bookkeeping": "\u0415\u0436\u0435\u043c\u0435\u0441\u044f\u0447\u043d\u043e\u0435 \u0432\u0435\u0434\u0435\u043d\u0438\u0435 \u0431\u0443\u0445\u0433\u0430\u043b\u0442\u0435\u0440\u0441\u043a\u043e\u0433\u043e \u0443\u0447\u0435\u0442\u0430", "Accounts & Billing": "\u0421\u0447\u0435\u0442\u0430 \u0438 \u0432\u044b\u0441\u0442\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u0441\u0447\u0435\u0442\u043e\u0432", "Bookkeeping Repair": "\u0420\u0435\u043c\u043e\u043d\u0442 \u0431\u0443\u0445\u0433\u0430\u043b\u0442\u0435\u0440\u0441\u043a\u0438\u0445 \u043a\u043d\u0438\u0433", "Financial Analysis": "\u0424\u0438\u043d\u0430\u043d\u0441\u043e\u0432\u044b\u0439 \u0430\u043d\u0430\u043b\u0438\u0437", "Payroll": "\u0420\u0430\u0441\u0447\u0435\u0442 \u0437\u0430\u0440\u0430\u0431\u043e\u0442\u043d\u043e\u0439 \u043f\u043b\u0430\u0442\u044b", "Bundle & Save": "\u041a\u043e\u043c\u043f\u043b\u0435\u043a\u0442 \u0438 \u0441\u043a\u0438\u0434\u043a\u0430"}, "ar": {"All Packages": "\u062c\u0645\u064a\u0639 \u0627\u0644\u0628\u0627\u0642\u0627\u062a", "Weekly Bookkeeping": "\u0645\u0633\u0643 \u0627\u0644\u062f\u0641\u0627\u062a\u0631 \u0627\u0644\u0623\u0633\u0628\u0648\u0639\u064a", "Monthly Bookkeeping": "\u0645\u0633\u0643 \u0627\u0644\u062f\u0641\u0627\u062a\u0631 \u0627\u0644\u0634\u0647\u0631\u064a\u0629", "Accounts & Billing": "\u0627\u0644\u062d\u0633\u0627\u0628\u0627\u062a \u0648\u0627\u0644\u0641\u0648\u0627\u062a\u064a\u0631", "Bookkeeping Repair": "\u0625\u0635\u0644\u0627\u062d \u0645\u0633\u0643 \u0627\u0644\u062f\u0641\u0627\u062a\u0631", "Financial Analysis": "\u0627\u0644\u062a\u062d\u0644\u064a\u0644 \u0627\u0644\u0645\u0627\u0644\u064a", "Payroll": "\u0643\u0634\u0648\u0641 \u0627\u0644\u0645\u0631\u062a\u0628\u0627\u062a", "Bundle & Save": "\u0627\u0634\u062a\u0631\u0650 \u0645\u062c\u0645\u0648\u0639\u0629 \u0648\u0648\u0641\u0631"}};const locale=document.documentElement.dataset.staticLocale||document.documentElement.lang||'en';const words=labels[locale];if(!words)return;
const insert=()=>{const nav=document.querySelector('.pt-nav');if(!nav)return;const home=nav.querySelector('a[href$="index.html"]');if(!home)return;
const packages=[...nav.children].find(e=>e.matches('a')&&new URL(e.href).pathname.endsWith('/packages.html'));
if(packages){const family=document.createElement('div');family.className='nav-family';family.dataset.packagesNavigation='true';packages.replaceWith(family);family.append(packages);packages.setAttribute('aria-haspopup','true');packages.setAttribute('aria-expanded','false');const panel=document.createElement('div');panel.className='nav-panel';panel.hidden=true;
[['All Packages','packages.html'],['Weekly Bookkeeping','weekly-bookkeeping.html'],['Monthly Bookkeeping','paper-trail-monthly-bookkeeping.html'],['Accounts & Billing','accounts-billing.html'],['Bookkeeping Repair','paper-trail-services.html'],['Financial Analysis','financial-analysis.html'],['Payroll','payroll.html']].forEach(([label,path])=>{const a=document.createElement('a');a.textContent=words[label];a.href=new URL(path,home.href).href;panel.append(a)});family.append(panel)}
if(!nav.querySelector('[data-bundle-navigation]')){const a=document.createElement('a');a.dataset.bundleNavigation='true';a.href=new URL('all-bundles.html',home.href).href;a.textContent=words['Bundle & Save'];const p=nav.querySelector('[data-packages-navigation]');nav.insertBefore(a,p?.nextSibling||null)}
};insert();new MutationObserver(insert).observe(document.documentElement,{childList:true,subtree:true});})();
