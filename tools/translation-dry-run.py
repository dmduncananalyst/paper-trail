"""Offline translation inventory. Contains no provider dispatch or ledger writes."""
from pathlib import Path
from decimal import Decimal
import argparse,hashlib,json,os,importlib.util

spec=importlib.util.spec_from_file_location('shared_translation',Path(__file__).with_name('translate-home-blog.py'))
shared_translation=importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared_translation)

ROOT=Path(__file__).resolve().parents[1]
LANGUAGES=('es','fa','hy','zh-CN','ko','tl','te','ru','ar')
POLICY={'monthly_workflow_ceiling_usd':'15','early_warning_usd':'12','live_enabled':False,
        'live_calls_approved':False,'shared_ledger_verified':False,
        'scope':['dommydom','paper-trail','startweb7'],'planning_english_characters_per_card':350}

def inspect():
    pointer=ROOT/'assets/locales/home-blog/provider-current.json'
    if pointer.exists() and json.loads(pointer.read_text(encoding='utf-8')).get('workflow')=='whole-site':
        spec=importlib.util.spec_from_file_location('saved_whole_site',Path(__file__).with_name('paper-trail-translations.py'))
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        _,_,_,_,report=module.inventory()
        manifest=json.loads((ROOT/'assets/locales/home-blog/manifest.json').read_text(encoding='utf-8'))
        saved=ROOT/'assets/translation-workflow/releases'/manifest['revision']/'fields.json'
        return {'mode':'offline_only','workflow':'whole-site','provenance':'Saved Google translations; native speaker review pending',
                'source_pages':report['pages'],'target_languages':len(LANGUAGES),
                'saved_bundle_sha256':hashlib.sha256(saved.read_bytes()).hexdigest(),
                'verified_google_cache_fields':report['source_strings']*len(LANGUAGES)-report['candidate_fields'],
                'pending_fields':report['candidate_fields'],'pending_characters':report['candidate_characters'],
                'google_requests':0,'characters_dispatched_to_google':0,
                'historical_google_requests':manifest['google_calls'],
                'historical_google_characters':manifest['google_characters_sent'],
                'translation_runner':'tools/paper-trail-translations.py',
                'note':'Read only audit. No provider dispatch, ledger writes, or publishing.'}
    connection=shared_translation.counter_connection()
    folder=ROOT/'assets/locales/home-blog'
    manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    english=json.loads((folder/'en.json').read_text(encoding='utf-8'))
    missing=[];mismatched=[];draft_hits=0
    for code in LANGUAGES:
        target=json.loads((folder/(code+'.json')).read_text(encoding='utf-8'))
        for key,value in english.items():
            expected=hashlib.sha256(value.encode('utf-8')).hexdigest()
            if manifest['fields'][key]['source_sha256']!=expected:mismatched.append({'language':code,'key':key})
            elif not target.get(key):missing.append({'language':code,'key':key,'characters':len(value)})
            else:draft_hits+=1
    unique_sources=set(english.values())
    if_all_sources_required_google=sum(len(s) for s in unique_sources)*len(LANGUAGES)
    blog_sources=set(v for k,v in english.items() if k.startswith(('blogTitle','blogPreview')))
    blog_chars=sum(len(s) for s in blog_sources)*len(LANGUAGES)
    planned=12*350*9*30
    estimate=Decimal(max(0,planned-500000))*Decimal('20')/1000000
    digest=hashlib.sha256(json.dumps({c:json.loads((folder/(c+'.json')).read_text(encoding='utf-8')) for c in ('en',)+LANGUAGES},ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    return {'mode':'offline_only','source_pages':['index.html','blog.html'],'saved_bundle_sha256':digest,
            'provenance':'Local AI drafts, not Google output; speaker review pending',
            'source_fields':len(english),'target_languages':9,'saved_draft_field_hits':draft_hits,
            'missing_draft_fields':missing,'source_hash_mismatches':mismatched,
            'verified_google_cache_fields':0,'google_requests':0,'characters_dispatched_to_google':0,
            'requests_authorized':False,'shared_policy':{**POLICY,'shared_ledger_connected':connection['connected'] and connection['project_matches']},
            'shared_counter_connection':connection,
            'translation_runner':'tools/translate-home-blog.py',
            'configured_private_ledger_present':connection['connected'],
            'configured_private_coordinator_present':bool(os.environ.get('DOMMYDOM_BUDGET_URL')),
            'actual_private_ledger_ceiling_usd':connection['cutoff_usd'],'actual_remaining_project_allowance':None,
            'hypothetical_google_characters_if_all_current_sources_required_provider_translation':if_all_sources_required_google,
            'hypothetical_current_blog_titles_and_previews_characters':blog_chars,
            'hypothetical_full_gross_usd_without_allowance':str(Decimal(if_all_sources_required_google)*Decimal('20')/1000000),
            'monthly_forecast':{'blogs_per_day':12,'days':30,'planning_characters_per_card':350,'targets':9,
                'dispatched_characters_without_cache':planned,'conditional_eligible_allowance':500000,
                'conditional_estimate_usd':str(estimate),'warning_exceeded':estimate>=12,
                'one_time_page_translations_included':False,
                'qualification':'Forecast only, not verified account usage or authorization. Extra translations and other callers consume the same project allowance.'},
            'blocking_reasons':['Live calls are not approved']+([connection['blocked_reason']] if connection['blocked_reason'] else [])+['Existing saved drafts are not Google output'],
            'provider_pricing_reference':'https://cloud.google.com/products/translate/pricing'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--verify-repeat',action='store_true')
    args=parser.parse_args();first=inspect()
    if first.get('workflow')!='whole-site':
        assert first['monthly_forecast']['dispatched_characters_without_cache']==1134000
        assert Decimal(first['monthly_forecast']['conditional_estimate_usd'])==Decimal('12.68')
        assert not first['source_hash_mismatches'] and not first['missing_draft_fields']
    if args.verify_repeat:
        second=inspect();assert first['saved_bundle_sha256']==second['saved_bundle_sha256']
        first['repeat_check']={'unchanged_source_and_saved_bundle':True,'new_google_requests':0,
            'new_google_characters':0,'note':'Offline repeat only. No provider requests.'}
    result=json.dumps(first,ensure_ascii=False,indent=2)+'\n'
    if args.output:args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(result,encoding='utf-8')
    print(result)

if __name__=='__main__':main()
