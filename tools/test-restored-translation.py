"""Offline restoration checks: no credentials, network, HubSpot or repository outputs."""
from pathlib import Path
from unittest.mock import patch
import importlib.util
import json
import os
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent / 'sun-and-sage/scripts'))
from translation_pipeline import pipeline, workflow
from translation_pipeline.budget import Budget, ExistingBudget
from translation_pipeline.connection import private_path

spec = importlib.util.spec_from_file_location('restored_runner', ROOT / 'tools/paper-trail-translations.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

class Restoration(unittest.TestCase):
    def test_lossless_html_spans_and_technical_fields(self):
        source = '<script>nativeSubmit("0-1/message")</script><select id="language"><option>English</option></select><select name="assessment"><option value="one">One answer</option></select><input name="technical" aria-label="Your name"><p> A &amp; B </p>'
        inv = runner.Inventory(source)
        self.assertEqual([s['source'] for s in inv.slots], ['One answer', 'Your name', 'A & B'])
        rendered = workflow.apply_edits(source, [(s['start'], s['end'], 'Traducido') for s in inv.slots])
        self.assertIn('nativeSubmit("0-1/message")', rendered)
        self.assertIn('value="one"', rendered)
        self.assertIn('<option>English</option>', rendered)
        self.assertIn('name="technical"', rendered)

    def test_saved_sources_only_and_no_network_inventory(self):
        with patch.object(runner, 'google_translate', side_effect=AssertionError('Offline')), patch.object(runner, 'access_token', side_effect=AssertionError('Offline')):
            pages, refs, fields, missing, report = runner.inventory()
            self.assertEqual(len(pages), 210)
            for locale, sources in missing.items():
                self.assertTrue(all(runner.key(s, locale) not in fields for s in sources))
                self.assertEqual(len(sources), len(set(sources)))
            self.assertGreater(len(fields), 30000)
            self.assertEqual(report['google_calls'], 0)
            self.assertEqual(report['candidate_fields'], sum(map(len, missing.values())))

    def test_provider_reserved_before_call_and_uncertainty_blocks_retry(self):
        with tempfile.TemporaryDirectory(prefix='paper-translation-unit-') as tmp:
            with patch.dict(os.environ, {'DOMMYDOM_TRANSLATION_REQUEST_DB': str(Path(tmp) / 'requests.sqlite')}):
                with patch.object(pipeline, 'build_opener') as opener:
                    opener.return_value.open.side_effect = TimeoutError()
                    with self.assertRaisesRegex(RuntimeError, 'not retried'):
                        pipeline.google_translate('es', ['New approved text'], runner.PROJECT, 'OFFLINE')
                    with self.assertRaisesRegex(RuntimeError, 'uncertain'):
                        pipeline.google_translate('es', ['New approved text'], runner.PROJECT, 'OFFLINE')
                    self.assertEqual(opener.return_value.open.call_count, 1)

    def test_successful_response_reused_without_second_request(self):
        with tempfile.TemporaryDirectory(prefix='paper-translation-unit-') as tmp:
            with patch.dict(os.environ, {'DOMMYDOM_TRANSLATION_REQUEST_DB': str(Path(tmp) / 'requests.sqlite')}):
                with patch.object(pipeline, 'build_opener') as opener:
                    response = opener.return_value.open.return_value.__enter__.return_value
                    response.read.return_value = json.dumps({'translations':[{'translatedText':'Texto nuevo de Paper Trail por $350'}]}).encode()
                    for _ in range(2):
                        self.assertEqual(pipeline.google_translate('es', ['New Paper Trail text for $350'], runner.PROJECT, 'OFFLINE'), ['Texto nuevo de Paper Trail por $350'])
                    self.assertEqual(opener.return_value.open.call_count, 1)

    def test_no_custom_cap_or_historical_balance_reset(self):
        with tempfile.TemporaryDirectory(prefix='paper-translation-unit-') as tmp:
            budget = Budget(Path(tmp) / 'usage.sqlite')
            self.assertTrue(budget.quote(50000000)['allowed'])
            self.assertIsNone(budget.status()['snapshot'])
            self.assertIsNone(pipeline.budget_warning(budget.quote(50000000)))
            budget.reserve('dommydom', 100)
            budget.reserve('paper-trail', 200)
            self.assertEqual(sum(r['chars'] for r in budget.status()['reservations']), 300)
            self.assertEqual(len(ExistingBudget(budget.path, read_only=True).status()['reservations']), 2)

    def test_private_paths_reject_repository_and_relative_paths(self):
        for target in ['relative.sqlite', str(ROOT / '.translation-cache/shared.sqlite')]:
            with patch.dict(os.environ, {'OFFLINE_LEDGER':target}):
                with self.assertRaises(ValueError): private_path('OFFLINE_LEDGER', 'shared.sqlite')

    def test_protected_brands_numbers_and_rtl_scoping(self):
        source = 'Paper Trail: $1,050; QuickBooks and https://example.org/ 500 entries'
        protected = pipeline.protected_html(source)
        self.assertIn('<span translate="no">Paper Trail</span>', protected)
        self.assertIn('<span translate="no">$1,050</span>', protected)
        css = (ROOT / 'assets/translation-workflow/display.css').read_text()
        self.assertIn('[data-static-locale="ar"]', css)
        self.assertIn('[data-static-locale="fa"]', css)
        self.assertIn('unicode-bidi:isolate', css)

if __name__ == '__main__':
    unittest.main(verbosity=2)
