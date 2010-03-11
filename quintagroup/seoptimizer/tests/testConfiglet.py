import re
from base import *

class TestConfiglet(FunctionalTestCase):

    def afterSetUp(self):
        self.sp = self.portal.portal_properties.site_properties
        self.seo = self.portal.portal_properties.seo_properties
        self.basic_auth = ':'.join((portal_owner,default_password))
        self.loginAsPortalOwner()
        self.save_url = self.portal.id+'/@@seo-controlpanel?form.actions.save=1' \
            '&_authenticator=%s' % self._getauth()

    def test_exposeDCMetaTags_On(self):
        self.publish(self.save_url + '&form.exposeDCMetaTags=on',
                     self.basic_auth)
        self.assert_(self.sp.exposeDCMetaTags)

    def test_exposeDCMetaTags_Off(self):
        self.publish(self.save_url + '&form.exposeDCMetaTags=',
             self.basic_auth)
        self.assertTrue(not self.sp.exposeDCMetaTags)

    def test_defaultCustomMetatags_On(self):
        expect = ('test', 'custom', 'metatags')
        formdata = "\n".join(expect)
        self.publish(self.save_url + '&form.default_custom_metatags=%s'%formdata,
             self.basic_auth)

        dcm = self.seo.getProperty("default_custom_metatags", ())
        self.assertTrue(dcm == expect, '"default_custom_metatags" property ' \
            'contains: "%s", must: "%s"' % (dcm, expect))

    def test_defaultCustomMetatags_Off(self):
        data = ('test', 'custom', 'metatags')
        self.seo._updateProperty("default_custom_metatags", data)
        self.publish(self.save_url + '&form.default_custom_metatags=',
             self.basic_auth)

        dcm = self.seo.getProperty("default_custom_metatags", ())
        self.assertTrue(dcm == (), '"default_custom_metatags" property ' \
            'contains: "%s", must be empty"' % str(dcm))

    def test_metatagsOrder_On(self):
        expect = ('test', 'metatags', 'order')
        formdata = "\n".join(expect)
        self.publish(self.save_url + '&form.metatags_order=%s'%formdata,
             self.basic_auth)

        mo = self.seo.getProperty("metatags_order", ())
        self.assertTrue(mo == expect, '"metatags_order" property ' \
            'contains: "%s", must: "%s"' % (mo, expect))

    def test_metatagsOrder_Off(self):
        data = ('test', 'metatags', 'order')
        self.seo._updateProperty("metatags_order", data)
        self.publish(self.save_url + '&form.metatags_order=',
             self.basic_auth)

        mo = self.seo.getProperty("metatags_order", ())
        self.assertTrue(mo == (), '"metatags_order" property ' \
            'contains: "%s", must be empty"' % str(mo))

    def test_typesSEOEnabled_On(self):
        expect = 'Event'
        self.publish(self.save_url + "&form.types_seo_enabled=%s" % expect, self.basic_auth)
        tse = self.seo.getProperty("content_types_with_seoproperties", ())
        self.assertTrue(tse == (expect,),
            '"content_types_with_seoproperties" property contains: ' \
            '"%s", must: "%s"' % (tse, expect))

    def test_typesSEOEnabled_Off(self):
        self.publish(self.save_url + '&form.types_seo_enabled-empty-marker=1',
             self.basic_auth)

        tse = self.seo.getProperty("content_types_with_seoproperties", ())
        self.assertTrue(tse == (), '"content_types_with_seoproperties" property ' \
            'contains: "%s", must be empty"' % str(tse))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestConfiglet))
    return suite
