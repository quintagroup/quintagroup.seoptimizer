from quintagroup.seoptimizer.tests.base import FunctionalTestCase
from Products.PloneTestCase.PloneTestCase import portal_owner, \
    default_password

import urllib2
import re
from StringIO import StringIO
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from quintagroup.seoptimizer.browser.interfaces import IPloneSEOLayer

KWSTMPL = '.*(<meta\s+(?:(?:name="keywords"\s*)|(?:content="%s"\s*)){2}/>)'


class TestUsageKeywords(FunctionalTestCase):

    def afterSetUp(self):
        self.sp = self.portal.portal_properties.seo_properties
        self.pu = self.portal.plone_utils
        self.basic_auth = ':'.join((portal_owner, default_password))
        self.loginAsPortalOwner()
        #Preparation for functional testing
        self.my_doc = self.portal.invokeFactory('Document', id='my_doc')
        self.my_doc = self.portal['my_doc']

    def test_noDefaultKeywords(self):
        """No keywords added for the content by default"""
        metatags = self.pu.listMetaTags(self.my_doc)
        self.assert_('keywords' not in metatags)

    def testrender_SEOKeywords(self):
        """ """
        self.my_doc.setText('<p>foo bar</p>')
        self.my_doc.manage_addProperty('qSEO_keywords', [], 'lines')

        for seokws in [('foo',), ('foo', 'bar')]:
            self.my_doc._updateProperty('qSEO_keywords', seokws)
            html = str(self.publish(self.portal.id + '/my_doc',
                                    self.basic_auth))
            expect = ',\s*'.join(seokws)
            open('/tmp/testrender_SEOKeywords', 'w').write(html)
            self.assert_(re.match(KWSTMPL % expect, html, re.S | re.M),
                         "No '%s' keyword found" % str(seokws))

    def testbehave_NoSEOKeywordsOnlySubject(self):
        self.my_doc.setText('<p>local subject</p>')
        self.my_doc.setSubject('subject')
        html = str(self.publish(self.portal.id + '/my_doc', self.basic_auth))

        expect = "subject"
        self.assert_(re.match(KWSTMPL % expect, html, re.S | re.M),
                     "No '%s' keyword find" % expect)

    def testbehave_SEOKeywordsOverrideSubject(self):
        SEOKWS = ('local',)
        self.my_doc.setText('<p>local subject</p>')
        self.my_doc.setSubject('subject')
        self.my_doc.manage_addProperty('qSEO_keywords', SEOKWS, 'lines')
        html = str(self.publish(self.portal.id + '/my_doc', self.basic_auth))

        expect = ',\s*'.join(SEOKWS)
        self.assert_(re.match(KWSTMPL % expect, html, re.S | re.M),
                     "No '%s' keywords find" % SEOKWS)

    def testbehave_noSEOKeywordsNoSubject(self):
        """Nor seo keywords not subject added"""
        html = str(self.publish(self.portal.id + '/my_doc', self.basic_auth))
        self.assertFalse(re.match('.*(<meta\s[^\>]*name="keywords"[^\>]*>)',
                                  html, re.S | re.M),
                         "'keyword' meta tag found")


class TestCalcKeywords(FunctionalTestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.seo = self.portal.portal_properties.seo_properties
        #Preparation for functional testing
        self.key = "SEO_KEYWORD "
        self.portal.invokeFactory('Document', id='my_doc')
        self.my_doc = getattr(self.portal, 'my_doc')
        self.my_doc.setText(self.key * 2)
        # Emulate JS request
        self.app.REQUEST.set("text", self.key)
        # Mark request with IPloneSEOLayer browser layer interface
        alsoProvides(self.app.REQUEST, IPloneSEOLayer)
        # Get checkSEOKeywords view
        self.chckView = queryMultiAdapter((self.my_doc, self.app.REQUEST),
            name="checkSEOKeywords")

    def patchURLLib(self, fnc):
        self.orig_urlopen = urllib2.urlopen
        self.urlfd = StringIO()
        urllib2.urlopen = fnc

    def unpatchURLLib(self):
        urllib2.urlopen = self.orig_urlopen
        self.urlfd.close()

    def test_InternalPageRendering(self):
        self.assertTrue(not self.seo.external_keywords_test)
        # Only keywords from content must present in check view
        self.assertTrue('2' in self.chckView())

    def test_ExternalPageRendering(self):
        def patch_urlopen(*args, **kwargs):
            if args[0] == self.my_doc.absolute_url():
                self.urlfd.write(unicode(self.my_doc() +
                                 self.key).encode("utf-8"))
                self.urlfd.seek(0)
                return self.urlfd
            else:
                return self.orig_urlopen(*args, **kwargs)
        self.seo._updateProperty("external_keywords_test", True)
        self.patchURLLib(fnc=patch_urlopen)
        self.assertTrue(self.seo.external_keywords_test)
        # 1. Extra keyword must present in check view
        self.assertTrue('3' in self.chckView())
        # 2. Opened urllib file descriptor must be closed
        self.assertTrue(self.urlfd.closed,
                        "Opened file descriptor was not closed.")
        self.unpatchURLLib()

    def test_ExternalURLError(self):
        def patch_urlopen(*args, **kwargs):
            if args[0] == self.my_doc.absolute_url():
                raise urllib2.URLError("Some URL Error occured")
            else:
                return self.orig_urlopen(*args, **kwargs)
        self.seo._updateProperty("external_keywords_test", True)
        self.patchURLLib(fnc=patch_urlopen)
        self.assertTrue(self.seo.external_keywords_test)
        # 1. Information about problem must present in check view
        msg = self.chckView()
        rematch = re.match(
            ".*Problem with page retrieval.*error_log/showEntry\?id=",
             msg, re.S)
        self.assertTrue(rematch, "Return message has incomplete information "
            "about problem with page retrieval: %s" % msg)
        # 2. Opened urllib file descriptor should not be closed because
        #    it even not returned to the view
        self.assertFalse(self.urlfd.closed,
                         "Opened file descriptor was closed.")
        self.unpatchURLLib()

    def test_ExternalIOError(self):
        def patch_urlopen(*args, **kwargs):
            if args[0] == self.my_doc.absolute_url():
                self.urlfd.write(unicode(self.my_doc() +
                                 self.key).encode("utf-8"))
                self.urlfd.seek(0)
                return self.urlfd
            else:
                return self.orig_urlopen(*args, **kwargs)

        def patch_read(*args, **kwargs):
            raise Exception("General exception")
        # Patch urllib2.urlopen to emulate external url retrieval
        self.patchURLLib(fnc=patch_urlopen)
        # Patch opened by urllib2 file descriptor to emulate
        # IOError during reading
        self.urlfd.read = patch_read
        self.seo._updateProperty("external_keywords_test", True)
        self.assertTrue(self.seo.external_keywords_test)
        # 1. General exception must be raised.
        self.assertRaises(Exception, self.chckView)
        # 2. Opened urllib file descriptor must be closed
        self.assertTrue(self.urlfd.closed,
                        "Opened file descriptor was not closed.")
        self.unpatchURLLib()


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUsageKeywords))
    suite.addTest(makeSuite(TestCalcKeywords))
    return suite
