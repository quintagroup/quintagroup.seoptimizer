import urllib, re
from base import getToolByName, FunctionalTestCase, newSecurityManager
from config import *

class TestAdditionalKeywords(FunctionalTestCase):

    def afterSetUp(self):
        self.qi = self.portal.portal_quickinstaller
        self.qi.installProduct(PROJECT_NAME)
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

    def test_additional_keywords_in_configlet(self):
        quoted_keywords = urllib.quote('foo\nbar')
        path = self.portal.id+'/@@seo-controlpanel?additionalKeywords:lines=%s&form.submitted=1'%quoted_keywords
        self.publish(path, self.basic_auth)
        self.assertEqual(self.sp.additional_keywords, ('foo', 'bar'))
        self.publish(self.portal.id+'/@@seo-controlpanel?form.submitted=1', self.basic_auth)
        self.assertEqual(self.sp.additional_keywords, ())

    def test_listMetaTags_empty(self):
        metatags = self.pu.listMetaTags(self.my_doc)
        self.assert_('keywords' not in metatags)

    def test_listMetaTags_one(self):        
        self.my_doc.manage_addProperty('qSEO_keywords', ('foo',), 'lines')
        self.html = str(self.publish(self.portal.id+'/my_doc', self.basic_auth))
        m = re.match('.*<meta\ content="foo"\ name="keywords"\ />', self.html, re.S|re.M)
        if not m:
            m = re.match('.*<meta\ name="keywords"\ content="foo"\ />', self.html, re.S|re.M)
        self.assert_(m, "No 'foo' keyword find")

    def test_listMetaTags_two(self):        
        self.my_doc.manage_addProperty('qSEO_keywords', ('foo', 'bar'), 'lines')
        self.html = str(self.publish(self.portal.id+'/my_doc', self.basic_auth))
        m = re.match('.*<meta\ content="foo, bar"\ name="keywords"\ />', self.html, re.S|re.M)
        if not m:
            m = re.match('.*<meta\ name="keywords"\ content="foo, bar"\ />', self.html, re.S|re.M)
        self.assert_(m, "No 'foo, bar' keyword find")

    def test_additional_keywords_in_listMetaTags_empty(self):        
        self.sp.additional_keywords = ('foo',)
        metatags = self.pu.listMetaTags(self.my_doc)
        self.assert_('keywords' not in metatags)

    def test_additional_keywords_in_listMetaTags_one(self):
        self.my_doc.setText('<p>foo</p>')
        self.sp.additional_keywords = ('foo',)
        self.html = str(self.publish(self.portal.id+'/my_doc', self.basic_auth))
        m = re.match('.*<meta\ content="foo"\ name="keywords"\ />', self.html, re.S|re.M)
        if not m:
            m = re.match('.*<meta\ name="keywords"\ content="foo"\ />', self.html, re.S|re.M)
        self.assert_(m, "No 'foo' keyword find")

    def test_additional_keywords_in_listMetaTags_two(self):
        self.my_doc.setText('<p>foo bar</p>')
        self.sp.additional_keywords = ('foo', 'bar')
        self.html = str(self.publish(self.portal.id+'/my_doc', self.basic_auth))
        m = re.match('.*<meta\ content="foo, bar"\ name="keywords"\ />', self.html, re.S|re.M)
        if not m:
            m = re.match('.*<meta\ name="keywords"\ content="foo, bar"\ />', self.html, re.S|re.M)
        self.assert_(m, "No 'foo, bar' keyword find")

    def test_additional_keywords_in_listMetaTags_merge(self):
        self.my_doc.setText('<p>foo bar</p>')
        self.sp.additional_keywords = ('foo', 'bar')
        self.my_doc.manage_addProperty('qSEO_keywords', ('baz',), 'lines')
        self.html = str(self.publish(self.portal.id+'/my_doc', self.basic_auth))
        m = re.findall('.*(<meta\s+(?:content="(?:(?:baz|bar|foo),\s*(?:baz|foo|bar),\s*(?:baz|foo|bar)"\s*)|(?:name="keywords"\s*)){2}/>)', self.html, re.S|re.M)
        self.assert_(m, "No 'foo, bar, baz' keyword find")

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAdditionalKeywords))
    return suite
