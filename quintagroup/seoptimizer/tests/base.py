"""Test setup for integration and functional tests.

When we import PloneTestCase and then call setupPloneSite(), all of
Plone's products are loaded, and a Plone site will be created. This
happens at module level, which makes it faster to run each test, but
slows down test runner startup.
"""
import re
import transaction
from zope.component import getUtility
from zope.app.cache.interfaces.ram import IRAMCache

from AccessControl.SecurityManagement import newSecurityManager

from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.CMFCore.utils import getToolByName

from Products.PloneTestCase.layer import onsetup, PloneSite
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase import setup as ptc_setup

from Products.PloneTestCase.PloneTestCase import portal_owner
from Products.PloneTestCase.PloneTestCase import default_user
from Products.PloneTestCase.PloneTestCase import default_password

from quintagroup.seoptimizer.config import *

ptc.setupPloneSite()

class NotInstalled(PloneSite):
    """ Only package register, without installation into portal
    """

    @classmethod
    def setUp(cls):
        fiveconfigure.debug_mode = True
        import quintagroup.seoptimizer
        zcml.load_config('configure.zcml', quintagroup.seoptimizer)
        #zcml.load_config('overrides.zcml', quintagroup.seoptimizer)
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
        qi.installProduct(PROJECT_NAME)
        transaction.commit()

    @classmethod
    def tearDown(cls):
        ptc_setup._placefulTearDown()
        

class MixinTestCase:

    def _getauth(self):
        # Fix authenticator for the form
        import re

        authenticator = self.portal.restrictedTraverse("@@authenticator")
        html = authenticator.authenticator()
        handle = re.search('value="(.*)"', html).groups()[0]
        return handle

    def beforeTearDown(self):
        getUtility(IRAMCache).invalidateAll()


class TestCase(MixinTestCase, ptc.PloneTestCase):
    layer = Installed

class TestCaseNotInstalled(MixinTestCase, ptc.PloneTestCase):
    layer = NotInstalled


class FunctionalTestCase(MixinTestCase, ptc.FunctionalTestCase):
    layer = Installed

class FunctionalTestCaseNotInstalled(MixinTestCase, ptc.FunctionalTestCase):
    layer = NotInstalled
