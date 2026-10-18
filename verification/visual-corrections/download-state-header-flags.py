"""Download selected, previously researched flag originals for large headers."""
import csv
import hashlib
import json
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'assets/state-flags/headers'
MANIFEST = ROOT / 'verification/visual-corrections/state-header-flag-assets.json'

def validate(data):
    root = ET.fromstring(data)
    assert root.tag == '{http://www.w3.org/2000/svg}svg', 'Not an SVG document'
    for el in root.iter():
        tag = el.tag.rsplit('}', 1)[-1].lower()
        assert tag not in ('script', 'foreignobject'), f'Unsafe SVG element: {tag}'
        for key, value in el.attrib.items():
            name = key.rsplit('}', 1)[-1].lower()
            assert not name.startswith('on'), f'Event handler: {name}'
            if name == 'href':
                assert not value or value.startswith('#') or value.startswith('data:'), f'External reference: {value}'
        if tag == 'style' and el.text:
            assert '@import' not in el.text.lower(), 'External stylesheet'
    import re
    for match in re.finditer(rb'url\(\s*[\'\"]?([^\)\'\"\s]+)', data, re.I):
        assert match.group(1).startswith((b'#', b'data:')), 'External rendered resource'
    return {key: root.attrib.get(key) for key in ('width', 'height', 'viewBox')}

def main():
    DEST.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader((ROOT / 'verification/state-guides/research/flag-sources.csv').open(encoding='utf-8-sig', newline='')))
    assert len(rows) == 50
    result = []
    for row in rows:
        path = DEST / (row['code'].lower() + '.svg')
        selected = ROOT / row['local_file']
        if path.exists():
            data = path.read_bytes()
        elif selected.suffix == '.svg':
            data = selected.read_bytes()
        else:
            for attempt in range(5):
                try:
                    request = urllib.request.Request(row['source_original_url'], headers={'User-Agent': 'PaperTrailFlagAssetPreparation/1.0 (educational state guide website)'})
                    with urllib.request.urlopen(request, timeout=60) as response:
                        data = response.read()
                    break
                except Exception:
                    if attempt == 4:
                        raise
                    time.sleep(3 * (attempt + 1))
        dimensions = validate(data)
        path.write_bytes(data)
        result.append({'code': row['code'], 'state': row['state'], 'header_file': path.relative_to(ROOT).as_posix(), 'source_url': row['source_original_url'], 'source_file_page': row['source_file_page'], 'sha256': hashlib.sha256(data).hexdigest(), 'license': row['license'], 'license_url': row['license_url'], 'attribution': row['attribution'], 'attribution_required': row['attribution_required'], 'license_notes': row['current_design_notes'], 'official_design_crosscheck': row['official_design_crosscheck'], 'source_credit': row['source_credit'], 'copyright_restrictions': row['copyright_restrictions'], 'dimensions': dimensions, 'bytes': len(data)})
        MANIFEST.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        print(f"{row['code']}: {len(data)} bytes, validated", flush=True)
    print(f'Complete: {len(result)} validated SVG headers', flush=True)

if __name__ == '__main__':
    main()
