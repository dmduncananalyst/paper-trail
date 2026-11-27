"""Verify the approved Fitness subtree before packaging its localized pages."""
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
from source_section_policy import Document

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://www.papertrailusa.com/'
LANDING = 'fitness-bookkeeping.html'
DETAILS = ['pilates-studio-bookkeeping.html', 'yoga-studio-bookkeeping.html', 'gym-bookkeeping.html']


def sitemap(name):
    return {node.text for node in ET.parse(ROOT / name).iter() if node.tag.endswith('}loc')}


def main():
    inventory = json.loads((ROOT / 'tools/production-pages.json').read_text(encoding='utf-8'))
    translation = json.loads((ROOT / 'assets/translation-workflow/current.json').read_text(encoding='utf-8'))
    languages = list(translation['routes'])
    if len(languages) != 9 or set(languages) != set(inventory['locales']):
        raise SystemExit('Fitness locale inventory differs from the approved website configuration')
    for locale in ['', *languages]:
        prefix = locale + '/' if locale else ''
        public = inventory['locales'][locale] if locale else inventory['english']
        indexed = sitemap('sitemap-translations.xml' if locale else 'sitemap.xml')
        routes = translation['routes'].get(locale, public)
        for name in [LANDING, *DETAILS]:
            markup = (ROOT / prefix / name).read_text(encoding='utf-8')
            nodes = Document(markup).nodes
            metadata = [n['attrs'] for n in nodes if n['tag'] in {'link', 'meta'}]
            canonical = ORIGIN + prefix + name
            if name not in public or name not in routes or canonical not in indexed:
                raise SystemExit(f'Fitness route missing from an inventory: {prefix}{name}')
            if [a.get('href') for a in metadata if a.get('rel') == 'canonical'] != [canonical]:
                raise SystemExit(f'Incorrect Fitness canonical: {prefix}{name}')
            alternates = {a['hreflang']: a.get('href') for a in metadata if a.get('rel') == 'alternate' and 'hreflang' in a}
            expected = {lang: ORIGIN + lang + '/' + name for lang in languages}
            expected.update({'en': ORIGIN + name, 'x-default': ORIGIN + name})
            if alternates != expected:
                raise SystemExit(f'Incorrect Fitness alternates: {prefix}{name}')
            if name == LANDING:
                cards = [n['attrs']['href'] for n in nodes if n['tag'] == 'a' and 'named-service' in n['attrs'].get('class', '').split()]
                if [urlsplit(card).path.lstrip('/') for card in cards] != [prefix + route for route in DETAILS]:
                    raise SystemExit(f'Incorrect Fitness card links: {prefix}{name}')
            elif not any(a.get('name') == 'description' and a.get('content') for a in metadata):
                raise SystemExit(f'Missing Fitness description: {prefix}{name}')
    print('Fitness release check passed: 4 English pages and 36 localized versions (27 new).')


if __name__ == '__main__':
    main()
