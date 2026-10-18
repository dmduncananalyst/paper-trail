(async()=>{
 const dictionary=window.PAPER_TRAIL_CHAT_LOCALES[document.documentElement.lang];
 document.querySelectorAll('.chat-options button')[1].click();
 const editLabels=[...document.querySelectorAll('.chat-options button')].map(b=>b.textContent);
 document.querySelector('.chat-options button').click();document.querySelector('.chat input').value='Nevada';document.querySelector('.send-message').click();
 const edited=document.querySelector('.chat-question').textContent.includes(dictionary.State+': Nevada');
 const originalFetch=window.fetch;let payload=null;
 window.fetch=async(url,init)=>{if(String(url).startsWith('https://api.hsforms.com/')){payload=JSON.parse(init.body);return {ok:true,status:200}}throw Error('Unexpected request blocked by local test')};
 try{
 document.querySelector('.chat-options button').click();
 for(let i=0;i<100;i++){if([...document.querySelectorAll('.bubble')].some(b=>b.textContent===dictionary['Your note is with Paper Trail. We have your contact details and everything you shared, including your meeting preference.']))break;await new Promise(r=>setTimeout(r,50))}
 return {edited,editLabels,confirmationTranslated:[...document.querySelectorAll('.bubble')].some(b=>b.textContent===dictionary['Your note is with Paper Trail. We have your contact details and everything you shared, including your meeting preference.']),activeQuestions:document.querySelectorAll('.chat-question').length,mockPayload:payload,externalDeliveryPerformed:false};
 }finally{window.fetch=originalFetch}
})()
