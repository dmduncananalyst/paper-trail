"""Extend the existing counter's initial-work classification, without resets."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[1]
shared=root.parent/'sun-and-sage/scripts/translation_pipeline/budget.py'
out=root/'verification/google-translation-20261016';out.mkdir(parents=True,exist_ok=True)
before=shared.read_bytes();old="if allocation.get('purpose')!='initial-dommydom' or allocation.get('project')!=s['project']:raise ValueError('Unknown funding classification')"
new="if allocation.get('purpose') not in ('initial-dommydom','initial-paper-trail') or allocation.get('project')!=s['project']:raise ValueError('Unknown funding classification')"
text=before.decode('utf-8')
if new not in text:
    assert text.count(old)==1,'Shared counter changed, inspect before editing'
    (out/'shared-budget.py.before.txt').write_bytes(before)
    shared.write_bytes(text.replace(old,new).encode('utf-8'))
print(json.dumps({'extended_initial_classification':True,'ongoing_thresholds_unchanged':True,'ledger_reset':False}))
