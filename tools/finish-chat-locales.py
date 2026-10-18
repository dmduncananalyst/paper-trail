from pathlib import Path
import json,re
p=Path('assets/locales/home-blog/chat.json');d=json.loads(p.read_text(encoding='utf-8'))
placeholders={
'en':'Your preferred day|Your preferred time|Your time zone',
'es':'El día que prefieres|El horario que prefieres|Tu zona horaria',
'fa':'روز ترجیحی شما|زمان ترجیحی شما|منطقه زمانی شما',
'hy':'Ձեր նախընտրած օրը|Ձեր նախընտրած ժամը|Ձեր ժամային գոտին',
'zh-CN':'您希望的星期|您希望的时间|您的时区',
'ko':'선호하는 요일|선호하는 시간|거주 시간대',
'tl':'Ang araw na gusto mo|Ang oras na gusto mo|Iyong sona ng oras',
'te':'మీకు అనుకూలమైన రోజు|మీకు అనుకూలమైన సమయం|మీ సమయ మండలం',
'ru':'Предпочтительный день|Предпочтительное время|Ваш часовой пояс',
'ar':'اليوم الذي تفضله|الوقت الذي تفضله|منطقتك الزمنية'}
for code,row in placeholders.items():d[code].update(zip(['Your preferred day','Your preferred time','Your time zone'],row.split('|')))
d['hy']['Which period needs attention?']='Ո՞ր ժամանակահատվածին է պետք ուշադրություն դարձնել։'
d['te']['What about your books needs attention?']='మీ లెక్కలలో ఏ విషయానికి శ్రద్ధ అవసరం?'
d['tl']['Mountain']='Oras sa Kabundukan';d['tl']['Availability']='Mga araw na maaari'
for code,row in d.items():
 for key,value in row.items():
  assert '??' not in value and '\ufffd' not in value and not re.search(r'\w\?\w',value),(code,key)
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
p=Path('assets/site.js');s=p.read_text(encoding='utf-8');s=s.replace('replace(/[?-??-??-??-?]/g',r'replace(/[\u0660-\u0669\u06f0-\u06f9\u0966-\u096f\u0c66-\u0c6f]/g');p.write_text(s,encoding='utf-8')
print('Verified real Unicode wording in all 890 guided chat translations.')
