from quintagroup.seoptimizer.tests.base import FunctionalTestCase
from Products.PloneTestCase.PloneTestCase import portal_owner, \
    default_password

from zope.formlib.form import FormFields
from zope.schema.interfaces import IBool
from quintagroup.seoptimizer.browser.seo_configlet import ISEOConfigletSchema


class TestConfiglet(FunctionalTestCase):

    def afterSetUp(self):
        self.sp = self.portal.portal_properties.site_properties
        self.seo = self.portal.portal_properties.seo_properties
        self.basic_auth = ':'.join((portal_owner, default_password))
        self.loginAsPortalOwner()
        self.save_url = self.portal.id + '/@@seo-controlpanel?' \
                        'form.actions.save=1&_authenticator=%s' \
                        % self._getauth()

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
        self.publish(self.save_url + '&form.default_custom_metatags=%s'
                     % formdata, self.basic_auth)

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
        self.publish(self.save_url + '&form.metatags_order=%s' % formdata,
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
        self.publish(self.save_url + "&form.types_seo_enabled=%s" % expect,
                     self.basic_auth)
        tse = self.seo.getProperty("content_types_with_seoproperties", ())
        self.assertTrue(tse == (expect,),
                        '"content_types_with_seoproperties" property ' \
                        'contains:" %s", must: "%s"' % (tse, expect))

    def test_typesSEOEnabled_Off(self):
        self.publish(self.save_url + '&form.types_seo_enabled-empty-marker=1',
             self.basic_auth)

        tse = self.seo.getProperty("content_types_with_seoproperties", ())
        self.assertTrue(tse == (), '"content_types_with_seoproperties" ' \
                        'property contains: "%s", must be empty"' % str(tse))

    def test_CustomScriptAdd(self):
        expect = "<script>\n<!-- Test custom script -->\n</script>"

        self.publish(self.save_url + '&form.custom_script=%s' % expect,
             self.basic_auth)

        cs = self.seo.getProperty("custom_script", "")
        self.assertTrue(cs == expect, '"custom_script" property ' \
            'contains: "%s", but "%s" must be"' % (cs, expect))

    def test_CustomScriptDel(self):
        self.publish(self.save_url + '&form.custom_script=',
             self.basic_auth)

        cs = self.seo.getProperty("custom_script", "")
        self.assertTrue(cs == "", '"custom_script" property ' \
            'contains: "%s", must be empty"' % cs)

    def test_fieldsAdd(self):
        expect = ('field1', 'field2')
        formdata = "\n".join(expect)
        self.publish(self.save_url + '&form.fields=%s' % formdata,
                     self.basic_auth)

        f = self.seo.getProperty("fields", ())
        self.assertTrue(f == expect, '"fields" property ' \
            'contains: "%s", must: "%s"' % (f, expect))

    def test_fieldsDel(self):
        data = ('field1', 'field2')
        self.seo._updateProperty("fields", data)
        self.publish(self.save_url + '&form.fields=',
                     self.basic_auth)

        f = self.seo.getProperty("fields", ())
        self.assertTrue(f == (), '"fields" property ' \
                        'contains: "%s", must be empty"' % str(f))

    def test_stopWordsAdd(self):
        expect = ('sw1', 'sw2', 'sw3')
        formdata = "\n".join(expect)
        self.publish(self.save_url + '&form.stop_words=%s' % formdata,
                     self.basic_auth)

        f = self.seo.getProperty("stop_words", ())
        self.assertTrue(f == expect, '"stop_words" property ' \
                        'contains: "%s", must: "%s"' % (f, expect))

    def test_stopWordsDel(self):
        data = ('sw1', 'sw2', 'sw3')
        self.seo._updateProperty("stop_words", data)
        self.publish(self.save_url + '&form.stop_words=',
                     self.basic_auth)

        f = self.seo.getProperty("stop_words", ())
        self.assertTrue(f == (), '"stop_words" property ' \
                        'contains: "%s", must be empty"' % str(f))

    def test_externalKeywordTest(self):
        fields = FormFields(ISEOConfigletSchema)
        ffield = fields.get("external_keywords_test")
        self.assertTrue(ffield is not None,
                        'Not found "external_keywords_test" field in ' \
                        'ISEOConfigletSchema interface')
        self.assertTrue(IBool.providedBy(ffield.field),
                        '"external_keywords_test" is not boolean type field')
        self.assertTrue(ffield.field.default == False,
                        '"external_keywords_test" field default value ' \
                        'is not set to False')

    def test_externalKeyword_On(self):
        self.publish(self.save_url + '&form.external_keywords_test=on',
                     self.basic_auth)
        self.assert_(self.seo.external_keywords_test)

    def test_externalKeyword_Off(self):
        self.publish(self.save_url + '&form.external_keywords_test=',
             self.basic_auth)
        self.assertTrue(not self.seo.external_keywords_test)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestConfiglet))
    return suite
