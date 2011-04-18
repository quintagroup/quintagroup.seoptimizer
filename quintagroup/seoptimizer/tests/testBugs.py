import urllib
from cStringIO import StringIO

from OFS.interfaces import ITraversable

from zope.component import providedBy
from zope.component import getGlobalSiteManager
from zope.component import queryAdapter, getMultiAdapter
from zope.interface import directlyProvides
from zope.viewlet.interfaces import IViewlet, IViewletManager
from zope.publisher.browser import TestRequest

from quintagroup.seoptimizer.browser.interfaces import IPloneSEOLayer
from quintagroup.seoptimizer.browser.views import PROP_CUSTOM_PREFIX
from quintagroup.seoptimizer.browser.seo_configlet import ISEOConfigletSchema
from quintagroup.canonicalpath.interfaces import ICanonicalLink
from quintagroup.canonicalpath.adapters import DefaultCanonicalLinkAdapter
from base import *


class TestBugs(FunctionalTestCase):

    def afterSetUp(self):
        self.basic_auth = ':'.join((portal_owner, default_password))
        self.loginAsPortalOwner()
        # prepare test document
        my_doc = self.portal.invokeFactory('Document', id='my_doc')
        self.my_doc = self.portal['my_doc']
        self.mydoc_path = "/%s" % self.my_doc.absolute_url(1)

    def test_modification_date(self):
        """ Modification date changing on SEO properties edit """
        form_data = {'seo_title': 'New Title',
                     'seo_title_override:int': 1,
                     'form.button.Save': "Save",
                     'form.submitted:int': 1}

        md_before = self.my_doc.modification_date
        self.publish(path=self.mydoc_path + '/@@seo-context-properties',
                     basic=self.basic_auth, request_method='POST',
                     stdin=StringIO(urllib.urlencode(form_data)))
        md_after = self.my_doc.modification_date

        self.assertNotEqual(md_before, md_after)

    def test_bug_20_at_plone_org(self):
        portal = self.portal
        fp = portal['front-page']
        request = portal.REQUEST
        view = portal.restrictedTraverse('@@plone')

        manager = getMultiAdapter((fp, request, view), IViewletManager,
                        name=u'plone.htmlhead')
        viewlet = getMultiAdapter((fp, request, view, manager), IViewlet,
                        name=u'plone.htmlhead.title')
        viewlet.update()
        old_title = viewlet.render()

        # add IPloneSEOLayer
        directlyProvides(request, IPloneSEOLayer)

        viewlet = getMultiAdapter((fp, request, view, manager), IViewlet,
                        name=u'plone.htmlhead.title')
        viewlet.update()
        new_title = viewlet.render()

        self.assertEqual(old_title, new_title)

    def test_bug_22_at_plone_org(self):
        """If ICanonicalLink adapter is not found for the context object
           - page rendering should not break, but only canonical link
           should disappear.
        """
        curl = re.compile('<link\srel\s*=\s*"canonical"\s+' \
                          '[^>]*href\s*=\s*\"([^\"]*)\"[^>]*>', re.S | re.M)
        # When adapter registered for the object - canoncal link
        # present on the page
        self.assertNotEqual(queryAdapter(self.my_doc, ICanonicalLink), None)

        res = self.publish(path=self.mydoc_path, basic=self.basic_auth)
        self.assertNotEqual(curl.search(res.getBody()), None)

        # Now remove adapter from the registry -> this should :
        #     - not break page on rendering;
        #     - canonical link will be absent on the page
        gsm = getGlobalSiteManager()
        gsm.unregisterAdapter(DefaultCanonicalLinkAdapter, [ITraversable, ],
                              ICanonicalLink)
        self.assertEqual(queryAdapter(self.my_doc, ICanonicalLink), None)

        res = self.publish(path=self.mydoc_path, basic=self.basic_auth)
        self.assertEqual(curl.search(res.getBody()), None)

        # register adapter back in the global site manager
        gsm.registerAdapter(DefaultCanonicalLinkAdapter, [ITraversable, ],
                            ICanonicalLink)

    def test_bug_19_23_at_plone_org(self):
        """overrides.zcml should present in the root of the package"""
        import quintagroup.seoptimizer
        try:
            zcml.load_config('overrides.zcml', quintagroup.seoptimizer)
        except IOError:
            self.fail("overrides.zcml removed from the package root")

    def test_escape_characters_title(self):
        """Change escape characters in title of SEO properties
           Bug url http://plone.org/products/plone-seo/issues/31
        """
        from cgi import escape
        title = 'New <i>Title</i>'
        form_data = {'seo_title': title,
                     'seo_title_override:int': 1,
                     'form.button.Save': "Save",
                     'form.submitted:int': 1}

        res = self.publish(path=self.mydoc_path + '/@@seo-context-properties',
                     basic=self.basic_auth, request_method='POST',
                     stdin=StringIO(urllib.urlencode(form_data)))
        html = self.publish(self.mydoc_path, self.basic_auth).getBody()
        m = re.match('.*<title>\\s*%s\\s*</title>' % escape(title), html,
                     re.S | re.M)
        self.assert_(m, 'Title is not escaped properly.')

    def test_escape_characters_comment(self):
        """Change escape characters in comment of SEO properties
        """
        from cgi import escape
        comment = 'New <i>comment</i>'
        form_data = {'seo_title': 'New Title',
                     'seo_title_override:int': 1,
                     'seo_html_comment': comment,
                     'seo_html_comment_override:int': 1,
                     'form.button.Save': "Save",
                     'form.submitted:int': 1}

        res = self.publish(path=self.mydoc_path + '/@@seo-context-properties',
                           basic=self.basic_auth, request_method='POST',
                           stdin=StringIO(urllib.urlencode(form_data)))
        html = self.publish(self.mydoc_path, self.basic_auth).getBody()
        m = re.match('.*<!--\\s*%s\\s*-->' % escape(comment), html,
                     re.S | re.M)
        self.assert_(m, 'Comment is not escaped properly.')

    def test_bug_custom_metatags_update(self):
        # Prepare a page for the test
        page = self.portal["front-page"]
        request = self.portal.REQUEST
        directlyProvides(request, IPloneSEOLayer)
        seo_context_props = getMultiAdapter((page, request),
                                            name="seo-context-properties")
        # Set default custom meta tag without default value (tag name only)
        self.gseo = queryAdapter(self.portal, ISEOConfigletSchema)
        self.gseo.default_custom_metatags = ["test_tag", ]
        try:
            # Breakage on updating custom metatag
            # with seo-context-properties view
            seo_context_props.updateSEOCustomMetaTagsProperties([])
        except IndexError:
            self.fail("Error in calculating of default tag value, when only "\
                      "tag name set in default_custom_metatags property of "\
                      "the configlet.")


