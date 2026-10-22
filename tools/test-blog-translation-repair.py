"""Offline checks for lossless spans, cache keys and localized SEO identities."""
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('blog_sync',Path(__file__).with_name('sync-blog-translations.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class BlogTranslationRepair(unittest.TestCase):
    def test_entity_paragraph_is_one_complete_provider_segment(self):
        source='<html><body><p>  A contractor&#x27;s records &amp; receipts.  </p></body></html>'
        slots=m.Inventory(source).slots
        self.assertEqual(len(slots),1)
        a,b,text,attribute=slots[0]
        self.assertEqual(text,"A contractor's records & receipts.")
        self.assertEqual(source[a:b],"A contractor&#x27;s records &amp; receipts.")
        self.assertFalse(attribute)

    def test_scripts_forms_and_language_choices_are_preserved(self):
        source='<head><script>const x="Never translate code";</script></head><body><select id="language"><option>English</option></select><form action="/submit"><input name="email" placeholder="Your email"></form></body>'
        slots=m.Inventory(source).slots
        self.assertEqual([s[2] for s in slots],['Your email'])
        for a,b,text,attribute in reversed(slots):source=source[:a]+'Correo'+source[b:]
        self.assertIn('const x="Never translate code";',source)
        self.assertIn('<form action="/submit">',source)
        self.assertIn('<option>English</option>',source)

    def test_schema_urls_fragments_and_complete_body_localize(self):
        fields={m.key('Approved title','es'):{'text':'Título aprobado'}}
        schema={'@type':'BlogPosting','@id':m.ORIGIN+'article.html#article','url':m.ORIGIN+'article.html','mainEntityOfPage':m.ORIGIN+'article.html','headline':'Approved title','articleBody':'English body','citation':['https://www.irs.gov/taxtopics/tc305']}
        actual=m.translated_schema(schema,'es',fields,['article.html'],'Texto completo')
        self.assertEqual(actual['@id'],m.ORIGIN+'es/article.html#article')
        self.assertEqual(actual['mainEntityOfPage'],m.ORIGIN+'es/article.html')
        self.assertEqual(actual['headline'],'Título aprobado')
        self.assertEqual(actual['articleBody'],'Texto completo')
        self.assertEqual(actual['citation'],schema['citation'])
        self.assertEqual(actual['inLanguage'],'es')

    def test_saved_cache_key_and_approval_scope_are_stable(self):
        self.assertEqual(m.key('one  paragraph\ncontinued','es'),m.key('one paragraph continued','es'))
        self.assertNotEqual(m.key('one paragraph continued','es'),m.key('one paragraph continued','fa'))
        self.assertFalse(m.eligible('https://www.irs.gov/taxtopics/tc305'))

if __name__=='__main__':unittest.main()
