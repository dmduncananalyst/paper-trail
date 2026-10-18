from pathlib import Path
import json,hashlib
copy={
'en':('Answer one question at a time to prepare your message.','Use the chat to tell Paper Trail about your bookkeeping needs.'),
'es':('Responde una pregunta a la vez para preparar tu mensaje.','Usa el chat para contarle a Paper Trail qué necesitas para tu contabilidad.'),
'fa':('برای آماده کردن پیام، هر بار به یک پرسش پاسخ دهید.','از طریق گفتگو نیازهای دفترداری خود را به Paper Trail بگویید.'),
'hy':('Ձեր հաղորդագրությունը պատրաստելու համար հերթով պատասխանեք հարցերին։','Զրույցի միջոցով Paper Trail ընկերությանը հայտնեք ձեր հաշվապահական կարիքները։'),
'zh-CN':('请逐一回答问题，准备您的留言。','请通过聊天向 Paper Trail 说明您的记账需求。'),
'ko':('질문에 하나씩 답하며 메시지를 작성해 주세요.','채팅으로 Paper Trail에 장부 관리에 필요한 사항을 알려 주세요.'),
'tl':('Sagutin ang isang tanong bawat pagkakataon upang ihanda ang iyong mensahe.','Gamitin ang chat upang sabihin sa Paper Trail ang iyong mga pangangailangan sa bookkeeping.'),
'te':('మీ సందేశాన్ని సిద్ధం చేయడానికి ఒక్కో ప్రశ్నకు సమాధానం ఇవ్వండి.','చాట్ ద్వారా మీ బుక్‌కీపింగ్ అవసరాలను Paper Trailకు తెలియజేయండి.'),
'ru':('Отвечайте на вопросы по одному, чтобы подготовить сообщение.','Расскажите Paper Trail в чате о ваших потребностях в учёте.'),
'ar':('أجب عن سؤال واحد في كل مرة لإعداد رسالتك.','استخدم المحادثة لإخبار Paper Trail باحتياجاتك في مسك الدفاتر.')}
for code,(notice,description) in copy.items():
 p=Path('assets/locales/home-blog')/(code+'.json');d=json.loads(p.read_text(encoding='utf-8'));d['chatNotice']=notice;d['mobileBlogSupport']=description;p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
p=Path('assets/locales/home-blog/manifest.json');d=json.loads(p.read_text(encoding='utf-8'))
for key,value in [('chatNotice',copy['en'][0]),('mobileBlogSupport',copy['en'][1])]:d['fields'][key]={'source':value,'source_sha256':hashlib.sha256(value.encode()).hexdigest(),'origin':'local_ai_draft','provider_verified':False}
d['guided_chat']={'file':'chat.json','languages':list(copy),'phrases_per_language':86,'origin':'local_authored_draft','google_calls':0,'speaker_review':'pending'};p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
p=Path('blog.html');s=p.read_text(encoding='utf-8').replace('Contact Paper Trail about your bookkeeping. Support is currently available in English.',copy['en'][1]);p.write_text(s,encoding='utf-8')
for p in list(Path('.').glob('*.html'))+list(Path('state-records').glob('*.html')):
 s=p.read_text(encoding='utf-8').replace('assets/site.js?v=follow-up-20261016','assets/site.js?v=localized-chat-20261016').replace('assets/design.js?v=mobile-menu-20261016','assets/design.js?v=localized-chat-20261016').replace('assets/design.css?v=mobile-menu-20261016','assets/design.css?v=localized-chat-20261016').replace('assets/locales/home-blog/current.js?v=mobile-menu-20261016','assets/locales/home-blog/current.js?v=localized-chat-20261016');p.write_text(s,encoding='utf-8')
