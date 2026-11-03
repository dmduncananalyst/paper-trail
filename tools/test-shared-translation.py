"""Current whole-site integration: real page copies, temporary ledgers, no network."""
import importlib.util
from contextlib import closing
import io
import json
from pathlib import Path
import re
import shutil
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
SPEC = importlib.util.spec_from_file_location('paper_translation', TOOLS / 'paper-trail-translations.py')
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)
LEGACY_SPEC = importlib.util.spec_from_file_location('legacy_paper_translation', TOOLS / 'translate-home-blog.py')
legacy = importlib.util.module_from_spec(LEGACY_SPEC)
LEGACY_SPEC.loader.exec_module(legacy)
from translation_pipeline import pipeline
from translation_pipeline.budget import Budget, ExistingBudget


class Integration(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='paper-trail-offline-')
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.root = self.directory / 'site'
        original = runner.ROOT
        self.repository_files = {
            name: (original / name).read_bytes()
            for name in ('index.html', 'blog.html', 'notes.html', 'catch-up-bookkeeping-overdue-books.html')
        }
        self.addCleanup(self.assert_repository_unchanged, original)
        for name in ('index.html', 'blog.html'):
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(self.repository_files[name])
        # Unrelated copies are outside the whole-site source scanner's two roots.
        for name in ('notes.html', 'catch-up-bookkeeping-overdue-books.html'):
            target = self.root / 'preserved' / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(self.repository_files[name])
        self.ui_base = Path('assets/locales/home-blog')
        original_ui = json.loads((original / self.ui_base / 'en.json').read_text(encoding='utf-8'))
        self.ui = dict(list(original_ui.items())[:4])
        self.ui['fixtureBlogTitle'] = self.blog_title()
        self.write_json(self.ui_base / 'en.json', self.ui)
        self.write_json(self.ui_base / 'chat.json', {'en': {}})
        self.write_json(self.ui_base / 'manifest.json', {'provider': 'none', 'status': 'Offline fixture'})
        for locale in runner.LOCALES:
            self.write_json(self.ui_base / (locale + '.json'), {k: 'AUTHORED DRAFT ' + v for k, v in self.ui.items()})
        self.write_json('tools/production-pages.json', {
            'english': ['index.html', 'blog.html'],
            'locales': {locale: [] for locale in runner.LOCALES},
        })
        for name, value in {
            'ROOT': self.root,
            'CACHE': self.root / '.translation-cache/google-site-fields.json',
            'RECEIPTS': self.root / '.translation-cache/provider-responses',
            'OUT': self.directory / 'reports',
        }.items():
            self.enterContext(patch.object(runner, name, value))
        self.budget = Budget(self.directory / 'accounting.sqlite')
        self.budget.reconcile({'project': runner.PROJECT, 'all_jobs_use_counter': True})
        self.request_db = self.directory / 'requests.sqlite3'
        self.enterContext(patch.dict('os.environ', {
            'DOMMYDOM_SHARED_BUDGET_DB': self.budget.path,
            'DOMMYDOM_TRANSLATION_REQUEST_DB': str(self.request_db),
        }))
        self.auth = self.enterContext(patch.object(runner, 'access_token', return_value='OFFLINE-TEST-TOKEN'))
        self.preflight_http = self.enterContext(patch.object(runner, 'urlopen', side_effect=self.preflight_response))
        self.opener = self.enterContext(patch.object(pipeline, 'build_opener'))
        self.provider_http = self.opener.return_value.open
        self.provider_http.side_effect = self.provider_response
        # Any network path outside these explicit mocks is a test failure.
        self.enterContext(patch('socket.create_connection', side_effect=AssertionError('Network forbidden')))
        self.calls = []
        self.provider_override = None

    def assert_repository_unchanged(self, original):
        for name, content in self.repository_files.items():
            self.assertEqual((original / name).read_bytes(), content)

    def tearDown(self):
        for name in ('notes.html', 'catch-up-bookkeeping-overdue-books.html'):
            self.assertEqual((self.root / 'preserved' / name).read_bytes(), self.repository_files[name])

    def write_json(self, path, value):
        runner.atomic(self.root / path, runner.encoded(value))

    def blog_title(self):
        markup = (self.root / 'blog.html').read_text(encoding='utf-8')
        card = re.search(r'<article\b[^>]*class="[^"]*\bblog-story\b[^"]*"[^>]*>.*?</article>', markup, re.S)
        self.assertIsNotNone(card)
        heading = re.search(r'<h2\b[^>]*>.*?</h2>', card[0], re.S)
        self.assertIsNotNone(heading)
        # Use the real translatable title span; retain its styled numeric prefix.
        return next(slot['source'] for slot in runner.Inventory(heading[0]).slots if slot['kind'] == 'text')

    def preflight_response(self, request, timeout):
        url = request.full_url
        self.assertIn(runner.PROJECT, url)
        if url.startswith('https://serviceusage.googleapis.com/'):
            value = {'state': 'ENABLED'}
        elif url.startswith('https://cloudresourcemanager.googleapis.com/'):
            value = {'permissions': ['serviceusage.services.use']}
        elif url.startswith('https://cloudbilling.googleapis.com/'):
            value = {'billingEnabled': True}
        else:
            self.fail('Unexpected preflight network destination')
        return io.BytesIO(json.dumps(value).encode())

    def provider_response(self, request, timeout):
        self.assertEqual(request.full_url, 'https://translation.googleapis.com/v3/projects/' + runner.PROJECT + '/locations/global:translateText')
        payload = json.loads(request.data)
        locale = payload['targetLanguageCode']
        sources = [''.join(pipeline.PlainResult(value).parts) for value in payload['contents']]
        reservation = self.budget.status()['reservations'][-1]
        self.assertEqual(reservation['site'], 'paper-trail')
        self.assertEqual(reservation['result'], 'reserved')
        self.assertEqual(reservation['chars'], sum(map(len, sources)))
        self.calls.append((locale, sources))
        if self.provider_override:
            self.provider_override(locale, sources)
        return io.BytesIO(json.dumps({'translations': [
            {'translatedText': 'OFFLINE ' + locale + ': ' + value} for value in payload['contents']
        ]}).encode())

    def build(self, approve=True):
        return runner.run('refresh', approve=approve)

    def seed_except(self, missing):
        _, sources, _, _, _ = runner.inventory()
        fields = {
            runner.key(source, locale): {'source': source, 'locale': locale,
                'text': 'OFFLINE ' + locale + ': ' + source, 'provider': 'google'}
            for locale in runner.LOCALES for source in sources if (locale, source) not in missing
        }
        runner.atomic(runner.CACHE, runner.encoded(fields))

    def test_one_shared_counter_reserves_actual_characters_before_dispatch(self):
        other = self.budget.reserve('dommydom', 2610)
        self.budget.finish(other['reservation'], 'complete')
        expected = runner.inventory()[-1]['candidate_characters']
        report = self.build()
        self.assertEqual(report['actual_characters_sent'], expected)
        records = self.budget.status()['reservations']
        self.assertEqual((records[0]['site'], records[0]['chars']), ('dommydom', 2610))
        self.assertTrue(all(r['site'] == 'paper-trail' and r['result'] == 'complete' for r in records[1:]))
        self.assertEqual(sum(r['chars'] for r in records[1:]), expected)
        self.assertEqual(sum(len(text) for _, texts in self.calls for text in texts), expected)
        self.assertEqual(set(report['source_fingerprints']), {'index.html', 'blog.html'})
        self.assertTrue(report['rendered'])

    def test_permanent_release_reuses_every_google_response(self):
        first = self.build()
        self.calls.clear()
        count = len(self.budget.status()['reservations'])
        second = self.build()
        self.assertEqual(second['candidate_characters'], 0)
        self.assertEqual(first['revision'], second['revision'])
        self.assertEqual(self.calls, [])
        shutil.rmtree(self.root / '.translation-cache')
        third = self.build()
        self.assertEqual(third['candidate_characters'], 0)
        self.assertEqual(self.calls, [])
        self.assertEqual(len(self.budget.status()['reservations']), count)
        release = self.root / runner.BASE / 'releases' / first['revision'] / 'fields.json'
        self.assertEqual(json.loads(release.read_text(encoding='utf-8'))['provider'], 'google')

    def test_drafts_are_not_claimed_as_google_cache(self):
        self.assertEqual(runner.load_cache(), {})
        self.assertEqual(json.loads((self.root / self.ui_base / 'manifest.json').read_text())['provider'], 'none')
        report = self.build()
        self.assertTrue(self.calls)
        self.assertEqual(report['pending_fields'], 0)
        self.assertTrue(all(v['text'].startswith('OFFLINE ') for v in runner.load_cache().values()))

    def test_later_failure_preserves_first_response_and_retries_only_missing(self):
        source = self.blog_title()
        self.seed_except({(locale, source) for locale in ('es', 'fa', 'hy')})
        def fail_second(locale, sources):
            if locale == 'fa':
                self.assertTrue(list(runner.RECEIPTS.glob('*.json')))
                raise TimeoutError('Offline uncertain response')
        self.provider_override = fail_second
        report = self.build()
        self.assertGreater(report['pending_fields'], 0)
        self.assertFalse(report['rendered'])
        self.assertEqual([r['result'] for r in self.budget.status()['reservations']], ['complete', 'uncertain'])
        self.assertIn(runner.key(source, 'es'), runner.load_cache())
        self.provider_override = None
        self.calls.clear()
        blocked = self.build()
        self.assertEqual(self.calls, [])  # Unknown outcomes must never be resent.
        self.assertFalse(blocked['rendered'])
        # Fixture-only reconciliation supplies a known response, never a retry.
        with closing(sqlite3.connect(self.request_db)) as connection:
            with connection:
                connection.execute("UPDATE requests SET status='complete',response=? WHERE locale='fa' AND status='uncertain'",
                    (json.dumps(['OFFLINE fa: ' + source]),))
        self.calls.clear()
        recovered = self.build()
        self.assertTrue(recovered['rendered'])
        self.assertEqual(self.calls, [('hy', [source])])

    def test_interruption_keeps_checkpoint_and_conservative_reservation(self):
        source = self.blog_title()
        self.seed_except({('es', source)})
        atomic = runner.atomic
        def power_loss(path, data):
            atomic(path, data)
            if Path(path).parent == runner.RECEIPTS:
                raise KeyboardInterrupt('Offline interruption after durable receipt')
        with patch.object(runner, 'atomic', side_effect=power_loss):
            with self.assertRaises(KeyboardInterrupt):
                self.build()
        self.assertEqual(self.budget.status()['reservations'][-1]['result'], 'uncertain')
        self.assertIn(runner.key(source, 'es'), runner.load_cache())
        self.calls.clear()
        recovered = self.build()
        self.assertTrue(recovered['rendered'])
        self.assertEqual(self.calls, [])
        self.assertEqual(len(self.budget.status()['reservations']), 1)
        self.assertEqual(self.budget.status()['reservations'][0]['result'], 'uncertain')

    def test_changed_real_blog_card_is_automatically_detected_and_saved(self):
        self.build()
        self.calls.clear()
        old = self.blog_title()
        changed = old + ' (updated)'
        page = self.root / 'blog.html'
        page.write_text(page.read_text(encoding='utf-8').replace(old, changed), encoding='utf-8')
        report = self.build()
        self.assertEqual(report['actual_characters_sent'], len(changed) * 9)
        self.assertEqual(self.calls, [(locale, [changed]) for locale in runner.LOCALES])
        self.calls.clear()
        self.build()
        self.assertEqual(self.calls, [])

    def test_future_unmarked_card_fields_get_stable_translation_keys(self):
        page = self.root / 'blog.html'
        original = page.read_text(encoding='utf-8')
        unmarked = re.sub(r'\sdata-i18n="[^"]*"', '', original)
        page.write_text(unmarked, encoding='utf-8')
        pages, sources, _, _, _ = runner.inventory()
        title = self.blog_title()
        self.assertIn(title, sources)
        self.assertEqual(pages['blog.html'].markup.count('<article'), original.count('<article'))
        self.build()
        self.assertTrue(all(runner.key(title, locale) in runner.load_cache() for locale in runner.LOCALES))
        self.calls.clear()
        self.build()
        self.assertEqual(self.calls, [])

    def test_saved_bundle_contains_all_nine_languages_and_keeps_time_elements(self):
        original = (self.root / 'blog.html').read_text(encoding='utf-8')
        self.build()
        text = (self.root / self.ui_base / 'current.js').read_text(encoding='utf-8')
        ui = json.loads(text.split('window.PAPER_TRAIL_LOCALES=', 1)[1].split(';\nwindow.PAPER_TRAIL_CHAT_LOCALES=', 1)[0])
        self.assertEqual(set(ui), {'en', *runner.LOCALES})
        for locale in runner.LOCALES:
            self.assertTrue(ui[locale]['fixtureBlogTitle'].startswith('OFFLINE ' + locale + ': '))
            localized = (self.root / locale / 'blog.html').read_text(encoding='utf-8')
            self.assertEqual(localized.count('<time '), original.count('<time '))
            self.assertEqual(localized.count('<img '), original.count('<img ') + 1)  # Existing Google attribution.
        generated = (self.root / 'blog.html').read_text(encoding='utf-8')
        self.assertEqual(original.count('<time '), generated.count('<time '))
        self.assertEqual(original.count('<img '), generated.count('<img '))

    def test_wrong_project_blocks_live_before_authentication_or_reservation(self):
        with self.budget.db() as connection:
            connection.execute('UPDATE snapshot SET data=? WHERE id=1',
                (json.dumps({'project': 'OFFLINE-WRONG-PROJECT', 'all_jobs_use_counter': True}),))
        with self.assertRaisesRegex(ValueError, 'Google project mismatch'):
            self.build()
        self.assertEqual(self.budget.status()['reservations'], [])
        self.auth.assert_not_called()
        self.preflight_http.assert_not_called()
        self.provider_http.assert_not_called()

    def test_live_requires_explicit_approval_without_auth_or_budget_mutation(self):
        before = Path(self.budget.path).read_bytes()
        with self.assertRaisesRegex(ValueError, 'Explicit live approval required'):
            self.build(approve=False)
        self.assertEqual(Path(self.budget.path).read_bytes(), before)
        self.auth.assert_not_called()
        self.provider_http.assert_not_called()

    def test_readonly_connection_cannot_change_fixture_or_create_missing_db(self):
        path = Path(self.budget.path)
        before = path.read_bytes()
        read_only = ExistingBudget(path, read_only=True)
        self.assertEqual(read_only.status()['snapshot']['project'], runner.PROJECT)
        with self.assertRaises(sqlite3.OperationalError):
            with read_only.db() as connection:
                connection.execute('DELETE FROM snapshot')
        self.assertEqual(path.read_bytes(), before)
        missing = path.with_name('MISSING.sqlite')
        with self.assertRaises(FileNotFoundError):
            ExistingBudget(missing)
        self.assertFalse(missing.exists())

    def test_budget_block_prevents_provider_and_preserves_reservations(self):
        with self.budget.db() as connection:
            connection.execute('UPDATE snapshot SET data=? WHERE id=1',
                (json.dumps({'project': runner.PROJECT, 'all_jobs_use_counter': False}),))
        with self.assertRaisesRegex(ValueError, 'Shared accounting configuration requires review'):
            self.build()
        self.assertEqual(self.calls, [])
        self.assertEqual(self.budget.status()['reservations'], [])
        self.auth.assert_not_called()
        self.preflight_http.assert_not_called()
        self.provider_http.assert_not_called()

    def test_legacy_runner_rejects_whole_site_workflow_pointer(self):
        self.write_json(self.ui_base / 'provider-current.json', {
            'workflow': 'whole-site', 'provider': 'google', 'revision': 'a' * 64,
        })
        with patch.object(legacy, 'access_token', side_effect=AssertionError('Authentication forbidden')) as auth:
            with patch.object(legacy, 'google_translate', side_effect=AssertionError('Provider forbidden')) as provider:
                with self.assertRaisesRegex(ValueError, 'Use tools/paper-trail-translations.py'):
                    legacy.run(self.root, 'mock', offline_translator=lambda *_: self.fail('Legacy dispatch'), offline_budget=self.budget)
                auth.assert_not_called()
                provider.assert_not_called()
        self.assertEqual(self.budget.status()['reservations'], [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
