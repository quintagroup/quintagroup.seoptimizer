import urllib
from cStringIO import StringIO

from zope.component import getMultiAdapter
from zope.component import providedBy
from zope.interface import directlyProvides
from zope.viewlet.interfaces import IViewlet, IViewletManager
from zope.publisher.browser import TestRequest

from quintagroup.seoptimizer.browser.interfaces import IPloneSEOLayer
from base import *


class TestBugs(FunctionalTestCase):

    def afterSetUp(self):
        self.basic_auth = ':'.join((portal_owner,default_password))
        self.loginAsPortalOwner()
        # prepare test document
        my_doc = self.portal.invokeFactory('Document', id='my_doc')
        self.my_doc = self.portal['my_doc']
        self.abs_path = "/%s" % self.my_doc.absolute_url(1)

    def test_modification_date(self):
        """ Modification date changing on SEO properties edit """
        form_data = {'seo_title': 'New Title',
                     'seo_title_override:int': 1,
                     'form.submitted:int': 1}

        md_before = self.my_doc.modification_date
        self.publish(path=self.abs_path+'/@@seo-context-properties',
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



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBugs))
    return suite
