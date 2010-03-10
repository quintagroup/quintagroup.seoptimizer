import re
from base import getToolByName, FunctionalTestCase, newSecurityManager, ptc
from config import *

METATAG = '.*(<meta\s+(?:(?:name="%s"\s*)|(?:content=".*?"\s*)){2}/>)'

class TestExposeDCMetaTags(FunctionalTestCase):

    def afterSetUp(self):
        self.sp = self.portal.portal_properties.site_properties
        self.basic_auth = ':'.join((ptc.portal_owner,ptc.default_password))
        self.loginAsPortalOwner()
        # Preparation for functional testing
        self.my_doc = self.portal.invokeFactory('Document', id='my_doc')
        self.my_doc = self.portal['my_doc']

    def test_exposeDCMetaTagsPropertyOff(self):
        self.sp.manage_changeProperties(exposeDCMetaTags = False)
        self.html = str(self.publish(self.portal.id+'/my_doc', self.basic_auth))
        m1 = re.match(METATAG % "DC.format", self.html, re.S|re.M)
        m2 = re.match(METATAG % "DC.distribution", self.html, re.S|re.M)
        self.assert_(not (m1 or m2), 'DC meta tags avaliable when exposeDCMetaTags=False')

    def test_exposeDCMetaTagsPropertyOn(self):
        self.sp.manage_changeProperties(exposeDCMetaTags = True)
        self.html = str(self.publish(self.portal.id+'/my_doc', self.basic_auth))
        m1 = re.match(METATAG % "DC.format", self.html, re.S|re.M)
        m2 = re.match(METATAG % "DC.type", self.html, re.S|re.M)
        self.assert_(m1 and m2, 'DC meta tags not avaliable when createManager=True')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestExposeDCMetaTags))
    return suite
