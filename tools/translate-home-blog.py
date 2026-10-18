"""Paper Trail Home/Blog runner. Default: offline, read-only inventory.

Reuses the sibling DommyDom budget/auth/provider modules, never duplicates cloud
configuration. Live mode requires --approve-google-calls and a valid shared quote.
"""
import argparse
import html
from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT.parent / 'sun-and-sage' / 'scripts'
if not (SHARED / 'translation_pipeline/budget.py').is_file():
    raise RuntimeError('Existing DommyDom shared translation modules are required')
sys.path.insert(0, str(SHARED))
from translation_pipeline.budget import ExistingBudget
from translation_pipeline.connection import private_path, access_token
from translation_pipeline.pipeline import Parser, LOCALES, atomic, encoded, digest, google_translate, budget_warning

PROJECT = 'project-2e0d7d9d-d482-4fcf-b6d'
PAGES = ('index.html', 'blog.html')
BASE = Path('assets/locales/home-blog')


def counter_connection(root=ROOT):
    """Pure read-only check; no schema creation, token retrieval or reservation."""
    path = private_path('DOMMYDOM_SHARED_BUDGET_DB', 'shared-usage.sqlite')
    if not path.is_absolute() or path.resolve().is_relative_to(Path(root).resolve()):
        raise ValueError('Shared database must be private and outside Paper Trail')
    budget = ExistingBudget(path, read_only=True)
    status = budget.status()
    snapshot = status['snapshot']
    matches = bool(snapshot and snapshot.get('project') == PROJECT)
    quote = budget.quote(0)
    return {'connected': True, 'project_matches': matches,
            'shared_database': str(path.resolve()), 'read_only': True,
            'opening_characters': snapshot.get('opening_characters') if snapshot else None,
            'warning_usd': snapshot.get('soft_usd') if snapshot else None,
            'cutoff_usd': snapshot.get('hard_usd') if snapshot else None,
            'reservation_count': len(status['reservations']),
            'live_dispatch_allowed': matches and quote['allowed'],
            'blocked_reason': quote['reason'] if not quote['allowed'] else (None if matches else 'Google project mismatch'),
            'google_calls': 0}


def annotate_blog(markup):
    """Discover new real cards automatically; add attributes without layout edits."""
    def card(match):
        block = match.group()
        parsed = Parser(); parsed.feed(block)
        links = parsed.root.find(lambda n: n.tag == 'a' and n.attrs.get('href'))
        if not links: raise ValueError('Blog card has no article link')
        url = links[-1].attrs['href'].split('?', 1)[0].split('#', 1)[0]
        prefix = 'blogCard-' + digest(url)[:16]
        def mark_tag(tag, suffix):
            return tag if re.search(r'\bdata-i18n\s*=', tag) else tag[:-1] + ' data-i18n="' + prefix + '-' + suffix + '">'
        block = re.sub(r'<h2\b[^>]*>', lambda m: mark_tag(m.group(), 'title'), block, count=1)
        for cls, suffix in [('blog-preview', 'preview')]:
            block = re.sub(r'<p\b[^>]*>', lambda m: mark_tag(m.group(), suffix)
                           if re.search(r'\bclass=[\"\'][^\"\']*\b' + cls + r'\b', m.group()) else m.group(), block)
        # Localize the publication LABEL while retaining semantic <time datetime>.
        block = re.sub(r'(<p\b[^>]*class=[\"\'][^\"\']*\bpublication-date\b[^>]*>)([^<]+)(<time\b[\s\S]*?</time>)([\s\S]*?</p>)',
                       lambda m: m[1] + '<span data-i18n="' + prefix + '-publication">' + html.escape(m[2].strip()) + '</span> ' + m[3] + m[4], block)
        return block
    return re.sub(r'<article\b[^>]*class=[\"\'][^\"\']*\bblog-story\b[^\"\']*[\"\'][^>]*>[\s\S]*?</article>', card, markup)


def sources(root):
    # Runtime chat/email labels already belonging to Home/Blog retain their keys.
    english = json.loads((root / BASE / 'en.json').read_text(encoding='utf-8'))
    marked = {}; pages = {}
    for page in PAGES:
        markup = (root / page).read_text(encoding='utf-8')
        if page == 'blog.html': markup = annotate_blog(markup)
        pages[page] = markup
        parsed = Parser(); parsed.feed(markup)
        for node in parsed.root.find(lambda n: 'data-i18n' in n.attrs):
            key, text = node.attrs['data-i18n'], node.text()
            if key in marked and marked[key] != text:
                # Existing shared UI labels can have different raw fallback text;
                # design.js already displays their canonical en.json value.
                if key in english and not key.startswith(('blogTitle','blogPreview','blogCard-')): text = english[key]
                else: raise ValueError('Conflicting English translation key: ' + key)
            if text: marked[key] = text
    english = {key:value for key,value in english.items() if not key.startswith(('blogTitle','blogPreview')) or key in marked}
    english.update(marked)
    return english, pages


