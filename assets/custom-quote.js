(() => {
  'use strict';
  document.querySelectorAll('[data-quote-select]').forEach(link=>link.addEventListener('click',()=>{
    try{sessionStorage.setItem('paper-trail-quote-service',link.dataset.quoteSelect)}catch{}
  }));
  const form=document.querySelector('#quote-questionnaire');
  if(!form)return;
  try{
    if(sessionStorage.getItem('paper-trail-quote-service')!==form.dataset.serviceKey){location.replace('request-a-custom-quote.html');return}
  }catch{location.replace('request-a-custom-quote.html');return}
  const config=window.PAPER_TRAIL_QUOTE_CONFIG;
  const localized=value=>window.PAPER_TRAIL_CHAT_LOCALES?.[document.documentElement.dataset.staticLocale||'en']?.[value]||value;
  let nativeForm;
  const feedback=document.createElement('p');
  feedback.id='quote-submission-feedback';
  feedback.setAttribute('role','alert');
  feedback.hidden=true;
  form.append(feedback);
  function showProblem(message){
    if(form.hidden)return;
    feedback.textContent=localized(message);
    feedback.hidden=false;
  }
  function matchesInstance(event){
    return nativeForm&&event.detail?.formId===config.formId&&
      event.detail.instanceId===nativeForm.getInstanceId();
  }
  function quoteDetails(){
    const lines=['Selected service: '+form.dataset.service];
    form.querySelectorAll('.quote-field[data-question]').forEach(field=>{
      const answers=[],details=[];
      field.querySelectorAll('input,select,textarea').forEach(input=>{
        if(input.disabled||input.type==='file')return;
        if(['checkbox','radio'].includes(input.type)&&!input.checked)return;
        const value=input.value.trim();
        if(!value)return;
        (input.name.endsWith('-extra')?details:answers).push(value);
      });
      if(!answers.length&&!details.length)return;
      lines.push('\n'+field.dataset.question);
      if(answers.length)lines.push('Answer: '+answers.join('; '));
      if(details.length)lines.push('Additional details: '+details.join('\n'));
    });
    return lines.join('\n');
  }
  function synchronize(){
    if(nativeForm)nativeForm.setFieldValue('0-1/'+config.quoteDetailsFieldName,quoteDetails());
  }
  // These listeners precede the deferred embed. Contact values, authorization,
  // file selection, validation and submission are owned entirely by HubSpot.
  addEventListener('hs-form-event:on-ready',event=>{
    if(event.detail?.formId!==config.formId)return;
    nativeForm=window.HubSpotFormsV4.getFormFromEvent(event);
    synchronize();
  });
  form.querySelector('.questionnaire-sections').addEventListener('input',synchronize);
  form.querySelector('.questionnaire-sections').addEventListener('change',synchronize);
  addEventListener('pageshow',synchronize);
  addEventListener('hs-form-event:on-submission:failed',event=>{
    if(!matchesInstance(event))return;
    showProblem('Your request could not be completed. Please review any highlighted errors in the form. Keep this page open so you can correct your information. If there are no highlighted errors, call Paper Trail at 818-934-0444 before submitting again.');
  });
  // Report a blocked native form/CAPTCHA dependency without weakening policy.
  document.addEventListener('securitypolicyviolation',event=>{
    if(event.disposition==='report')return;
    let blocked;
    try{blocked=new URL(event.blockedURI)}catch{return}
    if(/^(?:[a-z0-9-]+\.)*(?:hsforms\.net|hsforms\.com)$/.test(blocked.hostname)||
       (/^(?:(?:www|recaptcha)\.)?(?:google\.com|recaptcha\.net|gstatic\.com)$/.test(blocked.hostname)&&blocked.pathname.startsWith('/recaptcha/'))){
      showProblem('The quote form could not complete its security check. Your request has not been confirmed. Keep this page open and call Paper Trail at 818-934-0444 before submitting again.');
    }
  });
  addEventListener('error',event=>{
    if(event.target?.src===config.embedScript){
      showProblem('The quote form could not load. Please keep this page open and call Paper Trail at 818-934-0444 for help.');
    }
  },true);
  addEventListener('hs-form-event:on-submission:success',event=>{
    if(!matchesInstance(event))return;
    form.inert=true;
    form.hidden=true;
    const success=document.querySelector('#quote-success');
    success.hidden=false;
    success.focus({preventScroll:true});
    success.scrollIntoView({block:'center'});
  });
})();
