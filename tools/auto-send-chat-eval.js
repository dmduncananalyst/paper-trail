(async()=>{
 const dictionary=window.PAPER_TRAIL_CHAT_LOCALES[document.documentElement.lang];
 const assert=(ok,message)=>{if(!ok)throw Error(message)};
 const answer=value=>{document.querySelector('.chat input').value=value;document.querySelector('.send-message').click()};
 const choice=()=>document.querySelector('.chat-options button').click();
 const wait=async test=>{for(let i=0;i<100;i++){if(test())return;await new Promise(r=>setTimeout(r,25))}throw Error('Timed out waiting for delivery state')};
 const status=()=>document.querySelector('.chat-status').textContent;
 const buttons=()=>[...document.querySelectorAll('.chat-options button')].map(b=>b.textContent);
 const confirmed=()=>[...document.querySelectorAll('.bubble')].some(b=>b.textContent===dictionary['Your note is with Paper Trail. We have your contact details and everything you shared, including your meeting preference.']);
 let calls=0,payload,resolveDelivery,fail=false;
 const originalFetch=window.fetch;
 window.fetch=async(url,init)=>{
  assert(String(url).startsWith('https://api.hsforms.com/'),'Unexpected endpoint');
  calls++;payload=JSON.parse(init.body);
  if(fail)throw Error('Simulated delivery failure');
  return new Promise(resolve=>{resolveDelivery=()=>resolve({ok:true,status:200})});
 };
 const fill=()=>{
  document.querySelector('.chat-reset').click();
  answer('California');choice();choice();choice();answer('Example shop');answer('Example Company');
  choice();choice();choice();choice();choice();answer('Example Owner');
  answer('invalid');assert(status()===dictionary['Please enter a business email address.'],'Email validation missing');
  answer('owner@example.com');answer('12');assert(status()===dictionary['Please enter a ten digit phone number, including the area code.'],'Phone validation missing');
 };
 try{
  fill();assert(calls===0,'Sent before valid final answer');answer('8185550123');
  await wait(()=>calls===1);
  assert(!buttons().length&&!document.querySelector('.chat-question'),'Confirmation step remains');
  answer('8185550123');document.querySelector('.send-message').click();
  assert(calls===1,'Duplicate send while delivery is pending');
  resolveDelivery();await wait(confirmed);
  assert(document.querySelector('.chat input').disabled&&!buttons().length,'Chat did not finish');
  assert(payload.fields.some(f=>f.name==='email'&&f.value==='owner@example.com'),'Contact details missing');
  fail=true;fill();answer('8185550123');
  await wait(()=>buttons().includes(dictionary['Try sending again']));
  assert(calls===2&&!confirmed(),'Failure incorrectly reported as success');
  // Editing a failed submission automatically sends the corrected details.
  document.querySelectorAll('.chat-options button')[1].click();choice();
  fail=false;answer('Nevada');await wait(()=>calls===3);
  assert(payload.fields.find(f=>f.name==='message').value.includes('State: Nevada'),'Edited details missing');
  resolveDelivery();await wait(confirmed);
  // A failed automatic send still offers a translated retry.
  fail=true;fill();answer('8185550123');await wait(()=>calls===4&&buttons().length===2);
  fail=false;choice();await wait(()=>calls===5);resolveDelivery();await wait(confirmed);
  return {language:document.documentElement.lang,automaticSend:true,validation:true,noConfirmation:true,noDuplicate:true,editAfterFailure:true,retry:true,calls};
 }finally{window.fetch=originalFetch}
})()
