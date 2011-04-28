from unittest import TestSuite, makeSuite, TestCase
from quintagroup.seoptimizer.util import unescape


class TestUtils(TestCase):

    def test_unicode_str_unescaping(self):
        self.assertEqual(unescape(u"&&amp;-/&#91;"), u"&&-/[")

    def test_str_unescaping(self):
        self.assertEqual(unescape("&&amp;-/&#91;"), u"&&-/[")

    def test_hex_unescaping(self):
        self.assertEqual(unescape('&#x5B;'), u'[')

    def test_simple_text_unescaping(self):
        self.assertEqual(unescape("Simple text."), u"Simple text.")

    def test_entity_hex_unescaping(self):
        self.assertEqual(unescape('&amp;#x5B;'), u'&#x5B;')

    def test_intity_dec_unescaping(self):
        self.assertEqual(unescape('&amp;#91;'), u'&#91;')

    def test_entity_dec_hex_unescaping(self):
        self.assertEqual(unescape('&amp;#38;#x5B;'), u'&#38;#x5B;')

    def test_fake_entity_unescaping(self):
        self.assertEqual(unescape("&asd;"), u"&asd;")


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestUtils))
    return suite
