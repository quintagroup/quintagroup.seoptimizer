from quintagroup.seoptimizer.tests.base import FunctionalTestCase, \
    FunctionalTestCaseNotInstalled
import re

GENERATOR = re.compile('.*(<meta\s+(?:(?:name="generator"\s*)|' \
                       '(?:content=".*?"\s*)){2}/>)', re.S | re.M)
DESCRIPTION = re.compile('.*(<meta\s+(?:(?:name="description"\s*)|' \
                         '(?:content=".*?"\s*)){2}/>)', re.S | re.M)


class InstallMixin:

    def prepare(self):
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


class TestTagsDuplicationInstalled(InstallMixin, FunctionalTestCase):

    def afterSetUp(self):
        self.prepare()

    def test_GeneratorMetaSEOInstalled(self):
        lengen = len(GENERATOR.findall(self.html))
        self.assert_(lengen == 1, "There is %d generator meta tag(s) " \
           "when seoptimizer installed" % lengen)

    def test_DescriptionMetaSEOInstalled(self):
        lendesc = len(DESCRIPTION.findall(self.html))
        self.assert_(lendesc == 1, "There is %d DESCRIPTION meta tag(s) " \
           "when seoptimizer installed" % lendesc)


class TestTagsDuplicationNotInstalled(InstallMixin,
                                      FunctionalTestCaseNotInstalled):

    def afterSetUp(self):
        self.prepare()

    def test_GeneratorMetaSEOUninstalled(self):
        lengen = len(GENERATOR.findall(self.html))
        self.assert_(lengen <= 1, "There is %d generator meta tag(s) " \
            "when seoptimizer uninstalled" % lengen)

    def test_DescriptionMetaSEOUninstalled(self):
        lendesc = len(DESCRIPTION.findall(self.html))
        self.assert_(lendesc == 1, "There is %d DESCRIPTION meta tag(s) " \
           "when seoptimizer uninstalled" % lendesc)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTagsDuplicationInstalled))
    suite.addTest(makeSuite(TestTagsDuplicationNotInstalled))
    return suite
