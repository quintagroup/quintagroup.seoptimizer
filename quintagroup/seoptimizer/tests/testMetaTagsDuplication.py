import re
from base import *

GENERATOR = re.compile('.*(<meta\s+(?:(?:name="generator"\s*)|' \
                       '(?:content=".*?"\s*)){2}/>)', re.S|re.M)
DESCRIPTION = re.compile('.*(<meta\s+(?:(?:name="description"\s*)|' \
                         '(?:content=".*?"\s*)){2}/>)', re.S|re.M)

class TestMetaTagsDuplication(FunctionalTestCase):

    def afterSetUp(self):
        self.qi = self.portal.portal_quickinstaller
        # Preparation for functional testing
        self.loginAsPortalOwner()
        self.my_doc = self.portal.invokeFactory('Document', id='my_doc')
        self.my_doc = self.portal['my_doc']
        self.my_doc.update(description="Document description")
        self.portal.portal_workflow.doActionFor(self.my_doc, 'publish')
        self.logout()
        # Get document without customized canonical url
        self.abs_path = "/%s" % self.my_doc.absolute_url(1)
        self.html = self.publish(self.abs_path).getBody()

    def test_GeneratorMetaSEOInstalled(self):
        lengen = len(GENERATOR.findall(self.html))
        self.assert_(lengen==1, "There is %d generator meta tag(s) " \
           "when seoptimizer installed" % lengen)
 
    def test_GeneratorMetaSEOUninstalled(self):
        self.qi.uninstallProducts([PROJECT_NAME,])
        lengen = len(GENERATOR.findall(self.html))
        self.assert_(lengen<=1, "There is %d generator meta tag(s) " \
            "when seoptimizer uninstalled" % lengen)

    def test_DescriptionMetaSEOInstalled(self):
        lendesc = len(DESCRIPTION.findall(self.html))
        self.assert_(lendesc==1, "There is %d DESCRIPTION meta tag(s) " \
           "when seoptimizer installed" % lendesc)

    def test_DescriptionMetaSEOUninstalled(self):
        self.qi.uninstallProducts([PROJECT_NAME,])
        lendesc = len(DESCRIPTION.findall(self.html))
        self.assert_(lendesc==1, "There is %d DESCRIPTION meta tag(s) " \
           "when seoptimizer uninstalled" % lendesc)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMetaTagsDuplication))
    return suite
