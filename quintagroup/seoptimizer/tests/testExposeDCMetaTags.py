from DateTime import DateTime

from quintagroup.seoptimizer.tests.base import FunctionalTestCase
from Products.PloneTestCase.PloneTestCase import portal_owner, \
    default_password
import re

METATAG = '.*(<meta\s+(?:(?:name="%s"\s*)|(?:content="(?P<tagcontent>.' \
          '*?)"\s*)){2}/>)'


class TestExposeDCMetaTags(FunctionalTestCase):

    def afterSetUp(self):
        self.sp = self.portal.portal_properties.site_properties
        self.basic_auth = ':'.join((portal_owner, default_password))
        self.loginAsPortalOwner()
        # Preparation for functional testing
        self.my_doc = self.portal.invokeFactory('Document', id='my_doc')
        self.my_doc = self.portal['my_doc']

    def test_propertyOff(self):
        self.sp.manage_changeProperties(exposeDCMetaTags=False)
        self.html = str(self.publish(self.portal.id + '/my_doc',
                                     self.basic_auth))
        m1 = re.match(METATAG % "DC.format", self.html, re.S | re.M)
        m2 = re.match(METATAG % "DC.distribution", self.html, re.S | re.M)
        self.assert_(not (m1 or m2), 'DC meta tags avaliable when ' \
                     'exposeDCMetaTags=False')

    def test_propertyOn(self):
        self.sp.manage_changeProperties(exposeDCMetaTags=True)
        self.html = str(self.publish(self.portal.id + '/my_doc',
                                     self.basic_auth))
        m1 = re.match(METATAG % "DC.format", self.html, re.S | re.M)
        m2 = re.match(METATAG % "DC.type", self.html, re.S | re.M)
        self.assert_(m1 and m2, 'DC meta tags not avaliable when ' \
                     'createManager=True')

    def test_descriptionInPropertyOff(self):
        self.sp.manage_changeProperties(exposeDCMetaTags=False)
        self.my_doc.setDescription("My document description")
        self.html = str(self.publish(self.portal.id + '/my_doc',
                                     self.basic_auth))
        m = re.match(METATAG % "description", self.html, re.S | re.M)
        self.assert_(m, 'No "description" meta tag when expose DC meta tags ' \
                     'is Off')

    def test_descriptionInPropertyOn(self):
        self.sp.manage_changeProperties(exposeDCMetaTags=True)
        self.my_doc.setDescription("My document description")
        self.html = str(self.publish(self.portal.id + '/my_doc',
                                     self.basic_auth))
        m = re.match(METATAG % "description", self.html, re.S | re.M)
        self.assert_(m, 'No "description" meta tag when expose DC meta tags ' \
                     'is On')

    def test_dateValidRange(self):
        self.sp.manage_changeProperties(exposeDCMetaTags=True)
        EFFDSTR, EXPDSTR = "2009/12/23", "2010/03/10"
        self.my_doc.setExpirationDate(EXPDSTR)
        self.my_doc.setEffectiveDate(EFFDSTR)
        self.html = str(self.publish(self.portal.id + '/my_doc',
                                     self.basic_auth))
        m = re.match(METATAG % "DC.date.valid_range", self.html, re.S | re.M)
        content = m and m.group("tagcontent")
        fact = content and map(DateTime, content.split("-"))
        expect = map(DateTime, [EFFDSTR, EXPDSTR])
        self.assert_(fact == expect, '"DC.date.valid_range" meta tags ' \
                     'content="%s", but "%s" must be' % (fact, expect))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestExposeDCMetaTags))
    return suite
