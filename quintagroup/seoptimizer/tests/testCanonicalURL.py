import re
from zope.component import queryAdapter
from base import getToolByName, FunctionalTestCase, newSecurityManager
from config import *

class TestCanonicalURL(FunctionalTestCase):

    def afterSetUp(self):
        self.qi = self.portal.portal_quickinstaller
        self.qi.installProduct(PROJECT_NAME)
        #self.portal.changeSkin('Plone Default')

        self.basic_auth = 'portal_manager:secret'
        uf = self.app.acl_users
        uf.userFolderAddUser('portal_manager', 'secret', ['Manager'], [])
        user = uf.getUserById('portal_manager')
        if not hasattr(user, 'aq_base'):
            user = user.__of__(uf)
        newSecurityManager(None, user)

        self.portal.invokeFactory('Document', id='mydoc')
        self.mydoc = self.portal['mydoc']
        self.mydoc_path = "/%s" % self.mydoc.absolute_url(1)
        self.curl = re.compile('<link\srel\s*=\s*"canonical"\s+[^>]*href\s*=\s*\"([^\"]*)\"[^>]*>', re.S|re.M)


    def test_CanonicalURL(self):
        html = self.publish(self.mydoc_path, self.basic_auth).getBody()
        foundcurls = self.curl.findall(html)
        mydoc_url = self.mydoc.absolute_url()

        self.assert_([1 for curl in foundcurls if curl==mydoc_url],
           "Wrong CANONICAL URL for document: %s, all must be: %s" % (foundcurls, mydoc_url))

    def test_updateCanonicalURL(self):
        mydoc_url_new = self.mydoc.absolute_url() + '.new'
        # Update canonical url property
        self.publish(self.mydoc_path + '/@@seo-context-properties?seo_canonical_override=checked' \
                     '&seo_canonical=%s&form.submitted=1' % mydoc_url_new, self.basic_auth)
        # Test updated canonical url
        html = self.publish(self.mydoc_path, self.basic_auth).getBody()
        foundcurls = self.curl.findall(html)

        self.assert_(self.mydoc.getProperty('qSEO_canonical','') == mydoc_url_new,
                     "Not set 'qSEO_canonical' property")
        self.assert_([1 for curl in foundcurls if curl==mydoc_url_new],
           "Wrong CANONICAL URL for document: %s, all must be: %s" % (foundcurls, mydoc_url_new))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCanonicalURL))
    return suite
