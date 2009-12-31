import re
from base import getToolByName, FunctionalTestCase, newSecurityManager
from config import *

class TestMetaTagsDuplication(FunctionalTestCase):

    def afterSetUp(self):
        self.qi = self.portal.portal_quickinstaller
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
        self.my_doc.update(description="Document description")

    def test_GeneratorMeta(self):
        # Get document without customized canonical url
        abs_path = "/%s" % self.my_doc.absolute_url(1)
        regen = re.compile('<meta\s+[^>]*name=\"generator\"[^>]*>', re.S|re.M)

        # Before product installation
        html = self.publish(abs_path, self.basic_auth).getBody()
        lengen = len(regen.findall(html))
        self.assert_(lengen==1, "There is %d generator meta tag(s) " \
           "before seoptimizer installation" % lengen)

#         # After PROJECT_NAME installation
#         self.qi.installProduct(PROJECT_NAME)
#         html = self.publish(abs_path, self.basic_auth).getBody()
#         lengen = len(regen.findall(html))
#         self.assert_(lengen==1, "There is %d generator meta tag(s) " \
#            "after seoptimizer installation" % lengen)

    def test_DescriptionMeta(self):
        # Get document without customized canonical url
        abs_path = "/%s" % self.my_doc.absolute_url(1)
        regen = re.compile('<meta\s+[^>]*name=\"description\"[^>]*>', re.S|re.M)

        # Before product installation
        html = self.publish(abs_path, self.basic_auth).getBody()
        lendesc = len(regen.findall(html))
        self.assert_(lendesc==1, "There is %d DESCRIPTION meta tag(s) " \
           "before seoptimizer installation" % lendesc)

#         # After PROJECT_NAME installation
#         self.qi.installProduct(PROJECT_NAME)
#         html = self.publish(abs_path, self.basic_auth).getBody()
#         lendesc = len(regen.findall(html))
#         self.assert_(lendesc==1, "There is %d DESCRIPTION meta tag(s) " \
#            "after seoptimizer installation" % lendesc)
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMetaTagsDuplication))
    return suite
