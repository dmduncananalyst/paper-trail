"""Offline integration: real page copies, isolated ledger fixtures, no Google."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import time
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('paper_translation', Path(__file__).with_name('translate-home-blog.py'))
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)
from translation_pipeline.budget import Budget, ExistingBudget


class Integration(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='paper-trail-offline-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'site'
        for name in ['index.html','blog.html','notes.html','catch-up-bookkeeping-overdue-books.html']:
            target = self.root / name; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(runner.ROOT / name, target)
        shutil.copytree(runner.ROOT / runner.BASE, self.root / runner.BASE)
        self.budget = Budget(Path(self.temp.name) / 'OFFLINE-FIXTURE.sqlite')
        now = time.time()
        self.budget.reconcile(dict(mode='shared-counter', project=runner.PROJECT,
            period_start=now-15*86400, period_end=now+15*86400, approved_at=now,
            opening_characters=500000, all_jobs_use_counter=True,
            report_reference='OFFLINE fixture only', included_reservations=[],
            price_per_million='20', soft_usd='12', hard_usd='15'))
        self.calls = []
        self.no_network = patch.object(runner, 'google_translate', side_effect=AssertionError('Google forbidden'))
        self.no_network.start(); self.addCleanup(self.no_network.stop)
        self.no_auth = patch.object(runner, 'access_token', side_effect=AssertionError('OAuth forbidden'))
        self.no_auth.start(); self.addCleanup(self.no_auth.stop)
        self.original = {name: (self.root / name).read_bytes() for name in ('notes.html','catch-up-bookkeeping-overdue-books.html')}

    def tearDown(self):
        for name, original in self.original.items(): self.assertEqual((self.root / name).read_bytes(), original)

    def translate(self, locale, texts):
        state = self.budget.status()['reservations']
        self.assertEqual(state[-1]['site'], 'paper-trail')
        self.assertEqual(state[-1]['result'], 'reserved')
        self.calls.append((locale, list(texts)))
        return ['OFFLINE ' + locale + ': ' + text for text in texts]

    def build(self, translator=None):
        return runner.run(self.root, 'mock', offline_translator=translator or self.translate, offline_budget=self.budget)

    def test_one_shared_counter_reserves_actual_characters_before_dispatch(self):
        other = self.budget.reserve('dommydom', 2610)
        self.budget.finish(other['reservation'], 'complete')
        source, _ = runner.sources(self.root)
        expected = sum(len(text) for text in set(source.values())) * 9
        report = self.build()
        self.assertEqual(report['characters_total'], expected)
        records = self.budget.status()['reservations']
        self.assertEqual([(r['site'], r['chars']) for r in records], [('dommydom',2610),('paper-trail',expected)])
        self.assertEqual(records[-1]['result'], 'complete')
        self.assertEqual(sum(len(text) for _, texts in self.calls for text in texts), expected)
        self.assertEqual(report['source_pages'], ['index.html','blog.html'])

    def test_permanent_release_reuses_every_google_response(self):
        first = self.build(); self.calls.clear()
        second = self.build()
        self.assertEqual(second['characters_total'], 0)
        self.assertEqual(first['revision'], second['revision'])
        self.assertEqual(self.calls, [])
        shutil.rmtree(self.root / '.translation-cache')
        third = self.build()
        self.assertEqual(third['characters_total'], 0)
        self.assertEqual(self.calls, [])
        self.assertEqual(len(self.budget.status()['reservations']), 1)

    def test_drafts_are_not_claimed_as_google_cache(self):
        self.assertEqual(runner.load_cache(self.root), {})
        report = self.build()
        self.assertEqual(report['cached_fields'], 0)
        self.assertTrue(self.calls)
        self.assertEqual(json.loads((self.root / runner.BASE / 'manifest.json').read_text())['provider'], 'none')

    def test_later_failure_preserves_first_response_and_retries_only_missing(self):
        attempted = []; failed = []
        def partial(locale, texts):
            attempted.append(1)
            if len(attempted) == 2:
                self.assertTrue((self.root / '.translation-cache/google-fields.json').exists())
                failed.extend((locale, text) for text in texts)
                raise TimeoutError('Offline failure')
            return self.translate(locale, texts)
        report = self.build(partial)
        self.assertGreater(report['pending_fields'], 0)
        self.assertEqual(self.budget.status()['reservations'][-1]['result'], 'partial')
        self.calls.clear(); self.build()
        self.assertEqual([(locale,text) for locale,texts in self.calls for text in texts], failed)

    def test_interruption_keeps_checkpoint_and_conservative_reservation(self):
        completed = []
        def interrupted(locale, texts):
            if completed: raise KeyboardInterrupt('Offline interruption')
            completed.extend((locale,text) for text in texts)
            return self.translate(locale,texts)
        with self.assertRaises(KeyboardInterrupt): self.build(interrupted)
        self.assertEqual(self.budget.status()['reservations'][-1]['result'],'uncertain')
        self.calls.clear(); self.build()
        retried = {(locale,text) for locale,texts in self.calls for text in texts}
        self.assertFalse(set(completed) & retried)

    def test_changed_real_blog_card_is_automatically_detected_and_saved(self):
        self.build(); self.calls.clear()
        source, _ = runner.sources(self.root)
        old = source['blogTitle0']; changed = old + ' (updated)'
        page = self.root / 'blog.html'; page.write_text(page.read_text(encoding='utf-8').replace(old, changed),encoding='utf-8')
        report = self.build()
        self.assertEqual(report['characters_total'], len(changed)*9)
        self.assertEqual(self.calls, [(locale,[changed]) for locale in runner.LOCALES])
        self.calls.clear(); self.build(); self.assertEqual(self.calls, [])

    def test_future_unmarked_card_fields_get_stable_translation_keys(self):
        # Remove attributes on an EXISTING real card; do not invent test articles.
        page = self.root / 'blog.html'
        text = page.read_text(encoding='utf-8').replace(' data-i18n="blogTitle0"','').replace(' data-i18n="blogPreview0"','')
        page.write_text(text,encoding='utf-8')
        source, pages = runner.sources(self.root)
        self.assertTrue(any(key.startswith('blogCard-') and key.endswith('-title') for key in source))
        self.assertTrue(any(key.startswith('blogCard-') and key.endswith('-preview') for key in source))
        self.assertEqual(pages['blog.html'].count('<article'), text.count('<article'))

    def test_saved_bundle_contains_all_nine_languages_and_keeps_time_elements(self):
        original = (self.root / 'blog.html').read_text(encoding='utf-8')
        self.build()
        text = (self.root / runner.BASE / 'current.js').read_text(encoding='utf-8')
        locales = json.loads(text.split('window.PAPER_TRAIL_LOCALES=',1)[1].strip().rstrip(';'))
        self.assertEqual(set(locales), {'en', *runner.LOCALES})
        for locale in runner.LOCALES:
            for field in ('blogTitle0','blogPreview0'):
                self.assertTrue(locales[locale][field].startswith('OFFLINE '+locale+': '))
        generated = (self.root / 'blog.html').read_text(encoding='utf-8')
        self.assertEqual(original.count('<time '), generated.count('<time '))
        self.assertEqual(original.count('<img '), generated.count('<img '))

    def test_wrong_project_blocks_live_before_authentication_or_reservation(self):
        snapshot = self.budget.status()['snapshot']; snapshot['project'] = 'OFFLINE-WRONG-PROJECT'
        with self.budget.db() as connection:
            connection.execute('UPDATE snapshot SET data=? WHERE id=1',(json.dumps(snapshot),))
        with patch.dict('os.environ', {'DOMMYDOM_SHARED_BUDGET_DB':self.budget.path}):
            with self.assertRaises(ValueError): runner.run(self.root, 'live', approve=True)
        self.assertEqual(self.budget.status()['reservations'], [])
        runner.access_token.assert_not_called()

    def test_live_requires_explicit_approval_without_auth_or_budget_mutation(self):
        before = Path(self.budget.path).read_bytes()
        with self.assertRaises(ValueError): runner.run(self.root, 'live')
        self.assertEqual(Path(self.budget.path).read_bytes(), before)
        runner.access_token.assert_not_called()

    def test_readonly_connection_cannot_change_fixture_or_create_missing_db(self):
        path = Path(self.budget.path); before = path.read_bytes()
        with patch.dict('os.environ', {'DOMMYDOM_SHARED_BUDGET_DB':str(path)}):
            report = runner.counter_connection(self.root)
        self.assertTrue(report['connected']); self.assertTrue(report['project_matches'])
        self.assertEqual(path.read_bytes(), before)
        missing = path.with_name('MISSING.sqlite')
        with self.assertRaises(FileNotFoundError): ExistingBudget(missing)
        self.assertFalse(missing.exists())

    def test_budget_block_prevents_provider_and_preserves_reservations(self):
        snapshot = self.budget.status()['snapshot']; snapshot['all_jobs_use_counter'] = False
        with self.budget.db() as connection:
            connection.execute('UPDATE snapshot SET data=? WHERE id=1',(json.dumps(snapshot),))
        with self.assertRaises(ValueError): self.build()
        self.assertEqual(self.calls, [])
        self.assertEqual(self.budget.status()['reservations'], [])


if __name__ == '__main__': unittest.main(verbosity=2)
