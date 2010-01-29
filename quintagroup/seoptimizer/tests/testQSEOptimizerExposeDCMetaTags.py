import re
from base import getToolByName, FunctionalTestCase, newSecurityManager
from config import *

class TestExposeDCMetaTags(FunctionalTestCase):

    def afterSetUp(self):
        self.qi = self.portal.portal_quickinstaller
        self.sp = self.portal.portal_properties.site_properties
        self.qi.installProduct(PROJECT_NAME)
        self.basic_auth = 'portal_manager:secret'
        uf = self.app.acl_users
        uf.userFolderAddUser('portal_manager', 'secret', ['Manager'], [])
        user = uf.getUserById('portal_manager')
        if not hasattr(user, 'aq_base'):
            user = user.__of__(uf)
        newSecurityManager(None, user)

        '''Preparation for functional testing'''
        self.my_doc = self.portal.invokeFactory('Document', id='my_doc')
        self.my_doc = self.portal['my_doc']

    def test_exposeDCMetaTags_in_configletOn(self):
        path = self.portal.id+'/@@seo-controlpanel?exposeDCMetaTags=True&form.submitted=1'
        self.publish(path, self.basic_auth)
        self.assert_(self.sp.exposeDCMetaTags)

    def test_exposeDCMetaTags_in_configletOff(self):
        self.publish(self.portal.id+'/@@seo-controlpanel?form.submitted=1', self.basic_auth)
        self.assert_(not self.sp.exposeDCMetaTags)

    def test_exposeDCMetaTagsPropertyOff(self):
        self.sp.manage_changeProperties(exposeDCMetaTags = False)
        self.html = str(self.publish(self.portal.id+'/my_doc', self.basic_auth))
        m1 = re.match('.*(<meta\s+(?:(?:name="DC.format"\s*)|(?:content=".*?"\s*)){2}/>)', self.html, re.S|re.M)
        m2 = re.match('.*(<meta\s+(?:(?:name="DC.distribution"\s*)|(?:content=".*?"\s*)){2}/>)', self.html, re.S|re.M)
        m = m1 or m2
        self.assert_(not m, 'DC meta tags avaliable when exposeDCMetaTags=False')

    def test_exposeDCMetaTagsPropertyOn(self):
        self.sp.manage_changeProperties(exposeDCMetaTags = True)
        self.html = str(self.publish(self.portal.id+'/my_doc', self.basic_auth))
        m1 = re.match('.*(<meta\s+(?:(?:name="DC.format"\s*)|(?:content=".*?"\s*)){2}/>)', self.html, re.S|re.M)
        m2 = re.match('.*(<meta\s+(?:(?:name="DC.type"\s*)|(?:content=".*?"\s*)){2}/>)', self.html, re.S|re.M)
        m = m1 and m2
        self.assert_(m, 'DC meta tags not avaliable when createManager=True')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestExposeDCMetaTags))
    return suite