def load_cache(root):
    cache = {}
    local = root / '.translation-cache/google-fields.json'
    if local.exists(): cache.update(json.loads(local.read_text(encoding='utf-8')))
    pointer = root / BASE / 'provider-current.json'
    if pointer.exists():
        revision = json.loads(pointer.read_text(encoding='utf-8'))['revision']
        if not re.fullmatch(r'[a-f0-9]{64}', revision): raise ValueError('Invalid provider release pointer')
        release = json.loads((root / BASE / 'releases' / revision / 'provider.json').read_text(encoding='utf-8'))
        cache.update(release['fields'])
    # Authored drafts are intentionally NOT treated as paid Google cache hits.
    return {k: v for k, v in cache.items() if v.get('provider') == 'google' and
            isinstance(v.get('text'), str) and v['text'].strip() and digest(v['source']) == v['source_sha256']}


@contextmanager
def build_lock(root):
    lock = root / '.translation-cache/build.lock'
    lock.parent.mkdir(parents=True, exist_ok=True)
    try: fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError: raise ValueError('Paper Trail translation build already active; do not bypass its lock')
    try:
        with os.fdopen(fd, 'w') as out: out.write(str(os.getpid()))
        yield
    finally: lock.unlink(missing_ok=True)


def run(root=ROOT, mode='dry-run', approve=False, *, offline_translator=None, offline_budget=None):
    root = Path(root).resolve()
    pointer = root / BASE / 'provider-current.json'
    if pointer.exists() and json.loads(pointer.read_text(encoding='utf-8')).get('workflow') == 'whole-site':
        raise ValueError('Use tools/paper-trail-translations.py for the saved whole-site workflow, including Blog updates and chat.')
    if mode not in ('dry-run', 'prepare', 'live', 'mock'): raise ValueError('Invalid mode')
    if mode == 'live' and not approve: raise ValueError('Explicit approval required before any live operation')
    if mode == 'mock' and (root == ROOT.resolve() or offline_translator is None or offline_budget is None):
        raise ValueError('Mock dispatch requires an isolated copy of the real listing')
    if mode != 'mock' and (offline_translator is not None or offline_budget is not None):
        raise ValueError('Offline injection is available only in isolated mock mode')
    if mode == 'dry-run': return build(root, mode)
    with build_lock(root): return build(root, mode, offline_translator, offline_budget)


