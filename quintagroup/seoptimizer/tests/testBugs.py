import urllib, re
from cStringIO import StringIO
from base import *

class TestBugs(FunctionalTestCase):

    def afterSetUp(self):
        self.basic_auth = 'portal_manager:secret'
        uf = self.app.acl_users
        uf.userFolderAddUser('portal_manager', 'secret', ['Manager'], [])
        user = uf.getUserById('portal_manager')
        if not hasattr(user, 'aq_base'):
            user = user.__of__(uf)
        newSecurityManager(None, user)

    def test_modification_date(self):
        """ Modification date changing on SEO properties edit """
        my_doc = self.portal.invokeFactory('Document', id='my_doc')
        my_doc = self.portal['my_doc']

        md_before = my_doc.modification_date
        abs_path = "/%s" % my_doc.absolute_url(1)
        form_data = {'seo_title': 'New Title',  'seo_title_override:int': 1, 'form.submitted:int': 1}
        self.publish(path=abs_path+'/@@seo-context-properties', basic=self.basic_auth, request_method='POST', stdin=StringIO(urllib.urlencode(form_data)))
        md_after = my_doc.modification_date
        self.assertNotEqual(md_before, md_after)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBugs))
    return suite
