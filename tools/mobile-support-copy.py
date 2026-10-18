from pathlib import Path
import json,hashlib
copy={
'en':('Get Bookkeeping Support','Contact Paper Trail about your bookkeeping. Support is currently available in English.'),
'es':('Recibe apoyo contable','Contacta a Paper Trail para hablar de tu contabilidad. Por ahora, la atención está disponible en inglés.'),
'fa':('دریافت پشتیبانی دفترداری','برای دفترداری کسب و کارتان با Paper Trail تماس بگیرید. پشتیبانی در حال حاضر به زبان انگلیسی ارائه می‌شود.'),
'hy':('Ստանալ հաշվապահական աջակցություն','Ձեր հաշվապահության հարցերով կապվեք Paper Trail-ի հետ։ Աջակցությունն այժմ տրամադրվում է անգլերեն։'),
'zh-CN':('获取记账支持','请联系 Paper Trail，咨询您的记账需求。目前我们使用英语提供支持。'),
'ko':('장부 관리 지원 받기','장부 관리에 관해 Paper Trail에 문의하세요. 현재 지원은 영어로 제공됩니다.'),
'tl':('Kumuha ng Suporta sa Bookkeeping','Makipag ugnayan sa Paper Trail tungkol sa iyong bookkeeping. Sa ngayon, Ingles ang ginagamit sa suporta.'),
'te':('బుక్‌కీపింగ్ సహాయం పొందండి','మీ బుక్‌కీపింగ్ గురించి Paper Trailను సంప్రదించండి. ప్రస్తుతం సహాయం ఆంగ్లంలో అందుబాటులో ఉంది.'),
'ru':('Получить помощь с учётом','Свяжитесь с Paper Trail по вопросам ведения учёта. Сейчас поддержка доступна на английском языке.'),
'ar':('احصل على دعم مسك الدفاتر','تواصل مع Paper Trail بشأن مسك دفاتر نشاطك التجاري. يتوفر الدعم حاليا باللغة الإنجليزية.')}
for code,(button,description) in copy.items():
 p=Path('assets/locales/home-blog')/(code+'.json');d=json.loads(p.read_text(encoding='utf-8'));d['mobileSupport']=button;d['mobileBlogSupport']=description;p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
p=Path('index.html');s=p.read_text(encoding='utf-8');old='<button class="action" data-open-chat type="button" data-i18n="talk">Talk With Paper Trail</button>';new='<button class="action" data-open-chat type="button"><span class="desktop-label" data-i18n="talk">Talk With Paper Trail</span><span class="mobile-label" data-i18n="mobileSupport">Get Bookkeeping Support</span></button>';assert old in s;s=s.replace(old,new);p.write_text(s,encoding='utf-8')
p=Path('blog.html');s=p.read_text(encoding='utf-8');assert 'class="mobile-support"' not in s;s=s.replace('</main>','<section class="mobile-support" aria-label="Bookkeeping support"><p data-i18n="mobileBlogSupport">'+copy['en'][1]+'</p><a class="action" href="areas-we-serve.html" data-i18n="mobileSupport">Get Bookkeeping Support</a></section></main>');p.write_text(s,encoding='utf-8')
locales={p.stem:json.loads(p.read_text(encoding='utf-8')) for p in Path('assets/locales/home-blog').glob('*.json') if p.stem!='manifest'}
Path('assets/locales/home-blog/current.js').write_text('/* Saved authored Home and Blog drafts. No provider calls. */\nwindow.PAPER_TRAIL_LOCALES='+json.dumps(locales,ensure_ascii=False)+';\n',encoding='utf-8')
p=Path('assets/locales/home-blog/manifest.json');d=json.loads(p.read_text(encoding='utf-8'))
for key,v in zip(['mobileSupport','mobileBlogSupport'],copy['en']):d['fields'][key]={'source':v,'source_sha256':hashlib.sha256(v.encode()).hexdigest(),'origin':'local_ai_draft','provider_verified':False}
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
for p in list(Path('.').glob('*.html'))+list(Path('state-records').glob('*.html')):
 s=p.read_text(encoding='utf-8').replace('assets/design.css?v=mobile-refinements-20261016','assets/design.css?v=mobile-menu-20261016').replace('assets/design.js?v=follow-up-20261016','assets/design.js?v=mobile-menu-20261016').replace('assets/locales/home-blog/current.js?v=mobile-refinements-20261016','assets/locales/home-blog/current.js?v=mobile-menu-20261016');p.write_text(s,encoding='utf-8')
print('Localized phone support labels and Blog contact section added without provider calls.')