def build(root, mode, translator=None, budget=None):
    english, pages = sources(root)
    cache = load_cache(root)
    groups = {locale: {} for locale in LOCALES}
    cached = 0
    for key, source in english.items():
        for locale in LOCALES:
            if digest(source) + '|' + locale in cache: cached += 1
            else: groups[locale].setdefault(source, []).append(key)
    counts = {locale: sum(len(s) for s in groups[locale]) for locale in LOCALES}
    total = sum(counts.values())
    missing = sum(len(keys) for group in groups.values() for keys in group.values())
    report = dict(site='paper-trail', mode=mode, source_pages=list(PAGES),
                  source_fields=len(english), cached_fields=cached, missing_fields=missing,
                  characters_per_language=counts, characters_total=total,
                  actual_characters_sent=0, google_calls=0, pending=[], budget_warnings=[])
    if mode != 'mock':
        path = private_path('DOMMYDOM_SHARED_BUDGET_DB', 'shared-usage.sqlite')
        if not path.is_absolute() or path.resolve().is_relative_to(root): raise ValueError('Private shared ledger required')
        budget = ExistingBudget(path, read_only=mode != 'live')
        snapshot = budget.status()['snapshot']
        if not snapshot or snapshot.get('project') != PROJECT: raise ValueError('Existing ledger Google project mismatch or missing baseline')
    quote = budget.quote(total)
    report['budget'] = {k: v for k, v in quote.items() if k not in ('project', 'reservation')}
    def warn(value):
        message = budget_warning(value)
        if message and message not in report['budget_warnings']:
            report['budget_warnings'].append(message)
            print(message, file=sys.stderr)
    warn(quote)
    def pending(locale, texts, reason):
        report['pending'].extend(dict(locale=locale, field=key, reason=reason)
                                 for text in texts for key in groups[locale][text])
    if total and mode in ('live', 'mock'):
        if not quote.get('allowed'): raise ValueError('Shared counter blocked: ' + quote['reason'])
        reservation = budget.reserve('paper-trail', total)
        if not reservation.get('allowed'): raise ValueError('Shared reservation blocked; no Google calls')
        warn(reservation)
        complete = False; partial = False
        try:
            if mode == 'live':
                if reservation.get('project') != PROJECT: raise ValueError('Reserved Google project mismatch')
                if os.environ.get('DOMMYDOM_GOOGLE_PROJECT', PROJECT) != PROJECT: raise ValueError('Environment Google project mismatch')
                token = access_token()
                translator = lambda locale, texts: google_translate(locale, texts, PROJECT, token)
            for locale in LOCALES:
                remaining = list(groups[locale])
                while remaining:
                    chunk = []; chars = 0
                    while remaining and len(chunk) < 50 and chars + len(remaining[0]) <= 25000:
                        text = remaining.pop(0); chunk.append(text); chars += len(text)
                    if not chunk:
                        pending(locale, [remaining.pop(0)], 'Field exceeds provider request limit'); partial = True
                        continue
                    try:
                        if mode == 'live':
                            report['google_calls'] += 1; report['actual_characters_sent'] += chars
                        values = translator(locale, chunk)
                        if len(values) != len(chunk): raise ValueError('Incomplete provider response')
                        for source, text in zip(chunk, values):
                            if not isinstance(text, str) or not text.strip():
                                pending(locale, [source], 'Empty provider response'); partial = True; continue
                            cache[digest(source) + '|' + locale] = dict(provider='google', source=source,
                                source_sha256=digest(source), text=text)
                    except Exception:
                        pending(locale, chunk, 'Provider request failed; no automatic retry'); partial = True
                    # Durable checkpoint BEFORE the next request and outside provider exception handling.
                    atomic(root / '.translation-cache/google-fields.json', encoded(cache))
            complete = True
        finally:
            try: budget.finish(reservation['reservation'], 'uncertain' if not complete else ('partial' if partial else 'complete'))
            except Exception: report['accounting_reconciliation_required'] = True
    else:
        for locale in LOCALES: pending(locale, list(groups[locale]), 'Saved Google translation unavailable; no dispatch in this mode')
    report['pending_fields'] = len(report['pending'])
    if mode != 'dry-run':
        locales = {'en': english}
        for locale in LOCALES:
            drafts = json.loads((root / BASE / (locale + '.json')).read_text(encoding='utf-8'))
            baseline = json.loads((root / BASE / 'en.json').read_text(encoding='utf-8'))
            locales[locale] = {key: cache[digest(source) + '|' + locale]['text'] if digest(source) + '|' + locale in cache
                              else (drafts.get(key, source) if baseline.get(key) == source else source)
                              for key, source in english.items()}
        payload = dict(schema=1, source=english, fields=cache, source_pages=list(PAGES), provider='google')
        revision = digest(json.dumps(payload, sort_keys=True))
        directory = root / BASE / 'releases' / revision
        bundle = ('/* Saved Home/Blog strings. Provider provenance in provider.json; no browser API calls. */\n'
                  'window.PAPER_TRAIL_LOCALES=' + json.dumps(locales, ensure_ascii=True) + ';\n').encode()
        atomic(directory / 'provider.json', encoded(payload))
        atomic(directory / 'current.js', bundle)
        atomic(root / BASE / 'provider-current.json', encoded({'revision': revision}))
        atomic(root / BASE / 'current.js', bundle)
        for page, markup in pages.items():
            markup = re.sub(r'(assets/locales/home-blog/current\.js)(?:\?[^\"\s>]*)?', r'\1?v=' + revision, markup)
            atomic(root / page, markup.encode('utf-8'))
        atomic(root / '.translation-cache/google-fields.json', encoded(cache))
        report['revision'] = revision
        atomic(root / 'verification/shared-translation/latest.json', encoded(report))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('dry-run','prepare','live'), default='dry-run')
    parser.add_argument('--approve-google-calls', action='store_true')
    parser.add_argument('--details', action='store_true', help='Include every pending field in console output')
    args = parser.parse_args()
    try:
        report=run(mode=args.mode, approve=args.approve_google_calls)
        print(json.dumps(report if args.details else {k:v for k,v in report.items() if k!='pending'}, indent=2))
    except Exception as exc:
        print('Paper Trail translation stopped: ' + (str(exc) if isinstance(exc, ValueError) else type(exc).__name__), file=sys.stderr)
        raise SystemExit(1)


if __name__ == '__main__': main()
