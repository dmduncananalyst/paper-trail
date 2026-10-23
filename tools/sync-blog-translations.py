"""Incremental local Google translations for the existing Paper Trail blog system.

Preserves saved fields, routes, assets and static language rendering. No publishing.
Each provider batch is durably reserved before dispatch; uncertain calls never retry.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
import argparse, hashlib, html, json, os, re, sqlite3, sys, tempfile, time

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / '.translation-cache'
OUT = ROOT / 'verification/approved-blogs-20261021/translations'
BASE = ROOT / 'assets/translation-workflow'
LANGUAGES = ['es', 'fa', 'hy', 'zh-CN', 'ko', 'tl', 'te', 'ru', 'ar']
PROJECT = 'project-2e0d7d9d-d482-4fcf-b6d'
ORIGIN = 'https://www.papertrailusa.com/'
PROTECTED = {'Paper Trail', 'PaperTrail', 'StartWeb7', 'Google', 'Google Translate', 'QuickBooks', 'Xero', 'Gmail', 'Microsoft 365 / Outlook'}
JSON_KEYS = {'name', 'description', 'headline', 'text', 'caption', 'alternativeHeadline'}

def normal(s): return re.sub(r'\s+', ' ', s).strip()
def digest(s): return hashlib.sha256(s.encode()).hexdigest()
def key(s, lang): return digest(normal(s)) + '|' + lang
def eligible(s): return bool(re.search('[A-Za-z]', s)) and s not in PROTECTED and not re.match(r'^(https?:|mailto:|tel:|[^\s]+@)', s)

def atomic(path, value):
    path = Path(path)
    data = value.encode() if isinstance(value, str) else value
    if path.exists() and path.read_bytes() == data: return
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix='.' + path.name)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data); stream.flush(); os.fsync(stream.fileno())
        for attempt in range(9):
            try: os.replace(temporary, path); break
            except PermissionError:
                if attempt == 8: raise
                time.sleep(min(.05 * 2 ** attempt, 2))
    finally:
        if os.path.exists(temporary): os.unlink(temporary)

def save_json(path, value): atomic(path, json.dumps(value, ensure_ascii=False, indent=2) + '\n')

class Inventory(HTMLParser):
    def __init__(self, markup):
        super().__init__(convert_charrefs=True)
        self.markup, self.slots, self.stack = markup, [], []
        self.offsets = [0]
        for line in markup.splitlines(keepends=True): self.offsets.append(self.offsets[-1] + len(line))
        self.feed(markup)

    def pos(self):
        line, col = self.getpos()
        return self.offsets[line - 1] + col

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs); raw = self.get_starttag_text(); start = self.pos()
        blocked = any(b for _, b in self.stack) or tag in {'script', 'style', 'code', 'pre', 'svg', 'select'} or attrs.get('translate') == 'no'
        if not blocked:
            for match in re.finditer(r'''([\w:-]+)\s*=\s*(["'])(.*?)\2''', raw, re.S):
                name = match[1].lower(); source = normal(html.unescape(match[3]))
                meta = tag == 'meta' and name == 'content' and (attrs.get('name') in {'description', 'twitter:title', 'twitter:description'} or attrs.get('property') in {'og:title', 'og:description'})
                if eligible(source) and (name in {'alt', 'title', 'placeholder', 'aria-label', 'aria-description'} or meta):
                    self.slots.append((start + match.start(3), start + match.end(3), source, True))
        if tag not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}: self.stack.append((tag, blocked))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if self.stack and self.stack[-1][0] == tag: self.stack.pop()

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]; break

    def handle_data(self, data):
        if any(b for _, b in self.stack): return
        start = self.pos(); end = self.markup.find('<', start)
        if end < 0: end = len(self.markup)
        raw = self.markup[start:end]; source = normal(html.unescape(raw))
        if eligible(source):
            a = start + len(raw) - len(raw.lstrip()); b = end - len(raw) + len(raw.rstrip())
            self.slots.append((a, b, source, False))

def schema_sources(value):
    if isinstance(value, list):
        for item in value: yield from schema_sources(item)
    elif isinstance(value, dict):
        for field, item in value.items():
            if field in JSON_KEYS and isinstance(item, str) and eligible(normal(item)): yield normal(item)
            elif isinstance(item, (dict, list)): yield from schema_sources(item)

def discover():
    archive = (ROOT / 'blog.html').read_text(encoding='utf-8')
    cards = re.findall(r'<article\b[^>]*class="[^"]*\bblog-story\b[^"]*"[^>]*>.*?</article>', archive, re.S)
    articles = []
    for card in cards:
        links = re.findall(r'<a\b[^>]*href="([^"]+)"', card)
        name = html.unescape(links[-1])
        if '/' in name or not (ROOT / name).is_file(): raise ValueError('Invalid blog article route: ' + name)
        if name not in articles: articles.append(name)
    return ['blog.html'] + articles

def load_fields():
    pointer = json.loads((BASE / 'current.json').read_text(encoding='utf-8'))
    fields = json.loads((BASE / 'releases' / pointer['revision'] / 'fields.json').read_text(encoding='utf-8'))['fields']
    for path in (STATE / 'provider-responses').glob('*.json'):
        receipt = json.loads(path.read_text(encoding='utf-8'))
        for source, value in zip(receipt['sources'], receipt['values']):
            if value.strip(): fields[key(source, receipt['locale'])] = {'source':normal(source), 'locale':receipt['locale'], 'text':value, 'provider':'google', 'receipt':path.name}
    return pointer, fields

def inventory():
    names = discover(); pages = {}; refs = set()
    for name in names:
        inv = Inventory((ROOT / name).read_text(encoding='utf-8')); pages[name] = inv
        refs.update(s[2] for s in inv.slots)
        for match in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', inv.markup, re.S): refs.update(schema_sources(json.loads(match[1])))
    pointer, fields = load_fields()
    missing = {lang: sorted(s for s in refs if key(s, lang) not in fields) for lang in LANGUAGES}
    characters = sum(len(s) for values in missing.values() for s in values)
    report = {'blogs':len(names)-1, 'pages':names, 'languages':LANGUAGES, 'missing_fields':sum(map(len,missing.values())), 'source_characters_to_translate':characters, 'estimated_gross_cost_usd':characters * 20 / 1_000_000, 'paid_calls':0, 'local_only':True}
    return pages, pointer, fields, missing, report

def dispatch(fields, missing, report):
    # Standing owner authorization applies to complete blog translations only.
    policy = json.loads((ROOT / 'tools/blog-translation-policy.json').read_text())
    if not policy.get('standing_paid_blog_translation_approval') or policy['languages'] != LANGUAGES: raise ValueError('Blog translation authorization missing')
    import google.auth
    from google.auth.transport.requests import AuthorizedSession
    credentials_path = ROOT.parent / 'sun-and-sage/.tools/gcloud-profile/application_default_credentials.json'
    os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', str(credentials_path))
    credentials, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'], quota_project_id=PROJECT)
    session = AuthorizedSession(credentials)
    # Keep the configured project and existing API; create no cloud resources.
    for service in ['translate.googleapis.com']:
        response = session.get(f'https://serviceusage.googleapis.com/v1/projects/{PROJECT}/services/{service}', timeout=30)
        response.raise_for_status()
        if response.json().get('state') != 'ENABLED': raise ValueError('Existing translation API is not enabled')
    response = session.get(f'https://translation.googleapis.com/v3/projects/{PROJECT}/locations/global/supportedLanguages', timeout=30)
    response.raise_for_status()
    available = {item['languageCode'] for item in response.json().get('languages', []) if item.get('supportTarget')}
    if not set(LANGUAGES).issubset(available): raise ValueError('Provider language support check failed')
    STATE.mkdir(exist_ok=True)
    database = sqlite3.connect(STATE / 'blog-requests.sqlite3')
    database.execute('CREATE TABLE IF NOT EXISTS requests (id TEXT PRIMARY KEY, locale TEXT, characters INTEGER, status TEXT, created REAL, error TEXT)')
    database.execute('CREATE TABLE IF NOT EXISTS segments (id TEXT PRIMARY KEY, request TEXT, source TEXT, locale TEXT)')
    database.commit()
    ceiling = report['source_characters_to_translate']; sent = 0
    save_json(OUT / 'authorized-scope.json', {**report, 'approval':'Standing owner approval for every blog in all nine languages; local only', 'dispatch_character_ceiling':ceiling, 'historical_shared_ledger':'Original private ledger absent in this checkout; this durable job ledger records incremental blog calls without claiming an account-wide balance.'})
    for lang, sources in missing.items():
        groups = []; group = []; size = 0
        for source in sources:
            if group and (size + len(source) > 4500 or len(group) >= 50): groups.append(group); group = []; size = 0
            if len(source) > 30000: raise ValueError('Source paragraph exceeds provider limit')
            group.append(source); size += len(source)
        if group: groups.append(group)
        for group in groups:
            chars = sum(map(len, group))
            if sent + chars > ceiling: raise ValueError('Approved job scope exceeded')
            identifier = digest(lang + '\0' + '\0'.join(group))
            with database:
                for source in group:
                    prior = database.execute('SELECT request FROM segments WHERE id=?', (key(source,lang),)).fetchone()
                    if prior: raise ValueError('Previously reserved segment requires reconciliation; refusing duplicate paid call')
                database.execute('INSERT INTO requests VALUES (?,?,?,?,?,NULL)', (identifier,lang,chars,'reserved',time.time()))
                database.executemany('INSERT INTO segments VALUES (?,?,?,?)', [(key(s,lang),identifier,s,lang) for s in group])
            try:
                response = session.post(f'https://translation.googleapis.com/v3/projects/{PROJECT}/locations/global:translateText', json={'contents':group,'mimeType':'text/plain','sourceLanguageCode':'en','targetLanguageCode':lang,'model':f'projects/{PROJECT}/locations/global/models/general/nmt'}, timeout=90)
                response.raise_for_status()
                values = [html.unescape(item['translatedText']) for item in response.json()['translations']]
                if len(values) != len(group) or any(not v.strip() for v in values): raise ValueError('Incomplete provider response')
                receipt = {'locale':lang, 'sources':group, 'values':values, 'characters':chars, 'received_at':time.time(), 'request':identifier}
                save_json(STATE / 'provider-responses' / (identifier + '.json'), receipt)
                with database: database.execute("UPDATE requests SET status='complete' WHERE id=?", (identifier,))
                for source,value in zip(group,values): fields[key(source,lang)]={'source':source,'locale':lang,'text':value,'provider':'google','receipt':identifier+'.json'}
                sent += chars; report['paid_calls'] += 1; report['characters_sent'] = sent
                save_json(OUT / 'progress.json', report)
                print(json.dumps({'language':lang,'calls':report['paid_calls'],'characters_sent':sent}), flush=True)
            except BaseException as error:
                with database: database.execute("UPDATE requests SET status='uncertain',error=? WHERE id=? AND status!='complete'", (type(error).__name__,identifier))
                raise
    database.close()

def translated_schema(value, lang, fields, routes, body):
    def text(s): return fields[key(s,lang)]['text'] if eligible(normal(s)) else s
    def url(s):
        if not isinstance(s,str) or not s.startswith(ORIGIN): return s
        path = s[len(ORIGIN):].split('#')[0]
        return ORIGIN + lang + '/' + s[len(ORIGIN):] if path in routes else s
    if isinstance(value,list): return [translated_schema(v,lang,fields,routes,body) for v in value]
    if not isinstance(value,dict): return value
    result = {}
    for field,item in value.items():
        if field == 'articleBody' and body is not None: result[field] = body
        elif field in JSON_KEYS and isinstance(item,str): result[field] = text(item)
        elif field in {'url','@id','mainEntityOfPage','item'} and isinstance(item,str): result[field] = url(item)
        else: result[field] = translated_schema(item,lang,fields,routes,body)
    if result.get('@type') in {'BlogPosting','Article','WebPage','CollectionPage','WebSite'}: result['inLanguage'] = lang
    return result

def alternates(markup, name):
    markup = re.sub(r'<link[^>]*data-paper-trail-translation-alternate="true"[^>]*>', '', markup)
    tags = ''.join(f'<link rel="alternate" hreflang="{lang}" href="{ORIGIN}{lang+"/" if lang not in {"en","x-default"} else ""}{name}" data-paper-trail-translation-alternate="true">' for lang in ['en',*LANGUAGES,'x-default'])
    return markup.replace('</head>', tags + '</head>', 1)

def build(pages, pointer, fields, report):
    revision = digest(json.dumps({k:v['text'] for k,v in fields.items()},sort_keys=True))
    routes = pointer['routes']
    for lang in LANGUAGES: routes[lang] = sorted(set(routes.get(lang,[])) | set(pages))
    for name, inv in pages.items():
        for lang in LANGUAGES:
            markup = inv.markup
            for a,b,source,attribute in sorted(inv.slots, reverse=True):
                markup = markup[:a] + html.escape(fields[key(source,lang)]['text'],quote=attribute) + markup[b:]
            markup = re.sub(r'<base\b[^>]*>', '', markup)
            markup = markup.replace('<head>','<head><base href="../">',1)
            markup = re.sub(r'<html\b[^>]*>', f'<html lang="{lang}" dir="ltr" data-static-locale="{lang}">',markup,count=1)
            markup = re.sub(r'<(?:p|small)\b[^>]*class="article-language"[^>]*>.*?</(?:p|small)>','',markup,flags=re.S)
            markup = re.sub(r'(<link rel="canonical" href=")[^"]+("\s*/?>)',lambda m:m[1]+ORIGIN+lang+'/'+name+m[2],markup)
            markup = re.sub(r'(<meta property="og:url" content=")[^"]+(")',lambda m:m[1]+ORIGIN+lang+'/'+name+m[2],markup)
            og_locale={'es':'es_US','fa':'fa_IR','hy':'hy_AM','zh-CN':'zh_CN','ko':'ko_KR','tl':'tl_PH','te':'te_IN','ru':'ru_RU','ar':'ar_SA'}[lang]
            markup = re.sub(r'(<meta property="og:locale" content=")[^"]+(")',lambda m:m[1]+og_locale+m[2],markup)
            def link(match):
                target = html.unescape(match[2]); path = urlsplit(target).path
                return match[1]+lang+'/'+target+match[3] if path in routes[lang] else match[0]
            markup = re.sub(r'(<a\b[^>]*\bhref=")([^"]*)(")',link,markup)
            body_match = re.search(r'<div class="reading-spread">(.*?)(?:<section class="reference-list">|</article>)',inv.markup,re.S)
            body = None
            if body_match:
                body = '\n\n'.join(fields[key(normal(html.unescape(re.sub('<[^>]+>','',m[1]))),lang)]['text'] for m in re.finditer(r'<(?:p|h2)\b[^>]*>(.*?)</(?:p|h2)>',body_match[1],re.S))
            markup = re.sub(r'<script type="application/ld\+json">(.*?)</script>',lambda m:'<script type="application/ld+json">'+json.dumps(translated_schema(json.loads(m[1]),lang,fields,routes[lang],body),ensure_ascii=True)+'</script>',markup,flags=re.S)
            markup = alternates(markup,name)
            # Retain the site's saved Google attribution and translated notice.
            existing = ROOT / lang / name
            fallback = ROOT / lang / 'blog.html'
            old = (existing if existing.exists() else fallback).read_text(encoding='utf-8')
            credit = re.search(r'<aside class="translation-credit".*?</aside>',old,re.S)
            if credit: markup = markup.replace('</main>',credit[0]+'</main>',1)
            markup = markup.replace('</head>',f'<link rel="alternate machine-translated-from" hreflang="en" href="{ORIGIN}{name}"></head>',1)
            atomic(existing,markup)
        atomic(ROOT/name,alternates(inv.markup,name))
    save_json(BASE/'releases'/revision/'fields.json', {'provider':'google','fields':fields})
    pointer.update(revision=revision,routes=routes)
    pointer.setdefault('source_fingerprints',{}).update({name:digest(json.dumps([s[2] for s in inv.slots])) for name,inv in pages.items()})
    pointer['source_pages'] = len(set(n for values in routes.values() for n in values))
    save_json(BASE/'current.json',pointer)
    atomic(BASE/'routes.js','window.paperTrailTranslationRoutes='+json.dumps(routes)+';\n')
    provider_path = ROOT/'assets/locales/home-blog/provider-current.json'
    provider = json.loads(provider_path.read_text()); provider['revision']=revision; save_json(provider_path,provider)
    manifest_path = ROOT/'assets/locales/home-blog/manifest.json'
    manifest=json.loads(manifest_path.read_text()); manifest['revision']=revision; manifest['source_pages']=sorted(set(manifest['source_pages'])|set(pages)); manifest['status']='Saved Google translations. No visitor API calls. Native speaker review pending.'
    manifest['google_calls'] += report['paid_calls']; manifest['google_characters_sent'] += report.get('characters_sent',0)
    ledger=STATE/'blog-requests.sqlite3'
    if ledger.exists():
        with sqlite3.connect(ledger) as db:
            calls,characters=db.execute("SELECT COUNT(*),COALESCE(SUM(characters),0) FROM requests WHERE status='complete'").fetchone()
        manifest['successful_characters_saved']=manifest.get('successful_characters_saved',0)+max(0,characters-manifest.get('blog_sync_successful_characters',0))
        manifest['blog_sync_successful_characters']=characters
        report.update(total_saved_blog_paid_calls=calls,total_saved_blog_paid_characters=characters)
    save_json(manifest_path,manifest)
    sitemap = ROOT/'sitemap-translations.xml'; xml=sitemap.read_text(encoding='utf-8')
    for lang in LANGUAGES:
        for name in pages:
            url=ORIGIN+lang+'/'+name
            if '<loc>'+url+'</loc>' not in xml: xml=xml.replace('</urlset>','<url><loc>'+url+'</loc></url></urlset>')
    atomic(sitemap,xml)
    report.update(rendered_language_pages=len(pages)*len(LANGUAGES),missing_fields=0,revision=revision)
    save_json(OUT/'results.json',report)

def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--refresh',action='store_true'); args=parser.parse_args()
    pages,pointer,fields,missing,report=inventory(); save_json(OUT/'inventory.json',report)
    print(json.dumps(report,indent=2),flush=True)
    if not args.refresh: return
    STATE.mkdir(exist_ok=True); lock=STATE/'full-site.lock'
    descriptor=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.close(descriptor)
    try:
        if report['missing_fields']: dispatch(fields,missing,report)
        build(pages,pointer,fields,report)
        print(json.dumps(report,indent=2),flush=True)
    finally: lock.unlink(missing_ok=True)

if __name__=='__main__': main()
