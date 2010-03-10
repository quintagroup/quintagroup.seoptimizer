import urllib, re
from cStringIO import StringIO
from base import *

CUSTOM_METATAGS = [{'meta_name'    : 'metatag1',
                    'meta_content' : 'metatag1value'},
                   {'meta_name'    : 'metatag2',
                    'meta_content' : 'metatag2value'},
                   {'meta_name'    : 'metatag3',
                    'meta_content' : ''}
                  ]

VIEW_METATAGS = ['DC.creator', 'DC.format', 'DC.date.modified',
    'DC.date.created', 'DC.type', 'DC.distribution', 'description',
    'keywords', 'robots', 'distribution']

GLOBAL_CUSTOM_METATAGS = {
    'default_custom_metatags':'metatag1|global_metatag1value\nmetatag4|global_metatag4value'}

class TestResponse(FunctionalTestCase):

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
        my_doc = self.portal.invokeFactory('Document', id='my_doc')
        my_doc = self.portal['my_doc']
        self.canonurl = 'http://nohost/plone/test.html'
        self.sp.manage_changeProperties(**GLOBAL_CUSTOM_METATAGS)
        self.sp.manage_changeProperties(settings_use_keywords_sg=3, settings_use_keywords_lg=2)
        abs_path = "/%s" % my_doc.absolute_url(1)
        self.form_data = {'seo_description': 'it is description, test keyword1', 'seo_keywords_override:int': 1, 'seo_custommetatags_override:int': 1,
                        'seo_robots_override:int': 1, 'seo_robots': 'ALL', 'seo_description_override:int': 1, 'seo_canonical_override:int': 1,
                        'seo_keywords:list': 'keyword1', 'seo_html_comment': 'no comments',
                        'seo_title_override:int': 1, 'seo_title': 'hello world', 'seo_html_comment_override:int': 1,
                        'seo_distribution_override:int': 1, 'seo_distribution': 'Global', 'seo_canonical': self.canonurl, 'form.submitted:int': 1}
        st = ''
        for d in CUSTOM_METATAGS:
            st += '&seo_custommetatags.meta_name:records=%s&seo_custommetatags.meta_content:records=%s' % (d['meta_name'],d['meta_content'])
        self.publish(path=abs_path+'/@@seo-context-properties', basic=self.basic_auth, request_method='POST', stdin=StringIO(urllib.urlencode(self.form_data)+st))
        #self.publish(abs_path+'/@@seo-context-properties?%s' % urllib.urlencode(self.form_data), self.basic_auth)

        wf_tool = self.portal.portal_workflow
        wf_tool.doActionFor(my_doc, 'publish')

        self.abs_path = abs_path
        self.my_doc = my_doc
        self.html = self.publish(abs_path, self.basic_auth).getBody()

        # now setup page with title equal to plone site's title
        my_doc2 = self.portal.invokeFactory('Document', id='my_doc2')
        my_doc2 = self.portal['my_doc2']
        my_doc2.update(title=self.portal.Title())
        wf_tool.doActionFor(my_doc2, 'publish')
        abs_path2 = "/%s" % my_doc2.absolute_url(1)
        self.html2 = self.publish(abs_path2, self.basic_auth).getBody()

    def testTitle(self):
        m = re.match('.*<title>\\s*hello world\\s*</title>', self.html, re.S|re.M)
        self.assert_(m, 'Title not set in')

    def testTitleDuplication(self):
        """If we are not overriding page title and current page title equals title of the plone site
        then there should be no concatenation of both titles. Only one should be displayed.
        """
        m = re.match('.*<title>\\s*%s\\s*</title>' % self.portal.Title(), self.html2, re.S|re.M)
        self.assert_(m, 'Title is not set correctly, perhaps it is duplicated with plone site title')

    def testDescription(self):
        m = re.match('.*(<meta\s+(?:(?:name="description"\s*)|(?:content="it is description, test keyword1"\s*)){2}/>)', self.html, re.S|re.M)
        self.assert_(m, 'Description not set in')

    def testKeywords(self):
        m = re.match('.*(<meta\s+(?:(?:name="keywords"\s*)|(?:content="keyword1"\s*)){2}/>)', self.html, re.S|re.M)
        self.assert_(m, 'Keywords not set in')

    def testRobots(self):
        m = re.match('.*(<meta\s+(?:(?:name="robots"\s*)|(?:content="ALL"\s*)){2}/>)', self.html, re.S|re.M)
        self.assert_(m, 'Robots not set in')

    def testDistribution(self):
        m = re.match('.*(<meta\s+(?:(?:name="distribution"\s*)|(?:content="Global"\s*)){2}/>)', self.html, re.S|re.M)
        self.assert_(m, 'Distribution not set in')

    def testHTMLComments(self):
        m = re.match('.*<!--\\s*no comments\\s*-->', self.html, re.S|re.M)
        self.assert_(m, 'Comments not set in')

    def testTagsOrder(self):
        metatags_order = [t for t in self.sp.getProperty('metatags_order') if t in VIEW_METATAGS]
        m = re.search('.*'.join(['<meta.*name="%s".*/>' %t for t in metatags_order]), self.html, re.S|re.M)
        self.assert_(m, "Meta tags order not supported.")

        metatags_order.reverse()
        m = re.search('.*'.join(['<meta.*name="%s".*/>' %t for t in metatags_order]), self.html, re.S|re.M)
        self.assertFalse(m, "Meta tags order not supported.")

        self.sp.manage_changeProperties(**{'metatags_order':metatags_order})
        html = self.publish(self.abs_path, self.basic_auth).getBody()
        m = re.search('.*'.join(['<meta.*name="%s".*/>' %t for t in metatags_order]), self.html, re.S|re.M)
        self.assertFalse(m, "Meta tags order not supported.")

        m = re.search('.*'.join(['<meta.*name="%s".*/>' %t for t in metatags_order]), html, re.S|re.M)
        self.assert_(m, "Meta tags order not supported.")


    def testCustomMetaTags(self):
        for tag in CUSTOM_METATAGS:
            m = re.match('.*(<meta\s+(?:(?:name="%(meta_name)s"\s*)|(?:content="%(meta_content)s"\s*)){2}/>)' % tag, self.html, re.S|re.M)
            if tag['meta_content']:
                self.assert_(m, "Custom meta tag %s not applied." % tag['meta_name'])
            else:
                self.assert_(not m, "Meta tag %s has no content, but is present in the page." % tag['meta_name'])
        m = re.match('.*(<meta\s+(?:(?:name="metatag4"\s*)|(?:content="global_metatag4value"\s*)){2}/>)', self.html, re.S|re.M)
        self.assert_(m, "Global custom meta tag %s not applied." % 'metatag4')

    def testDeleteCustomMetaTags(self):
        self.sp.manage_changeProperties(**{'default_custom_metatags':'metatag1|global_metatag1value'})
        my_doc = self.my_doc
        self.form_data = {'seo_custommetatags': CUSTOM_METATAGS,  'seo_custommetatags_override:int': 0, 'form.submitted:int': 1}
        self.publish(path=self.abs_path+'/@@seo-context-properties', basic=self.basic_auth, request_method='POST', stdin=StringIO(urllib.urlencode(self.form_data)))
        self.html = self.publish(self.abs_path, self.basic_auth).getBody()
        m = re.match('.*(<meta\s+(?:(?:name="metatag4"\s*)|(?:content="global_metatag4value"\s*)){2}/>)', self.html, re.S|re.M)
        self.assert_(not m, "Global custom meta tag %s is prosent in the page." % 'metatag4')
        m = re.match('.*(<meta\s+(?:(?:name="metatag1"\s*)|(?:content="global_metatag1value"\s*)){2}/>)', self.html, re.S|re.M)
        self.assert_(m, "Global custom meta tag %s not applied." % 'metatag1')

    def testCanonical(self):
        m = re.match('.*<link rel="canonical" href="%s" />' % self.canonurl, self.html, re.S|re.M)
        self.assert_(m, self.canonurl)

    def testDefaultCanonical(self):
        """Default canonical url mast add document absolute_url
        """
        # Delete custom canonical url
        my_doc = self.portal['my_doc']
        my_doc._delProperty(id='qSEO_canonical')
        # Get document without customized canonical url
        abs_path = "/%s" % my_doc.absolute_url(1)
        self.html = self.publish(abs_path, self.basic_auth).getBody()

        my_url = my_doc.absolute_url()
        m = re.match('.*<link rel="canonical" href="%s" />' % my_url, self.html, re.S|re.M)
        self.assert_(m, my_url)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestResponse))
    return suite
