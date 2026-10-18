(async()=>{
 const ui=window.PAPER_TRAIL_LOCALES, locale=document.documentElement.dataset.staticLocale||document.documentElement.lang;
 const d=window.PAPER_TRAIL_CHAT_LOCALES[locale]||{};
 const t=s=>d[s]||ui[locale]?.[Object.keys(ui.en).find(k=>ui.en[k]===s)]||s;
 const input=document.querySelector('.chat input'), send=document.querySelector('.send-message');
 const answer=v=>{input.value=v;send.click()};
 document.querySelector('[data-open-chat]').click();document.querySelector('.chat-reset').click();
 answer('California');
 let guard=0;
 while(!document.querySelector('.chat-question')?.textContent.startsWith(t('Here is what Paper Trail will receive:'))&&guard++<25){
  const option=document.querySelector('.chat-options button');
  if(option){option.click();continue}
  answer(input.type==='email'?'salesstartweb7@gmail.com':input.type==='tel'?'8189340444':guard===4?'Paper Trail verification':'TEST Owner');
 }
 const reachedReview=guard<25;
 document.querySelector('.chat-options button').click();
 const form=document.querySelector('.hubspot-capture-form');
 if(!form)throw Error('Capture form did not open');
 const labels=[...form.querySelectorAll('.capture-field>span')].map(x=>x.textContent);
 const labelsMatch=['First Name','Last Name','Email','Phone number','Company name','Message'].every((s,i)=>labels[i].replace(/ \*$/,'')===t(s));
 const required=[...form.querySelectorAll('[name]')].map(f=>({name:f.name,required:f.required}));
 const submit=form.querySelector('[type=submit]');
 const submitLabelMatches=submit.textContent===t('Submit');
 form.elements.firstname.value='TEST';form.elements.lastname.value='Verification';form.elements.company.value='Paper Trail test inquiry';
 const original='TEST ONLY, original visitor text: \u00bfC\u00f3mo est\u00e1n mis libros? \u0645\u0631\u062d\u0628\u0627 \u4f60\u597d';
 form.elements.message.value=original;
 form.elements.email.value='invalid';form.requestSubmit();
 const emailValidation=document.querySelector('.chat-status').textContent===t('Please enter a business email address.');
 form.elements.email.value='salesstartweb7@gmail.com';form.elements.phone.value='12';form.requestSubmit();
 const phoneValidation=document.querySelector('.chat-status').textContent===t('Please enter a ten digit phone number, including the area code.');
 form.elements.phone.value='8189340444';
 const realFetch=window.fetch;let payload=null,calls=0,fail=true;
 window.fetch=async(url,options)=>{if(String(url).includes('api.hsforms.com/submissions/')){calls++;payload=JSON.parse(options.body);return {ok:!fail,status:fail?503:200}}return realFetch(url,options)};
 form.requestSubmit();
 for(let i=0;i<100&&submit.disabled;i++)await new Promise(r=>setTimeout(r,30));
 const failedRetained=document.contains(form)&&!submit.disabled&&form.elements.message.value===original;
 const failureLocalized=document.querySelector('.chat-status').textContent===t('Your note was not accepted. Please check your contact details and try again.');
 form.dispatchEvent(new Event('input',{bubbles:true}));
 window.__formSnapshot={original,labels,required};
 const result={locale,reachedReview,labelsMatch,submitLabelMatches,emailValidation,phoneValidation,failedRetained,failureLocalized,originalPreserved:payload?.fields.find(f=>f.name==='message')?.value===original,portal:form.dataset.portalId,formId:form.dataset.formId,mockCalls:calls,realSubmission:false,formOverflow:form.scrollWidth>form.clientWidth+2};
 window.__finishForm=async()=>{fail=false;form.requestSubmit();for(let i=0;i<100&&document.contains(form);i++)await new Promise(r=>setTimeout(r,30));return {successLocalized:[...document.querySelectorAll('.bubble')].some(p=>p.textContent===t('Your note is with Paper Trail. We have your contact details and everything you shared, including your meeting preference.')),formRemoved:!document.contains(form),mockCalls:calls}};
 return result;
})()
