from pathlib import Path

if 'function t(value)' in Path('assets/site.js').read_text(encoding='utf-8'):raise SystemExit('Already applied. Preserve the saved files and use the locale bundle builder for future translation edits.')
p=Path('assets/site.js');s=p.read_text(encoding='utf-8')
s=s.replace(" const log=el.querySelector",''' const chatLanguage=()=>document.querySelector('.page-language #language')?document.documentElement.lang||'en':'en';
 function t(value){const language=chatLanguage(),dictionary=window.PAPER_TRAIL_CHAT_LOCALES?.[language];if(dictionary&&Object.hasOwn(dictionary,value))return dictionary[value];const ui=window.PAPER_TRAIL_LOCALES,key=Object.keys(ui?.en||{}).find(k=>ui.en[k]===value);return key&&ui?.[language]?.[key]||value}
 const log=el.querySelector''',1)
s=s.replace("p.textContent=text;log.append(p)","p.textContent=user?text:t(text);log.append(p)")
s=s.replace("b.textContent=label;b.addEventListener", "b.textContent=t(label);b.addEventListener")
s=s.replace(" const labels={", " const displayAnswer=(key,value)=>steps.find(s=>s.key===key)?.choices?.includes(value)?t(value):value;\n const labels={")
s=s.replace("mode.textContent='Help me understand this'", "mode.textContent=t('Help me understand this')")
s=s.replace("input.placeholder=steps[step]?.placeholder||", "el.lang=chatLanguage();el.dir=['ar','fa'].includes(chatLanguage())?'rtl':'ltr';input.dir=['email','tel'].includes(input.type)?'ltr':'auto';input.placeholder=t(steps[step]?.placeholder||")
# Close the newly wrapped placeholder expression without touching its original spelling.
s=s.replace(";if(step>=steps.length){review();return}question(steps[step].q)", ");if(step>=steps.length){review();return}question(steps[step].q)")
s=s.replace("question('Here is what Paper Trail will receive:\\n\\n'+steps.filter(({key})=>details[key]).map(({key})=>labels[key]+': '+details[key]).join('\\n')+'\\n\\nShall I send this so Paper Trail can follow up?')", "question(t('Here is what Paper Trail will receive:')+'\\n\\n'+steps.filter(({key})=>details[key]).map(({key})=>t(labels[key])+': '+displayAnswer(key,details[key])).join('\\n')+'\\n\\n'+t('Shall I send this so Paper Trail can follow up?'))")
s=s.replace("bubble(value,true);input.value='';if(el.dataset.editing)","bubble(displayAnswer(key,value),true);input.value='';if(el.dataset.editing)")
s=s.replace(" function publishedNote(value){", " function publishedNote(value){\n  if(chatLanguage()!=='en'){bubble('Please include your bookkeeping question in your message so Paper Trail can follow up.');choices(['Continue my note'],()=>show());status.textContent='';return}")
s=s.replace("try{if(location.protocol==='file:')throw", "try{if(chatLanguage()!=='en'){publishedNote(value);return}if(location.protocol==='file:')throw",1)
# Translate status and placeholder literals, leaving canonical branch values untouched.
import re
s=re.sub(r"status\.textContent=('(?:[^'\\]|\\.)*')",r'status.textContent=t(\1)',s)
s=re.sub(r"input\.placeholder=('(?:[^'\\]|\\.)*')",r'input.placeholder=t(\1)',s)
s=s.replace("mode.textContent='Continue preparing my note'", "mode.textContent=t('Continue preparing my note')")
s=s.replace("status.textContent=e.message||'Your note was not sent. Please try again.'", "status.textContent=t(e.message||'Your note was not sent. Please try again.')")
s=s.replace("try{\n   if(location.protocol==='file:')", "try{\n   if(document.querySelector('.page-language #language'))details.language=chatLanguage();\n   if(location.protocol==='file:')")
# Refresh the active question and canonical choice labels when the page language changes.
s=s.replace(" el.querySelector('.chat-close').addEventListener", " document.addEventListener('preview-language',()=>{dialog.setAttribute('aria-label',t('Conversation with Paper Trail'));el.querySelector('label[for=chat-reply]').textContent=t('Your reply');if(started){log.replaceChildren();steps.filter(s=>details[s.key]).forEach(s=>bubble(displayAnswer(s.key,details[s.key]),true));show()}});\n el.querySelector('.chat-close').addEventListener")
p.write_text(s,encoding='utf-8')
p=Path('assets/hubspot.js');s=p.read_text(encoding='utf-8').replace("  state:'State',", "  language:'Conversation language', state:'State',");p.write_text(s,encoding='utf-8')
print('Canonical question sequence retained; display translation hooks added.')
