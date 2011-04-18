import urllib
from cStringIO import StringIO

from quintagroup.seoptimizer.tests.base import FunctionalTestCase, \
    IRAMCache, getUtility
from Products.PloneTestCase.PloneTestCase import portal_owner, \
    default_password
import re

CUSTOM_METATAGS = [
   {'meta_name': 'metatag1', 'meta_content': 'metatag1value'},
   {'meta_name': 'metatag2', 'meta_content': 'metatag2value'},
   {'meta_name': 'metatag3', 'meta_content': ''}
]

VIEW_METATAGS = [
    'DC.creator', 'DC.format', 'DC.date.modified',
    'DC.date.created', 'DC.type', 'DC.distribution',
    'description', 'keywords', 'robots', 'distribution'
]

FORM = {
    'seo_robots': 'ALL',
    'form.submitted:int': 1,
    'form.button.Save': "Save",
    'seo_title': 'hello world',
    'seo_title_override:int': 1,
    'seo_robots_override:int': 1,
    'seo_distribution': 'Global',
    'seo_keywords_override:int': 1,
    'seo_keywords:list': 'keyword1',
    'seo_description_override:int': 1,
    'seo_html_comment': 'no comments',
    'seo_html_comment_override:int': 1,
    'seo_distribution_override:int': 1,
    'seo_custommetatags_override:int': 1,
    'seo_description': 'it is description, test keyword1',
}

METATAG = '.*(<meta\s+(?:(?:name="%s"\s*)|(?:content="%s"\s*)){2}/>)'


class TestContextForm(FunctionalTestCase):

    def afterSetUp(self):
        self.sp = self.portal.portal_properties.seo_properties
        self.pu = self.portal.plone_utils
        self.wf = self.portal.portal_workflow

        self.basic_auth = ':'.join((portal_owner, default_password))
        self.loginAsPortalOwner()

        # Preparation for functional testing'
        # create document for test
        my_doc = self.portal.invokeFactory('Document', id='my_doc')
        my_doc = self.portal['my_doc']
        self.abs_path = "/%s" % my_doc.absolute_url(1)
        # prepare seo context form data
        self.sp.manage_changeProperties(default_custom_metatags='metatag1|' \
                                        'global_metatag1value\nmetatag4|' \
                                        'global_metatag4value')
        st = ''
        for d in CUSTOM_METATAGS:
            st += '&seo_custommetatags.meta_name:records=%s' % d['meta_name']
            st += '&seo_custommetatags.meta_content:records=%s' \
                  % d['meta_content']
        # update seo properties for the test document and publish it
        self.publish(path=self.abs_path + '/@@seo-context-properties',
                     basic=self.basic_auth, request_method='POST',
                     stdin=StringIO(urllib.urlencode(FORM) + st))
        self.wf.doActionFor(my_doc, 'publish')
        # get html view of test document
        self.html = self.publish(self.abs_path, self.basic_auth).getBody()

    def testTitle(self):
        m = re.match('.*<title>\\s*hello world\\s*</title>', self.html,
                     re.S | re.M)
        self.assert_(m, 'Title not set in')

    def testTitleDuplication(self):
        """If we are not overriding page title and current page title equals
           title of the plone site then there should be no concatenation of
           both titles. Only one should be displayed.
        """
        # setup page with title equal to plone site's title
        my_doc2 = self.portal.invokeFactory('Document', id='my_doc2',
                                            title=self.portal.Title())
        my_doc2 = self.portal['my_doc2']
        self.wf.doActionFor(my_doc2, 'publish')
        html2 = self.publish('/' + my_doc2.absolute_url(1),
                             self.basic_auth).getBody()

        m = re.match('.*<title>\\s*%s\\s*</title>' % self.portal.Title(),
                     html2, re.S | re.M)
        self.assert_(m, 'Title is not set correctly, perhaps it is ' \
                     'duplicated with plone site title')

    def testDescription(self):
        m = re.match(METATAG % ("description", FORM['seo_description']),
                     self.html, re.S | re.M)
        self.assert_(m, 'Description not set in')

    def testRobots(self):
        m = re.match(METATAG % ("robots", FORM['seo_robots']), self.html,
                     re.S | re.M)
        self.assert_(m, 'Robots not set in')

    def testDistribution(self):
        m = re.match(METATAG % ("distribution", FORM['seo_distribution']),
                     self.html, re.S | re.M)
        self.assert_(m, 'Distribution not set in')

    def testHTMLComments(self):
        m = re.match('.*<!--\\s*no comments\\s*-->', self.html, re.S | re.M)
        self.assert_(m, 'Comments not set in')

    def testTagsOrder(self):
        def is_match(html, mtorder):
            return re.search('.*'.join(['<meta.*name="%s".*/>' % t \
                                        for t in mtorder]), html, re.S | re.M)

        metatags_order = [t for t in self.sp.getProperty('metatags_order') \
                            if t in VIEW_METATAGS]
        self.assert_(is_match(self.html, metatags_order),
                     "Meta tags order not supported.")

        metatags_order.reverse()
        self.assertFalse(is_match(self.html, metatags_order),
                         "Meta tags order not supported.")

        self.sp.manage_changeProperties(metatags_order=metatags_order)
        self.assertFalse(is_match(self.html, metatags_order),
                         "Meta tags order not supported.")

        html = self.publish(self.abs_path, self.basic_auth).getBody()
        self.assert_(is_match(html, metatags_order),
                     "Meta tags order not supported.")

    def testCustomMetaTags(self):
        for tag in CUSTOM_METATAGS:
            m = re.match(METATAG % (tag['meta_name'], tag['meta_content']),
                         self.html, re.S | re.M)
            if tag['meta_content']:
                self.assert_(m, "Custom meta tag %s not applied." \
                             % tag['meta_name'])
            else:
                self.assert_(not m, "Meta tag %s has no content, but is " \
                             "present: in the page." % tag['meta_name'])

        m = re.match(METATAG % ("metatag4", "global_metatag4value"), self.html,
                     re.S | re.M)
        self.assert_(m, "Global custom meta tag %s not applied." % 'metatag4')

    def testDeleteCustomMetaTags(self):
        self.sp.manage_changeProperties(default_custom_metatags='metatag1|' \
                                        'global_metatag1value')
        form_data = {'seo_custommetatags': CUSTOM_METATAGS,
                     'seo_custommetatags_override:int': 0,
                     'form.button.Save': "Save",
                     'form.submitted:int': 1}

        # Clean-up ram cache
        getUtility(IRAMCache).invalidateAll()

        self.publish(path=self.abs_path + '/@@seo-context-properties',
                     basic=self.basic_auth, request_method='POST',
                     stdin=StringIO(urllib.urlencode(form_data)))
        html = self.publish(self.abs_path, self.basic_auth).getBody()

        m = re.match(METATAG % ("metatag4", "global_metatag4value"), html,
                     re.S | re.M)
        self.assert_(not m, "Global custom meta tag %s is prosent in the " \
                     "page." % 'metatag4')

        m = re.match(METATAG % ("metatag1", "global_metatag1value"), html,
                     re.S | re.M)
        self.assert_(m, "Global custom meta tag %s not applied." % 'metatag1')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestContextForm))
    return suite
