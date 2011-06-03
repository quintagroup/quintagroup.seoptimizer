from quintagroup.canonicalpath.interfaces import ICanonicalLink
from quintagroup.seoptimizer.tests.base import FunctionalTestCase
from Products.PloneTestCase.PloneTestCase import portal_owner, \
    default_password
import re
from Products.CMFCore.utils import getToolByName
from quintagroup.canonicalpath.adapters import PROPERTY_LINK \
                                        as CANONICAL_PROPERTY


class TestCanonicalURL(FunctionalTestCase):

    def afterSetUp(self):
        self.basic_auth = ':'.join((portal_owner, default_password))
        self.loginAsPortalOwner()
        # Preparation for functional testing
        self.portal.invokeFactory('Document', id='mydoc')
        self.mydoc = self.portal['mydoc']
        self.mydoc_path = "/%s" % self.mydoc.absolute_url(1)
        self.curl = re.compile('<link\srel\s*=\s*"canonical"\s+' \
                               '[^>]*href\s*=\s*\"([^\"]*)\"[^>]*>',
                                re.S | re.M)

    def test_NoCanonicalURL(self):
        html = self.publish(self.mydoc_path, self.basic_auth).getBody()
        foundcurls = self.curl.findall(html)
        assert not self.mydoc.hasProperty(CANONICAL_PROPERTY)
        self.assertTrue(not foundcurls, "CANONICAL URL found, " \
                "but object hasn't '%s' property" % CANONICAL_PROPERTY)

    def test_CanonicalProperty(self):
        self.assertTrue(not self.mydoc.hasProperty(CANONICAL_PROPERTY),
                        'Canonical URL property is present in new document.')

    def test_CanonicalPropertyEnable(self):
        curl = '/newcanonical'
        self.publish(self.mydoc_path + '/@@seo-context-properties?' \
                     'seo_canonical=%s&seo_canonical_override=checked&'\
                     'form.submitted=1&form.button.Save=Save' % curl,
                      self.basic_auth)

        self.assertTrue(self.mydoc.hasProperty(CANONICAL_PROPERTY),
                        'Overriding Canonical URL enabled,' \
                        'but object hasn\'t canonical url property')

        self.assertTrue(self.mydoc.getProperty(CANONICAL_PROPERTY) == curl,
                        "Wrong Canonical URL for document: %s, all must be: %s"
                        % (self.mydoc.getProperty(CANONICAL_PROPERTY), curl))

    def test_CanonicalPropertyDisable(self):
        curl = '/newcanonical'
        self.mydoc.manage_addProperty(CANONICAL_PROPERTY, curl,
                                      'string')

        assert self.mydoc.getProperty(CANONICAL_PROPERTY) == curl

        self.publish(self.mydoc_path + '/@@seo-context-properties?' \
                     'seo_canonical=%s&seo_canonical_override=&'\
                     'form.submitted=1&form.button.Save=Save' % curl,
                      self.basic_auth)

        self.assertTrue(not self.mydoc.hasProperty(CANONICAL_PROPERTY),
                        'Overriding Canonical URL disabled,' \
                        'but canonical link is present in object properties')

    def test_CanonicalUrlPresent(self):
        self.mydoc.manage_addProperty(CANONICAL_PROPERTY, self.mydoc_path,
                                      'string')
        assert self.mydoc.hasProperty(CANONICAL_PROPERTY)

        html = self.publish(self.mydoc_path, self.basic_auth).getBody()
        foundcurls = self.curl.findall(html)

        self.assertTrue([1 for curl in foundcurls if curl == self.mydoc_path],
           "Wrong CANONICAL URL for document: %s, all must be: %s" % (
           foundcurls, self.mydoc_path))

    def test_updateCanonicalURL(self):
        mydoc_url_new = self.mydoc.absolute_url() + '.new'
        # Update canonical url property
        self.publish(self.mydoc_path + '/@@seo-context-properties?' \
                     'seo_canonical_override=checked&seo_canonical=%s&' \
                     'form.submitted=1&form.button.Save=Save' % mydoc_url_new,
                     self.basic_auth)
        # Test updated canonical url
        html = self.publish(self.mydoc_path, self.basic_auth).getBody()
        foundcurls = self.curl.findall(html)

        qseo_url = ICanonicalLink(self.mydoc).canonical_link
        self.assertTrue(qseo_url == mydoc_url_new,
                        "Not set 'qSEO_canonical' property")
        self.assertTrue([1 for curl in foundcurls if curl == mydoc_url_new],
                        "Wrong CANONICAL URL for document: %s, all must be: %s"
                        % (foundcurls, mydoc_url_new))

    def test_defaultCanonical(self):
        expect = self.mydoc.absolute_url()
        cpath = ICanonicalLink(self.mydoc).canonical_link
        self.assertTrue(cpath == expect,
            "Default canonical link adapter return: '%s', must be: '%s'" % (
             cpath, expect))

    def testCatalogUpdated(self):
        getToolByName(self.portal, 'portal_url')
        catalog = getToolByName(self.portal, 'portal_catalog')
        catalog.addColumn('canonical_link')

        # get catalog data before update
        mydoc_catalog_canonical = catalog(id="mydoc")[0].canonical_link
        self.assertTrue(not mydoc_catalog_canonical)

        # Update canonical url property
        mydoc_url_new = self.mydoc.absolute_url() + '.new'
        self.publish(self.mydoc_path + '/@@seo-context-properties?' \
            'seo_canonical_override=checked&seo_canonical=%s' \
            '&form.submitted=1&form.button.Save=Save' % mydoc_url_new,
             self.basic_auth)

        newcpath = ICanonicalLink(self.mydoc).canonical_link
        mydoc_catalog_canonical = catalog(id="mydoc")[0].canonical_link
        self.assertTrue(newcpath == mydoc_catalog_canonical,
                        "canonical path get by adapter: '%s' not equals to "\
                        "cataloged one: '%s'" % (newcpath,
                                                 mydoc_catalog_canonical))

    def test_canonicalValidation(self):
        wrong_canonical = 'wrong   canonical'
        # Update canonical url property
        html = self.publish(self.mydoc_path + '/@@seo-context-properties?' \
                            'seo_canonical_override=checked&seo_canonical=%s&'\
                            'form.submitted=1&form.button.Save=Save'
                            % wrong_canonical, self.basic_auth).getBody()
        self.assertTrue("wrong canonical url" in html,
                        "Canonical url not validated")

    def test_delCanonical(self):
        newcanonical = '/new_canonical'
        ICanonicalLink(self.mydoc).canonical_link = newcanonical

        assert ICanonicalLink(self.mydoc).canonical_link == newcanonical

        # remove canonical url customization
        self.publish(self.mydoc_path + '/@@seo-context-properties?' \
                     'seo_canonical=%s&seo_canonical_override=&'\
                     'form.submitted=1&form.button.Save=Save' % newcanonical,
                      self.basic_auth)

        mydoc_canonical = ICanonicalLink(self.mydoc).canonical_link
        self.assertTrue(mydoc_canonical == self.mydoc.absolute_url(),
            "Steel customized canonical url after remove customization")


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCanonicalURL))
    return suite
