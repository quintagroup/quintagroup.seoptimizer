from base import *

KWSTMPL = '.*(<meta\s+(?:(?:name="keywords"\s*)|(?:content="%s"\s*)){2}/>)'

class TestUsageKeywords(FunctionalTestCase):

    def afterSetUp(self):
        self.sp = self.portal.portal_properties.seo_properties
        self.pu = self.portal.plone_utils
        self.basic_auth = ':'.join((portal_owner,default_password))
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
            html = str(self.publish(self.portal.id+'/my_doc', self.basic_auth))
            expect = ',\s*'.join(seokws)
            open('/tmp/testrender_SEOKeywords','w').write(html)
            self.assert_(re.match(KWSTMPL % expect, html, re.S|re.M),
                         "No '%s' keyword found" % str(seokws))

    def testbehave_NoSEOKeywordsOnlySubject(self):
        self.my_doc.setText('<p>local subject</p>')
        self.my_doc.setSubject('subject')
        html = str(self.publish(self.portal.id+'/my_doc', self.basic_auth))

        expect = "subject"
        self.assert_(re.match(KWSTMPL % expect, html, re.S|re.M),
                     "No '%s' keyword find" % expect)

    def testbehave_SEOKeywordsOverrideSubject(self):
        SEOKWS = ('local',)
        self.my_doc.setText('<p>local subject</p>')
        self.my_doc.setSubject('subject')
        self.my_doc.manage_addProperty('qSEO_keywords', SEOKWS, 'lines')
        html = str(self.publish(self.portal.id+'/my_doc', self.basic_auth))

        expect = ',\s*'.join(SEOKWS)
        self.assert_(re.match(KWSTMPL % expect, html, re.S|re.M),
                     "No '%s' keywords find" % SEOKWS)

    def testbehave_noSEOKeywordsNoSubject(self):
        """Nor seo keywords not subject added"""
        html = str(self.publish(self.portal.id+'/my_doc', self.basic_auth))
        self.assertFalse(re.match('.*(<meta\s[^\>]*name="keywords"[^\>]*>)',
                                  html, re.S|re.M), "'keyword' meta tag found")


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUsageKeywords))
    return suite
