import re
from zope.component import queryAdapter
from Products.Archetypes.interfaces import IBaseContent

from quintagroup.seoptimizer.interfaces import ISEOCanonicalPath
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
        self.curl = re.compile('<link\srel\s*=\s*"canonical"\s+' \
            '[^>]*href\s*=\s*\"([^\"]*)\"[^>]*>', re.S|re.M)


    def test_CanonicalURL(self):
        html = self.publish(self.mydoc_path, self.basic_auth).getBody()
        foundcurls = self.curl.findall(html)
        mydoc_url = self.mydoc.absolute_url()

        self.assertTrue([1 for curl in foundcurls if curl==mydoc_url],
           "Wrong CANONICAL URL for document: %s, all must be: %s" % (
           foundcurls, mydoc_url))

    def test_updateCanonicalURL(self):
        mydoc_url_new = self.mydoc.absolute_url() + '.new'
        # Update canonical url property
        self.publish(self.mydoc_path + '/@@seo-context-properties?' \
           'seo_canonical_override=checked&seo_canonical=%s&' \
           'form.submitted=1' % mydoc_url_new, self.basic_auth)
        # Test updated canonical url
        html = self.publish(self.mydoc_path, self.basic_auth).getBody()
        foundcurls = self.curl.findall(html)

        qseo_url = self.mydoc.getProperty('qSEO_canonical','')
        self.assertTrue(qseo_url == mydoc_url_new,
           "Not set 'qSEO_canonical' property")
        self.assertTrue([1 for curl in foundcurls if curl==mydoc_url_new],
           "Wrong CANONICAL URL for document: %s, all must be: %s" % (
           foundcurls, mydoc_url_new))

    def test_seoCanonicalAdapterRegistration(self):
        seocanonical = queryAdapter(self.mydoc, interface=ISEOCanonicalPath)
        self.assertTrue(seocanonical is not None,
            "Not registered ISEOCanonicalPath adapter")

    def test_canonicalAdapterRegistration(self):
        import quintagroup
        if hasattr(quintagroup, 'canonicalpath'):
            from quintagroup.canonicalpath.interfaces import ICanonicalPath
            canonical = queryAdapter(self.mydoc, interface=ICanonicalPath)
            self.assertTrue(canonical is not None,
                "Not registered ICanonicalPath adapter")

    def test_canonicalAdapter(self):
        purl = getToolByName(self.portal, 'portal_url')
        mydoc_path_rel = '/'+'/'.join(purl.getRelativeContentPath(self.mydoc))

        canonical = queryAdapter(self.mydoc, ISEOCanonicalPath)
        cpath = canonical.canonical_path()
        self.assertTrue(cpath == mydoc_path_rel,
            "By canonical path adapter got: '%s', must be: '%s'" % (
             cpath, mydoc_path_rel))

        # Update canonical url property
        mydoc_url_new = self.mydoc.absolute_url() + '.new'
        self.publish(self.mydoc_path + '/@@seo-context-properties?' \
            'seo_canonical_override=checked&seo_canonical=%s' \
            '&form.submitted=1' % mydoc_url_new, self.basic_auth)

        mydoc_path_rel_new = mydoc_path_rel + '.new'
        newcpath = canonical.canonical_path()
        self.assertTrue(newcpath == mydoc_path_rel_new,
            "By canonical path adapter got: '%s', must be: '%s'" % (
             newcpath, mydoc_path_rel_new))


    def addCanonicalPathCatalogColumn(self):
        from Products.CMFPlone.CatalogTool import registerIndexableAttribute

        def canonical_path(obj, portal, **kwargs):
            """Return canonical_path property for the object.
            """
            cpath = queryAdapter(obj, interface=ISEOCanonicalPath)
            if cpath:
                return cpath.canonical_path()
            return None

        registerIndexableAttribute('canonical_path', canonical_path)

        catalog = getToolByName(self.portal, 'portal_catalog')
        catalog.addColumn(name='canonical_path')


    def testCatalogUpdated(self):
        purl = getToolByName(self.portal, 'portal_url')
        catalog = getToolByName(self.portal, 'portal_catalog')
        self.addCanonicalPathCatalogColumn()

        canonical = queryAdapter(self.mydoc, ISEOCanonicalPath)
        cpath = canonical.canonical_path()

        # get catalog data before update
        mydoc_catalog_canonical = catalog(id="mydoc")[0].canonical_path
        self.assertTrue(not mydoc_catalog_canonical)

        # Update canonical url property
        mydoc_url_new = self.mydoc.absolute_url() + '.new'
        self.publish(self.mydoc_path + '/@@seo-context-properties?' \
            'seo_canonical_override=checked&seo_canonical=%s' \
            '&form.submitted=1' % mydoc_url_new, self.basic_auth)

        newcpath = canonical.canonical_path()
        mydoc_catalog_canonical = catalog(id="mydoc")[0].canonical_path
        self.assertTrue(newcpath == mydoc_catalog_canonical,
            "canonical path get by adapter: '%s' not equals to cataloged one: '%s'" % (
             newcpath, mydoc_catalog_canonical))

    def test_Canonical4Plone(self):
        canonical = queryAdapter(self.portal, ISEOCanonicalPath)
        self.assertTrue(canonical is not None,
            "No 'ISEOCanonicalPath' adapter registered for the Plone object")


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCanonicalURL))
    return suite
