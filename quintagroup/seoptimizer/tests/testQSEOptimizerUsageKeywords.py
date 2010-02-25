import urllib, re
from Acquisition import aq_inner
from base import getToolByName, FunctionalTestCase, newSecurityManager
from config import *


class TestUsageKeywords(FunctionalTestCase):

    def afterSetUp(self):
        self.sp = self.portal.portal_properties.seo_properties
        self.pu = self.portal.plone_utils

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

    def test_listMetaTags_empty(self):
        metatags = self.pu.listMetaTags(self.my_doc)
        self.assert_('keywords' not in metatags)

    def test_listMetaTags_one(self):
        self.my_doc.setText('<p>foo</p>')
        self.my_doc.manage_addProperty('qSEO_keywords', ('foo',), 'lines')
        self.html = str(self.publish(self.portal.id+'/my_doc', self.basic_auth))
        m = re.match('.*(<meta\s+(?:(?:name="keywords"\s*)|(?:content="foo"\s*)){2}/>)', self.html, re.S|re.M)
        self.assert_(m, "No 'foo' keyword find")

    def test_listMetaTags_two(self):
        self.my_doc.setText('<p>foo bar</p>')
        self.my_doc.manage_addProperty('qSEO_keywords', ('foo', 'bar'), 'lines')
        self.html = str(self.publish(self.portal.id+'/my_doc', self.basic_auth))
        m = re.match('.*(<meta\s+(?:(?:name="keywords"\s*)|(?:content="(?:foo|bar),\s*(?:foo|bar)"\s*)){2}/>)',
                     self.html, re.S|re.M)
        self.assert_(m, "No 'foo, bar' keyword find")

    def setup_testing_render_keywords(self, keywords=('local',),
                                      html='<p>local subject</p>'):
        self.my_doc.setText(html)
        if len(keywords):
            self.my_doc.manage_addProperty('qSEO_keywords', keywords, 'lines')
        aq_inner(self.my_doc).aq_explicit.setSubject('subject')
        html = str(self.publish(self.portal.id+'/my_doc', self.basic_auth))
        return html

    def test_render_only_subject(self):
        self.html = self.setup_testing_render_keywords(keywords=())
        m = re.match('.*(<meta\s+(?:(?:name="keywords"\s*)|(?:content="subject"\s*)){2}/>)', self.html, re.S|re.M)
        self.assert_(m, "No 'subject' keyword find")

    def test_render_only_local_seokeywords(self):
        self.html = self.setup_testing_render_keywords()
        m = re.match('.*(<meta\s+(?:(?:name="keywords"\s*)|(?:content="local\s*"\s*)){2}/>)', self.html, re.S|re.M)
        self.assert_(m, "No 'local' keywords find")


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUsageKeywords))
    return suite
