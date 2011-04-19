"""Test setup for integration and functional tests.

When we import PloneTestCase and then call setupPloneSite(), all of
Plone's products are loaded, and a Plone site will be created. This
happens at module level, which makes it faster to run each test, but
slows down test runner startup.
"""
import transaction
from zope.component import getUtility

# Starting from plone.memoize v1.1a4 (used in plone4), global ram cache
# utility provides other IRAMCache interface, than before
try:
    # In plone4 provides
    from zope.ramcache.interfaces.ram import IRAMCache
    IRAMCache
except ImportError:
    # In plone3 provides
    from zope.app.cache.interfaces.ram import IRAMCache

from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase import setup as ptc_setup

from quintagroup.seoptimizer.config import PROJECT_NAME

ptc.setupPloneSite()


class NotInstalled(PloneSite):
    """ Only package register, without installation into portal
    """

    @classmethod
    def setUp(cls):
        fiveconfigure.debug_mode = True
        import quintagroup.seoptimizer
        zcml.load_config('configure.zcml', quintagroup.seoptimizer)
        fiveconfigure.debug_mode = False
        ztc.installPackage(PROJECT_NAME)


class Installed(NotInstalled):
    """ Install product into the portal
    """
    @classmethod
    def setUp(cls):
        app = ztc.app()
        portal = app[ptc_setup.portal_name]

        # Sets the local site/manager
        ptc_setup._placefulSetUp(portal)
        # Install PROJECT
        qi = getattr(portal, 'portal_quickinstaller', None)
        if not ptc.PLONE31:
            qi.installProduct("plone.browserlayer")
        qi.installProduct(PROJECT_NAME)
        transaction.commit()

    @classmethod
    def tearDown(cls):
        ptc_setup._placefulTearDown()


class MixinTestCase:

    def _getauth(self):
        # Fix authenticator for the form
        import re
        try:
            authenticator = self.portal.restrictedTraverse("@@authenticator")
        except:
            handle = ""
        else:
            html = authenticator.authenticator()
            handle = re.search('value="(.*)"', html).groups()[0]
        return handle

    def beforeTearDown(self):
        getUtility(IRAMCache).invalidateAll()

    def installBrowserLayer(self):
        if not ptc.PLONE31:
            qi = getattr(self.portal, 'portal_quickinstaller', None)
            qi.installProduct("plone.browserlayer")


class TestCase(MixinTestCase, ptc.PloneTestCase):
    layer = Installed


class TestCaseNotInstalled(MixinTestCase, ptc.PloneTestCase):
    layer = NotInstalled


class FunctionalTestCase(MixinTestCase, ptc.FunctionalTestCase):
    layer = Installed

    def afterSetUp(self):
        self.installBrowserLayer()


class FunctionalTestCaseNotInstalled(MixinTestCase, ptc.FunctionalTestCase):
    layer = NotInstalled

    def afterSetUp(self):
        self.installBrowserLayer()
