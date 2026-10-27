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
  // Native segmented month inputs are difficult to type into on some browsers.
  // Keep their canonical YYYY-MM values for the existing Quote Details mapping;
  // expose ordinary keyboard-accessible selects with the existing translated labels.
  const periods=[...form.querySelectorAll('.period-fields input[type="month"]')].map(input=>{
    const label=input.parentElement;
    const group=document.createElement('div');
    group.className='period-date';
    group.setAttribute('role','group');
    const title=document.createElement('span');
    title.id=input.name+'-label';
    title.textContent=label.textContent.trim();
    group.setAttribute('aria-labelledby',title.id);
    const controls=document.createElement('div');
    controls.className='period-date-controls';
    const month=document.createElement('select'),year=document.createElement('select');
    month.id=input.id||input.name+'-month';
    year.id=input.name+'-year';
    input.removeAttribute('id');
    [month,year].forEach((select,index)=>{
      select.dataset.periodPart=index===0?'month':'year';
      select.setAttribute('aria-label',title.textContent+(index===0?' (MM)':' (YYYY)'));
      select.required=input.required;
      select.disabled=input.disabled;
      select.add(new Option('—',''));
    });
    const locale=document.documentElement.dataset.staticLocale||document.documentElement.lang||'en';
    const formatter=new Intl.DateTimeFormat(locale,{month:'long',timeZone:'UTC',calendar:'gregory'});
    for(let m=1;m<=12;m++)month.add(new Option(formatter.format(new Date(Date.UTC(2000,m-1,1))),String(m).padStart(2,'0')));
    // Put recent repair years first on mobile, retaining all four-digit years.
    // Native selects also support typing a year to jump directly to it.
    const currentYear=new Date().getFullYear();
    for(let offset=0;offset<9999;offset++){
      const y=(currentYear-offset+9998)%9999+1;
      year.add(new Option(String(y).padStart(4,'0'),String(y).padStart(4,'0')));
    }
    const initial=input.value;
    input.type='hidden';
    if(initial){year.value=initial.slice(0,4);month.value=initial.slice(5,7)}
    controls.append(month,year);
    group.append(title,controls,input);
    label.replaceWith(group);
    return {input,month,year};
  });
  function updatePeriods(){
    periods.forEach(({input,month,year})=>{input.value=month.value&&year.value?year.value+'-'+month.value:''});
    periods.forEach(({input,month,year},index)=>{
      const other=periods[index===0?1:0]?.input.value;
      const min=input.min||(index===1?other:''),max=input.max||(index===0?other:'');
      const allowed=value=>(!min||value>=min)&&(!max||value<=max);
      [...month.options].forEach(option=>{
        option.disabled=!!option.value&&!!year.value&&!allowed(year.value+'-'+option.value);
      });
      [...year.options].forEach(option=>{
        if(!option.value)return;
        const first=option.value+'-'+(month.value||'01'),last=option.value+'-'+(month.value||'12');
        option.disabled=!!((min&&last<min)||(max&&first>max));
      });
    });
  }
  periods.forEach(({month,year})=>[month,year].forEach(select=>select.addEventListener('change',updatePeriods)));
  updatePeriods();
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
        if(input.disabled||input.type==='file'||input.hasAttribute('data-period-part'))return;
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
