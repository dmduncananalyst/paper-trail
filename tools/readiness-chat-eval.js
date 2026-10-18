(async()=>{
 const locale=document.documentElement.dataset.staticLocale||document.documentElement.lang,d=window.PAPER_TRAIL_CHAT_LOCALES[locale];
 const t=s=>d[s]||s,answer=v=>{document.querySelector('.chat input').value=v;document.querySelector('.send-message').click()};
 document.querySelector('[data-open-chat]').click();document.querySelector('.chat-reset').click();
 const original='TEST ONLY \u00f1 \u0645\u0631\u062d\u0628\u0627 \u4f60\u597d';
 answer(original);let guard=0,questions=0;
 while(!document.querySelector('.chat-question')?.textContent.startsWith(t('Here is what Paper Trail will receive:'))&&guard++<25){
  if(document.querySelectorAll('.chat-question').length!==1)throw Error('Multiple active questions');questions++;
  const option=document.querySelector('.chat-options button');if(option){option.click();continue}
  const input=document.querySelector('.chat input');answer(input.type==='email'?'salesstartweb7@gmail.com':input.type==='tel'?'8189340444':'TEST Paper Trail verification');
 }
 const realFetch=window.fetch;let payload=null,calls=0,fail=true;
 window.fetch=async(url,options)=>{if(String(url).includes('api.hsforms.com/submissions/')){calls++;payload=JSON.parse(options.body);return {ok:!fail,status:fail?503:200}}return realFetch(url,options)};
 document.querySelector('.chat-options button').click();
 for(let i=0;i<100&&!document.querySelector('.chat-options button');i++)await new Promise(r=>setTimeout(r,30));
 const result={locale,reachedReview:guard<25,oneQuestionAtEachStep:true,questions,failureLocalized:document.querySelector('.chat-status').textContent===t('Your note was not accepted. Please check your contact details and try again.'),retryAvailable:document.querySelector('.chat-options button')?.textContent===t('Try sending again'),originalTextPreserved:payload?.fields.find(f=>f.name==='message')?.value.includes('State: '+original),emailMapped:payload?.fields.find(f=>f.name==='email')?.value==='salesstartweb7@gmail.com',noCustomReplacementForm:!document.querySelector('.hubspot-capture-form'),mockCalls:calls,realSubmission:false};
 fail=false;document.querySelector('.chat-options button').click();
 for(let i=0;i<100&&document.querySelector('.chat-status').textContent;i++)await new Promise(r=>setTimeout(r,30));
 result.successLocalized=[...document.querySelectorAll('.bubble')].some(p=>p.textContent===t('Your note is with Paper Trail. We have your contact details and everything you shared, including your meeting preference.'));
 result.mockCalls=calls;
 return result;
})()
