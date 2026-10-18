(async()=>{
 const click=()=>document.querySelector('.send-message').click();
 const answer=value=>{document.querySelector('.chat input').value=value;click()};
 const q=()=>document.querySelector('.chat-question')?.textContent;
 const d=window.PAPER_TRAIL_CHAT_LOCALES[document.documentElement.lang];
 const questions=[],options=[],errors=[];
 const capture=()=>{questions.push(q());options.push([...document.querySelectorAll('.chat-options button')].map(e=>e.textContent))};
 document.querySelector('.chat-reset').click();capture();answer('California');capture();document.querySelector('.chat-options button').click();capture();document.querySelector('.chat-options button').click();capture();document.querySelector('.chat-options button').click();capture();answer('Example shop');capture();answer('Example Company');capture();document.querySelector('.chat-options button').click();capture();document.querySelector('.chat-options button').click();capture();document.querySelector('.chat-options button').click();capture();document.querySelector('.chat-options button').click();capture();document.querySelector('.chat-options button').click();capture();answer('Example Owner');capture();answer('invalid');errors.push(document.querySelector('.chat-status').textContent);answer('owner@example.com');capture();answer('12');errors.push(document.querySelector('.chat-status').textContent);answer('8185550123');
 const review=q(),activeQuestions=document.querySelectorAll('.chat-question').length;
 const expected=['What state are you located in?','What about your books needs attention?','Which period needs attention?','Where are your books kept at the moment?','What does your business do?','What is your company name?','When would you like this work to begin?','What kind of meeting would work best for you?','What day would you prefer to meet?','What time usually works best for you?','What time zone are you in?','What name should we use when we reply?','What email should Paper Trail use to follow up?','What phone number can we reach you on?'];
 const result={questions,options,errors,review,activeQuestions,questionsMatch:questions.every((v,i)=>v===d[expected[i]]),errorsMatch:errors[0]===d['Please enter a business email address.']&&errors[1]===d['Please enter a ten digit phone number, including the area code.'],reviewTranslated:review.startsWith(d['Here is what Paper Trail will receive:']),direction:document.querySelector('.chat').dir,overflow:document.querySelector('.chat').scrollWidth>document.querySelector('.chat').clientWidth+2};
 await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
 return result;
})()
