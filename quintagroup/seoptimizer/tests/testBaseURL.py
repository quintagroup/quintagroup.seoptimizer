import re
from base import getToolByName, FunctionalTestCase, newSecurityManager
from config import *

class TestBaseURL(FunctionalTestCase):

    def afterSetUp(self):
        self.basic_auth = 'portal_manager:secret'
        uf = self.app.acl_users
        uf.userFolderAddUser('portal_manager', 'secret', ['Manager'], [])
        user = uf.getUserById('portal_manager')
        if not hasattr(user, 'aq_base'):
            user = user.__of__(uf)
        newSecurityManager(None, user)

    def test_notFolderBaseURL(self):
        my_doc = self.portal.invokeFactory('Document', id='my_doc')
        my_doc = self.portal['my_doc']
        regen = re.compile('<base\s+[^>]*href=\"([^\"]*)\"[^>]*>', re.S|re.M)

        path = "/%s" % my_doc.absolute_url(1)
        html = self.publish(path, self.basic_auth).getBody()
        burls = regen.findall(html)

        mydocurl = my_doc.absolute_url()
        self.assert_(not [1 for burl in burls if not burl==mydocurl],
           "Wrong BASE URL for document: %s, all must be: %s" % (burls, mydocurl))

    def test_folderBaseURL(self):
        my_fldr = self.portal.invokeFactory('Folder', id='my_fldr')
        my_fldr = self.portal['my_fldr']
        regen = re.compile('<base\s+[^>]*href=\"([^\"]*)\"[^>]*>', re.S|re.M)
        
        path = "/%s" % my_fldr.absolute_url(1)
        html = self.publish(path, self.basic_auth).getBody()
        burls = regen.findall(html)

        myfldrurl = my_fldr.absolute_url() + '/'
        self.assert_(not [1 for burl in burls if not burl==myfldrurl],
           "Wrong BASE URL for folder: %s , all must be : %s" % (burls, myfldrurl))

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBaseURL))
    return suite
