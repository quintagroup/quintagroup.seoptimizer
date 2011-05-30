# -*- coding: utf8 -*-
from unittest import TestSuite, makeSuite, TestCase
from quintagroup.seoptimizer.util import unescape


class TestUtils(TestCase):

    def test_unicode_str_unescaping(self):
        self.assertEqual(unescape("&&amp;-/&#91;"), "&&-/[")

    def test_str_unescaping(self):
        self.assertEqual(unescape("&&amp;-/&#91;"), "&&-/[")

    def test_entity_unicode_unescaping(self):
        self.assertEqual(unescape(u"&&amp;ї".encode('utf-8')),
                                  u"&&ї".encode('utf-8'))

    def test_hex_unescaping(self):
        self.assertEqual(unescape('&#x5B;'), '[')

    def test_simple_text_unescaping(self):
        self.assertEqual(unescape("Simple text."), "Simple text.")

    def test_entity_hex_unescaping(self):
        self.assertEqual(unescape('&amp;#x5B;'), '&#x5B;')

    def test_intity_dec_unescaping(self):
        self.assertEqual(unescape('&amp;#91;'), '&#91;')

    def test_entity_dec_hex_unescaping(self):
        self.assertEqual(unescape('&amp;#38;#x5B;'), '&#38;#x5B;')

    def test_fake_entity_unescaping(self):
        self.assertEqual(unescape("&asd;"), "&asd;")

    def test_aentity_unescaping(self):
        self.assertEqual(unescape("&mdash;").encode('utf-8'),
                         u"—".encode('utf-8'))


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestUtils))
    return suite