class TestBug24AtPloneOrg(FunctionalTestCase):

    def afterSetUp(self):
        # Add test users: member, editor
        member_id = 'test_member'
        editor_id = 'test_editor'
        test_pswd = 'pswd'
        uf = self.portal.acl_users
        uf.userFolderAddUser(member_id, test_pswd,
                        ['Member'], [])
        uf.userFolderAddUser(editor_id, test_pswd,
                        ['Member', 'Editor'], [])

        self.member_auth = '%s:%s' % (member_id, test_pswd)
        self.editor_auth = '%s:%s' % (editor_id, test_pswd)
        self.portal_url = '/'.join(self.portal.getPhysicalPath())

    def test_not_break(self):
        """Default portal page should not breaks for any user"""
        # Anonymous
        resp = self.publish(path=self.portal_url)
        self.assertEqual(resp.getStatus(), 200)
        # Member
        resp = self.publish(path=self.portal_url, basic=self.member_auth)
        self.assertEqual(resp.getStatus(), 200)
        # Editor: this fails, althought must pass
        resp = self.publish(path=self.portal_url, basic=self.editor_auth)
        self.assertEqual(resp.getStatus(), 200)

    def test_tab_visibility(self):
        """Only Editor can view seo tab"""
        rexp = re.compile('<a\s+[^>]*' \
               'href="[a-zA-Z0-9\:\/_-]*/@@seo-context-properties"[^>]*>'\
               '\s*SEO Properties\s*</a>', re.I | re.S)
        # Anonymous: NO SEO Properties link
        res = self.publish(path=self.portal_url).getBody()
        self.assertEqual(rexp.search(res), None)
        # Member: NO 'SEO Properties' link
        res = self.publish(path=self.portal_url,
                           basic=self.member_auth).getBody()
        self.assertEqual(rexp.search(res), None)
        # Editor: PRESENT 'SEO Properties' link
        res = self.publish(path=self.portal_url,
                           basic=self.editor_auth).getBody()
        self.assertNotEqual(rexp.search(res), None)

    def test_tab_access(self):
        """Only Editor can access 'SEO Properties' tab"""
        test_url = self.portal_url + '/front-page/@@seo-context-properties'
        # Anonymous: can NOT ACCESS
        headers = self.publish(path=test_url).headers
        self.assertEqual(headers.get('bobo-exception-type', ""),
                         'Unauthorized', "No 'Unauthorized' exception rised " \
                         "for Anonymous on '@@seo-context-properties' view")
        # Member: can NOT ACCESS
        status = self.publish(path=test_url, basic=self.member_auth).headers
        self.assertEqual(headers.get('bobo-exception-type', ""),
                         'Unauthorized', "No 'Unauthorized' exception rised " \
                         "for Member on '@@seo-context-properties' view")
        # Editor: CAN Access
        res = self.publish(path=test_url, basic=self.editor_auth)
        self.assertEqual(res.status, 200)

    def test_tab_edit(self):
        """Editor can change SEO Properties"""
        test_url = self.portal_url + '/front-page/@@seo-context-properties'
        form_data = {'seo_title': 'New Title',
                     'seo_title_override:int': 1,
                     'form.submitted:int': 1}
        res = self.publish(path=test_url, basic=self.editor_auth,
                           request_method='POST',
                           stdin=StringIO(urllib.urlencode(form_data)))
        self.assertNotEqual(res.status, 200)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBugs))
    suite.addTest(makeSuite(TestBug24AtPloneOrg))
    return suite
