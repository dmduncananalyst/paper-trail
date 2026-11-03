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
