window.PAPER_TRAIL_DIRECT_HUBSPOT=true;
(()=>{
 const nav=document.querySelector('.site-nav'),toggle=document.querySelector('.menu-toggle');
 toggle?.addEventListener('click',()=>{const open=toggle.getAttribute('aria-expanded')!=='true';toggle.setAttribute('aria-expanded',String(open));nav.classList.toggle('open',open)});
 document.querySelectorAll('.nav-group>button').forEach(b=>b.addEventListener('click',()=>{const g=b.parentElement,open=!g.classList.contains('open');document.querySelectorAll('.nav-group').forEach(x=>{x.classList.remove('open');x.querySelector('button')?.setAttribute('aria-expanded','false')});g.classList.toggle('open',open);b.setAttribute('aria-expanded',String(open))}));
 document.querySelectorAll('.nav-group').forEach(group=>{const button=group.querySelector(':scope>button');const dropdown=group.querySelector(':scope>.dropdown');const align=()=>dropdown?.style.setProperty('--dropdown-left',group.getBoundingClientRect().left+'px');group.addEventListener('focusin',align);group.addEventListener('mouseenter',align);group.addEventListener('mouseenter',()=>{if(matchMedia('(hover:hover) and (min-width:1181px)').matches)button?.setAttribute('aria-expanded','true')});group.addEventListener('mouseleave',()=>{if(matchMedia('(hover:hover) and (min-width:1181px)').matches){group.classList.remove('open');button?.setAttribute('aria-expanded','false')}})});
 document.querySelectorAll('.video-frame').forEach(frame=>{const video=frame.querySelector('video'),control=frame.querySelector('.video-toggle');if(!video)return;if(matchMedia('(prefers-reduced-motion: reduce)').matches)video.pause();if(!control)return;const sync=()=>{control.textContent=video.paused?'Play':'Pause';control.setAttribute('aria-label',video.paused?'Play background video':'Pause background video')};video.addEventListener('play',sync);video.addEventListener('pause',sync);control.addEventListener('click',()=>{if(video.paused){video.play().catch(()=>sync())}else video.pause()});sync()});
 document.addEventListener('keydown',e=>{if(e.key==='Escape'){nav?.classList.remove('open');toggle?.setAttribute('aria-expanded','false');document.querySelectorAll('.nav-group.open').forEach(x=>{x.classList.remove('open');x.querySelector('button').setAttribute('aria-expanded','false')})}});
 document.addEventListener('click',e=>{if(!e.target.closest('.nav-group'))document.querySelectorAll('.nav-group.open').forEach(x=>{x.classList.remove('open');x.querySelector('button').setAttribute('aria-expanded','false')})});
 const filter=document.querySelector('[data-filter]');filter?.addEventListener('input',()=>{const term=filter.value.toLowerCase();let count=0;document.querySelectorAll('[data-searchable]').forEach(x=>{const show=x.textContent.toLowerCase().includes(term);x.classList.toggle('hidden',!show);if(show)count++});const empty=document.querySelector('.empty-results');empty?.classList.toggle('hidden',count>0)});
 const el=document.querySelector('.chat');if(!el)return;
 const config=JSON.parse(document.getElementById('conversation-data').textContent);
 const chatLanguage=()=>document.documentElement.dataset.staticLocale||(document.querySelector('#language')?document.documentElement.lang||'en':'en');
 function t(value){const language=chatLanguage(),dictionary=window.PAPER_TRAIL_CHAT_LOCALES?.[language];if(dictionary&&Object.hasOwn(dictionary,value))return dictionary[value];const ui=window.PAPER_TRAIL_LOCALES,key=Object.keys(ui?.en||{}).find(k=>ui.en[k]===value);return key&&ui?.[language]?.[key]||value}
 const log=el.querySelector('.chat-log'),options=el.querySelector('.chat-options'),input=el.querySelector('input'),send=el.querySelector('.send-message'),mode=el.querySelector('.chat-mode'),status=el.querySelector('.chat-status');
 const privatePattern=/\b\d{3}[ -]\d{2}[ -]\d{4}\b|\b(?:\d[ -]?){13,19}\b|\b(?:password|routing number|account number|social security|credit card number|bank login)\s*[:=]/i;
 let step=0,details={},originalAnswers={},busy=false,questionMode=false,sent=false;
 const storageKey='paper-trail-chat:'+config.page;
 function saveConversation(){
  try{sessionStorage.setItem(storageKey,JSON.stringify({version:1,step,details,originalAnswers,sent,questionMode,editing:el.dataset.editing==='true',draft:input.value,history:[...log.children].filter(p=>!p.classList.contains('chat-question')).map(p=>({text:p.textContent,user:p.classList.contains('user'),parts:[...p.childNodes].map(n=>({text:n.textContent,href:n.nodeType===1&&n.tagName==='A'?n.getAttribute('href'):null,target:n.nodeType===1?n.target:null}))}))}))}catch{}
 }
 function restoreConversation(){
  try{const saved=JSON.parse(sessionStorage.getItem(storageKey)||'null');if(!saved||saved.version!==1||!Number.isInteger(saved.step)||saved.step<0||saved.step>steps.length)return false;
   step=saved.step;details=saved.details||{};originalAnswers=saved.originalAnswers||{};sent=saved.sent===true;questionMode=false;if(saved.editing)el.dataset.editing='true';
   for(const entry of saved.history||[]){const p=document.createElement('p');p.className='bubble'+(entry.user?' user':'');for(const part of entry.parts||[{text:entry.text}]){let href;try{href=part.href&&new URL(part.href,document.baseURI)}catch{}if(href&&['http:','https:'].includes(href.protocol)){const a=document.createElement('a');a.href=part.href;a.textContent=part.text;if(part.target==='_blank'){a.target='_blank';a.rel='noopener'}p.append(a)}else p.append(document.createTextNode(part.text||''))}log.append(p)}
   if(sent){input.disabled=true;send.disabled=true;mode.hidden=true}else{show();input.value=saved.draft||''}return true;
  }catch{return false}
 }
 input.addEventListener('input',saveConversation);addEventListener('pagehide',saveConversation);
 const steps=[
  {key:'state',q:'What state are you located in?',placeholder:'For example, California'},
  {key:'issue',q:'What about your books needs attention?',choices:config.issueChoices||config.choices||['Overdue books','Account balances','Monthly records']},
  {key:'period',q:'Which period needs attention?',choices:config.intakePeriodChoices||['This month','A few months','A year or more','I am not sure']},
  ...(config.periodQuestion?[{key:'scope',q:config.periodQuestion,choices:config.periodChoices||[]}]:[]),
  {key:'software',q:'Where are your books kept at the moment?',choices:['QuickBooks','Xero','Spreadsheets','Another system','I am starting fresh']},
  {key:'businessType',q:'What does your business do?',placeholder:'For example, interior design or a retail shop'},
  {key:'business',q:'What is your company name?',placeholder:'Your company name'},
  {key:'timing',q:'When would you like this work to begin?',choices:['As soon as possible','Within a month','I am planning ahead']},
  {key:'meeting',q:'What kind of meeting would work best for you?',choices:['Zoom','In person in Los Angeles County, by appointment','Email me first']},
  {key:'availability',q:'What day would you prefer to meet?',choices:['Monday','Tuesday','Wednesday','Thursday','Friday','Arrange by email'],placeholder:'Your preferred day'},
  {key:'meetingTime',q:'What time usually works best for you?',choices:['Morning','Afternoon','Arrange by email'],placeholder:'Your preferred time'},
  {key:'timeZone',q:'What time zone are you in?',choices:['Pacific','Mountain','Central','Eastern'],placeholder:'Your time zone'},
  {key:'name',q:'What name should we use when we reply?',placeholder:'Your name'},
  {key:'email',q:'What email should Paper Trail use to follow up?',placeholder:'you@yourbusiness.com'},
  {key:'phone',q:'What phone number can we reach you on?',placeholder:'Your phone number'}
 ];
 function bubble(text,user=false){const p=document.createElement('p');p.className='bubble'+(user?' user':'');p.textContent=user?text:t(text);log.append(p);log.scrollTop=log.scrollHeight;requestAnimationFrame(()=>{log.scrollTop=log.scrollHeight});}
 function choices(items,action){options.replaceChildren();for(const label of items||[]){const b=document.createElement('button');b.type='button';b.textContent=t(label);b.addEventListener('click',()=>action(label));options.append(b)}}
 const displayAnswer=(key,value)=>steps.find(s=>s.key===key)?.choices?.includes(value)?t(value):value;
 const labels={state:'State',scope:'Additional service scope',meetingTime:'Meeting time',timeZone:'Time zone',issue:'What needs attention',period:'Scope or period',software:'Current system',businessType:'Type of business',business:'Company name',timing:'Start timing',meeting:'Meeting preference',availability:'Availability',name:'Name',email:'Email',phone:'Phone number'};
 function question(text){log.querySelectorAll('.chat-question').forEach(e=>e.remove());bubble(text);log.lastElementChild.classList.add('chat-question')}
 function show(){status.textContent=t('');questionMode=false;input.disabled=false;send.disabled=false;mode.textContent=t('Help me understand this');mode.hidden=false;input.type=steps[step]?.key==='email'?'email':steps[step]?.key==='phone'?'tel':'text';input.maxLength=steps[step]?.key==='issue'?1000:steps[step]?.key==='phone'?40:240;el.lang=chatLanguage();el.dir=['ar','fa'].includes(chatLanguage())?'rtl':'ltr';input.dir=['email','tel'].includes(input.type)?'ltr':'auto';input.placeholder=t(steps[step]?.placeholder||'Write a reply…');if(step>=steps.length){review();return}question(steps[step].q);choices(steps[step].choices,answer);saveConversation()}
 function review(){input.disabled=true;send.disabled=true;mode.hidden=true;question(t('Here is what Paper Trail will receive:')+'\n\n'+steps.filter(({key})=>details[key]).map(({key})=>t(labels[key])+': '+displayAnswer(key,details[key])).join('\n')+'\n\n'+t('Shall I send this so Paper Trail can follow up?'));choices(['Send my note','Change a detail'],v=>v==='Send my note'?submitNote():edit());saveConversation();}
 function edit(){question('Which detail would you like to change?');choices(steps.map(x=>labels[x.key]),label=>{step=steps.findIndex(x=>labels[x.key]===label);bubble('Let’s update that.');show();el.dataset.editing='true'});}
 function answer(text){if(busy||sent)return;let value=String(text).trim();if(steps[step]?.key==='phone')value=value.normalize('NFKC').replace(/[\u0660-\u0669\u06f0-\u06f9\u0966-\u096f\u0c66-\u0c6f]/g,c=>String([0x660,0x6f0,0x966,0xc66].map(start=>c.charCodeAt(0)-start).find(n=>n>=0&&n<=9)));if(!value)return;
  if(privatePattern.test(value)){status.textContent=t('Use a general description without financial account details.');return}
  if(value.length>input.maxLength){status.textContent=t('Please shorten your reply.');return}
  if(questionMode){ask(value);return}
  if(step>=steps.length)return;
  if(steps[step].key==='email'&&!/^\S+@\S+\.\S+$/.test(value)){status.textContent=t('Please enter a business email address.');return}
  if(steps[step].key==='business'&&value.length<2){status.textContent=t('Please enter your company name.');return}
  if(steps[step].key==='phone'){const number=value.split(/\s*(?:ext\.?|x)\s*/i)[0].replace(/\D/g,'');if(!/^[+\d().\s-]+(?:\s*(?:x|ext\.?)\s*\d{1,6})?$/i.test(value)||!(number.length===10||(number.length===11&&number.startsWith('1')))){status.textContent=t('Please enter a ten digit phone number, including the area code.');return}}
  const key=steps[step].key;originalAnswers[key]=steps[step].choices?.includes(String(text))?t(String(text)):String(text);details[key]=value;log.querySelectorAll('.chat-question').forEach(e=>e.remove());bubble(displayAnswer(key,value),true);input.value='';if(el.dataset.editing){delete el.dataset.editing;step=steps.length}else{step++;if((key==='meeting'&&value==='Email me first')||(key==='availability'&&value==='Arrange by email')){details.availability='Arrange by email';while(['availability','meetingTime','timeZone'].includes(steps[step]?.key))step++}}show();
 }
 function publishedNote(value){
  const stop=new Set('what how can does should would could my the a an is are to of for and in it i me do with this that about business bookkeeping'.split(' '));
  const tokens=text=>new Set((text.toLowerCase().match(/[\p{L}\p{N}]+/gu)||[]).filter(w=>!stop.has(w)));
  const words=tokens(value);const ranked=(config.notes||[]).map(n=>({n,score:value===n.title||value===t(n.title)?Infinity:[...tokens(t(n.title))].filter(w=>words.has(w)).length})).sort((a,b)=>b.score-a.score);
  if(ranked.length&&ranked[0].score>=2){const n=ranked[0].n;bubble(n.answer);const p=document.createElement('p');p.className='bubble';const a=document.createElement('a');a.href=n.url;a.textContent=t('Read the full note');p.append(a);for(const source of n.sources||[]){const ref=document.createElement('a');ref.href=source.url;ref.target='_blank';ref.rel='noopener';ref.textContent=t(source.title);ref.style.display='block';ref.style.fontSize='11px';p.append(ref)}log.append(p);log.scrollTop=log.scrollHeight;requestAnimationFrame(()=>{log.scrollTop=log.scrollHeight});status.textContent=t('');choices(['Continue my note'],()=>show());}
  else{bubble('These published notes may help. Choose one, or continue telling us about your business.');choices([...(config.notes||[]).slice(0,3).map(n=>n.title),'Continue my note'],v=>v==='Continue my note'?show():publishedNote(v));status.textContent=t('');}
 }
 async function ask(value){busy=true;input.value='';log.querySelectorAll('.chat-question').forEach(e=>e.remove());bubble(value,true);status.textContent=t('One moment…');send.disabled=true;options.replaceChildren();
  try{publishedNote(value);saveConversation();}
  finally{busy=false;send.disabled=false;if(!options.children.length)choices(['Continue my note'],()=>show());}
 }
 async function submitNote(){if(busy)return;busy=true;choices([]);status.textContent=t('Sending your note…');
  try{
   details.language=chatLanguage();details.originalAnswers={...originalAnswers};
   if(location.protocol==='file:')throw new Error('Your note has not been sent. Open the hosted website to send it.');
   if(window.PAPER_TRAIL_DIRECT_HUBSPOT===true){
    const {deliverToHubSpot}=await import('./hubspot.js?v=localized-chat-20261016');
    await deliverToHubSpot(details,config.topic,location.origin+location.pathname);
   }else{
    const r=await fetch('/api/inquiry',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({page:config.page,topic:config.topic,details,consent:true})});
    const d=await r.json();if(!r.ok||!d.ok)throw new Error(d.error||'We could not confirm delivery. Your note is still here.');
   }
   sent=true;status.textContent=t('');log.querySelectorAll('.chat-question').forEach(e=>e.remove());bubble('Your note is with Paper Trail. We have your contact details and everything you shared, including your meeting preference.');input.disabled=true;send.disabled=true;mode.hidden=true;
  }
  catch(e){status.textContent=t(e.message||'Your note was not sent. Please try again.');choices(['Try sending again','Change a detail'],v=>v==='Try sending again'?submitNote():edit());}
  finally{busy=false;saveConversation()}
 }
 send.addEventListener('click',()=>answer(input.value));input.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.isComposing){e.preventDefault();answer(input.value)}});
 mode.addEventListener('click',()=>{questionMode=!questionMode;if(questionMode){choices([]);question('What would you like to understand about this part of your bookkeeping?');input.placeholder=t('Write your question…');input.maxLength=1000;input.type='text';mode.textContent=t('Continue preparing my note');input.focus()}else show()});
 el.querySelector('.chat-reset').addEventListener('click',()=>{if(busy)return;step=0;details={};originalAnswers={};questionMode=false;sent=false;delete el.dataset.editing;log.replaceChildren();input.value='';show()});
 const dialog=document.getElementById('conversation-dialog');let opener=null,started=false;started=restoreConversation();
 document.querySelectorAll('[data-open-chat]').forEach(button=>button.addEventListener('click',()=>{opener=button;if(!started){show();started=true}if(!dialog.open)dialog.showModal();document.body.classList.add('dialog-open');requestAnimationFrame(()=>{if(!input.disabled)input.focus({preventScroll:true});else el.querySelector('.chat-close').focus({preventScroll:true})})}));
 document.addEventListener('preview-language',()=>{el.lang=chatLanguage();el.dir=['ar','fa'].includes(chatLanguage())?'rtl':'ltr';dialog.setAttribute('aria-label',t('Conversation with Paper Trail'));el.querySelector('label[for=chat-reply]').textContent=t('Your reply');if(started&&!sent){show()}});
 el.querySelector('.chat-close').addEventListener('click',()=>dialog.close());
 dialog.addEventListener('close',()=>{document.body.classList.remove('dialog-open');opener?.focus({preventScroll:true})});
 dialog.addEventListener('click',event=>{if(event.target!==dialog)return;const rect=dialog.getBoundingClientRect();if(event.clientX<rect.left||event.clientX>rect.right||event.clientY<rect.top||event.clientY>rect.bottom)dialog.close()});
})();
