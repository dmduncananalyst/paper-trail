"""Offline regressions for article-specific archive photo protection."""
from pathlib import Path
import importlib.util,unittest
spec=importlib.util.spec_from_file_location('verify_blogs',Path(__file__).with_name('verify-blog-translations.py'));v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
def card(name,image):return '<article class="blog-story"><img src="'+image+'"><a href="'+name+'">Read</a></article>'
class Assignments(unittest.TestCase):
 def setUp(self):self.source='<img src="logo.png">'+card('one.html','one.jpg')+card('two.html','two.jpg')
 def test_reordered_correct_pairs_and_saved_attribution(self):v.verify_image_assignments(self.source,'<img src="logo.png">'+card('es/two.html','two.jpg')+card('es/one.html','one.jpg')+'<img src="attribution.png">','blog.html','es')
 def test_swapped_photos_fail(self):
  with self.assertRaises(AssertionError):v.verify_image_assignments(self.source,'<img src="logo.png">'+card('es/one.html','two.jpg')+card('es/two.html','one.jpg'),'blog.html','es')
 def test_missing_card_fails(self):
  with self.assertRaises(AssertionError):v.verify_image_assignments(self.source,'<img src="logo.png">'+card('es/one.html','one.jpg'),'blog.html','es')
 def test_duplicate_card_fails(self):
  with self.assertRaises(AssertionError):v.verify_image_assignments(self.source,self.source+card('one.html','one.jpg'),'blog.html','es')
 def test_changed_shared_logo_fails(self):
  with self.assertRaises(AssertionError):v.verify_image_assignments(self.source,self.source.replace('logo.png','wrong.png'),'blog.html','es')
 def test_individual_article_image_order_remains_strict(self):
  with self.assertRaises(AssertionError):v.verify_image_assignments('<img src="one.jpg"><img src="two.jpg">','<img src="two.jpg"><img src="one.jpg">','one.html','es')
if __name__=='__main__':unittest.main()
