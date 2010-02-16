import urllib, re
from Acquisition import aq_inner
from base import getToolByName, FunctionalTestCase, newSecurityManager
from config import *

class TestUsageKeywords(FunctionalTestCase):

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

    def test_default_values_radiobutton_in_configlet(self):
        self.assertEqual(self.sp.getProperty('settings_use_keywords_sg', 0), 3)
        self.assertEqual(self.sp.getProperty('settings_use_keywords_lg', 0), 2)

    def test_changes_using_keywords_in_configlet(self):
        for sg, lg in ((1, 1), (1, 2), (2, 1), (2, 2), (3, 1), (3, 2)):
            path = self.portal.id+'/@@seo-controlpanel?settingsUseKeywordsSG=%s'\
                                '&settingsUseKeywordsLG=%s&form.submitted=1' % (sg, lg)
            self.publish(path, self.basic_auth)
            self.assertEqual(self.sp.getProperty('settings_use_keywords_sg', 0), sg)
            self.assertEqual(self.sp.getProperty('settings_use_keywords_lg', 0), lg)

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
        self.my_doc.setText('<p>foo</p>')
        self.sp.manage_changeProperties(settings_use_keywords_sg=3, settings_use_keywords_lg=2)
        self.my_doc.manage_addProperty('qSEO_keywords', ('foo',), 'lines')
        self.html = str(self.publish(self.portal.id+'/my_doc', self.basic_auth))
        m = re.match('.*(<meta\s+(?:(?:name="keywords"\s*)|(?:content="foo"\s*)){2}/>)', self.html, re.S|re.M)
        self.assert_(m, "No 'foo' keyword find")

    def test_listMetaTags_two(self):
        self.my_doc.setText('<p>foo bar</p>')
        self.sp.manage_changeProperties(settings_use_keywords_sg=3, settings_use_keywords_lg=2)
        self.my_doc.manage_addProperty('qSEO_keywords', ('foo', 'bar'), 'lines')
        self.html = str(self.publish(self.portal.id+'/my_doc', self.basic_auth))
        m = re.match('.*(<meta\s+(?:(?:name="keywords"\s*)|(?:content="(?:foo|bar),\s*(?:foo|bar)"\s*)){2}/>)',
                     self.html, re.S|re.M)
        self.assert_(m, "No 'foo, bar' keyword find")

    def test_additional_keywords_in_listMetaTags_empty(self):
        self.sp.manage_changeProperties(settings_use_keywords_sg=3, settings_use_keywords_lg=2)
        self.sp.additional_keywords = ('foo',)
        metatags = self.pu.listMetaTags(self.my_doc)
        self.assert_('keywords' not in metatags)

    def test_additional_keywords_in_listMetaTags_one(self):
        self.my_doc.setText('<p>foo</p>')
        self.sp.manage_changeProperties(settings_use_keywords_sg=3, settings_use_keywords_lg=2)
        self.sp.additional_keywords = ('foo',)
        self.html = str(self.publish(self.portal.id+'/my_doc', self.basic_auth))
        m = re.match('.*(<meta\s+(?:(?:name="keywords"\s*)|(?:content="foo"\s*)){2}/>)', self.html, re.S|re.M)
        self.assert_(m, "No 'foo' keyword find")

    def test_additional_keywords_in_listMetaTags_two(self):
        self.my_doc.setText('<p>foo bar</p>')
        self.sp.manage_changeProperties(settings_use_keywords_sg=3, settings_use_keywords_lg=2)
        self.sp.additional_keywords = ('foo', 'bar')
        self.html = str(self.publish(self.portal.id+'/my_doc', self.basic_auth))
        m = re.match('.*(<meta\s+(?:(?:name="keywords"\s*)|(?:content="(?:foo|bar),\s*(?:foo|bar)"\s*)){2}/>)',
                    self.html, re.S|re.M)
        self.assert_(m, "No 'foo, bar' keyword find")

    def setup_testing_render_keywords(self, html='<p>global local subject</p>'):
        self.my_doc.setText(html)
        self.sp.additional_keywords = (('global',))
        self.my_doc.manage_addProperty('qSEO_keywords', ('local'), 'lines')
        aq_inner(self.my_doc).aq_explicit.setSubject('subject')
        html = str(self.publish(self.portal.id+'/my_doc', self.basic_auth))
        return html

    def test_render_only_subject(self):
        self.sp.manage_changeProperties(settings_use_keywords_sg=1, settings_use_keywords_lg=1)
        self.html = self.setup_testing_render_keywords()
        m = re.match('.*(<meta\s+(?:(?:name="keywords"\s*)|(?:content="subject"\s*)){2}/>)', self.html, re.S|re.M)
        self.assert_(m, "No 'subject' keyword find")

    def test_render_subject_and_local_seokeywords(self):
        self.sp.manage_changeProperties(settings_use_keywords_sg=1, settings_use_keywords_lg=2)
        self.html = self.setup_testing_render_keywords()
        m = re.match('.*(<meta\s+(?:(?:name="keywords"\s*)|(?:content="(?:subject|local),\s*(?:subject|local)"\s*)){2}/>)',
                    self.html, re.S|re.M)
        self.assert_(m, "No 'subject, local' keywords find")

    def test_render_only_global_seokeywords(self):
        self.sp.manage_changeProperties(settings_use_keywords_sg=2, settings_use_keywords_lg=1)
        self.html = self.setup_testing_render_keywords()
        m = re.match('.*(<meta\s+(?:(?:name="keywords"\s*)|(?:content="global"\s*)){2}/>)', self.html, re.S|re.M)
        self.assert_(m, "No 'global' keyword find")

    def test_render_global_and_local_seokeywords(self):
        self.sp.manage_changeProperties(settings_use_keywords_sg=2, settings_use_keywords_lg=2)
        self.html = self.setup_testing_render_keywords()
        m = re.match('.*(<meta\s+(?:(?:name="keywords"\s*)|(?:content="(?:global|local),\s*(?:global|local)"\s*)){2}/>)',
                    self.html, re.S|re.M)
        self.assert_(m, "No 'global, local' keywords find")

    def test_render_subject_and_global_seokeywords(self):
        self.sp.manage_changeProperties(settings_use_keywords_sg=3, settings_use_keywords_lg=1)
        self.html = self.setup_testing_render_keywords()
        m = re.match('.*(<meta\s+(?:(?:name="keywords"\s*)|(?:content="(?:subject|global),\s*(?:subject|global)"\s*)){2}/>)',
                    self.html, re.S|re.M)
        self.assert_(m, "No 'subject, global' keywords find")

    def test_render_subject_and_global_and_local_seokeywords(self):
        self.sp.manage_changeProperties(settings_use_keywords_sg=3, settings_use_keywords_lg=2)
        self.html = self.setup_testing_render_keywords()
        m = re.match('.*(<meta\s+(?:(?:name="keywords"\s*)|(?:content="(?:subject|global|local),\s*(?:subject|global|local),\s*(?:subject|global|local)"\s*)){2}/>)',
                    self.html, re.S|re.M)
        self.assert_(m, "No 'subject, global, local' keywords find")

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUsageKeywords))
    return suite
