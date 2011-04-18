#
# Test product's installation
#
import string
from zope.interface import alsoProvides
from zope.component import queryMultiAdapter
from zope.viewlet.interfaces import IViewletManager

from quintagroup.canonicalpath.adapters import PROPERTY_LINK
from quintagroup.seoptimizer.browser.interfaces import IPloneSEOLayer
from quintagroup.seoptimizer.tests.base import TestCase, \
    FunctionalTestCaseNotInstalled
from quintagroup.seoptimizer.config import PROJECT_NAME, SUPPORT_BLAYER

from Products.CMFCore.utils import getToolByName

PROPERTY_SHEET = 'seo_properties'
STOP_WORDS = ['a', 'an', 'amp', 'and', 'are', 'arial', 'as', 'at', 'be', 'but',
    'by', 'can', 'com', 'do', 'font', 'for', 'from', 'gif', 'had', 'has',
    'have', 'he', 'helvetica', 'her', 'his', 'how', 'href', 'i', 'if', 'in',
    'is', 'it', 'javascript', 'jpg', 'made', 'net', 'of', 'on', 'or', 'org',
    'our', 'sans', 'see', 'serif', 'she', 'that', 'the', 'this', 'to', 'us',
    'we', 'with', 'you', 'your']

PROPS = {'stop_words': STOP_WORDS,
         'fields': ['seo_title', 'seo_description', 'seo_keywords']}

DEFAULT_METATAGS_ORDER = [
    'DC.contributors', 'DC.creator', 'DC.date.created',
    'DC.date.modified', 'DC.description', 'DC.distribution',
    'DC.format', 'DC.language', 'DC.publisher', 'DC.rights',
    'DC.subject', 'DC.type', 'description', 'distribution',
    'keywords', 'robots']
DEFAULT_METATAGS_ORDER.sort()

SEO_CONTENT = ['File', 'Document', 'News Item']
CONTENTTYPES_WITH_SEOACTION = ['File', 'Document', 'News Item', 'Folder',
                               'Event']
CONTENTTYPES_WITH_SEOACTION.sort()


class TestBeforeInstallation(FunctionalTestCaseNotInstalled):

    def afterSetUp(self):
        self.basic_auth = 'mgr:mgrpw'
        self.portal_path = '/%s' % self.portal.absolute_url(1)

    def testAccessPortalRootAnonymous(self):
        response = self.publish(self.portal_path)
        self.assertEqual(response.getStatus(), 200)

    def testAccessPortalRootAuthenticated(self):
        response = self.publish(self.portal_path, self.basic_auth)
        self.assertEqual(response.getStatus(), 200)


class TestInstallation(TestCase):

    def afterSetUp(self):
        self.properties = getToolByName(self.portal, 'portal_properties')

    def testAddingPropertySheet(self):
        """ Test adding property sheet to portal_properties tool """
        self.failUnless(hasattr(self.properties.aq_base, PROPERTY_SHEET))

    def testAddingPropertyFields(self):
        """ Test adding property field to portal_properties.maps_properties
            sheet
        """
        map_sheet = self.properties[PROPERTY_SHEET]
        for key, value in PROPS.items():
            self.failUnless(map_sheet.hasProperty(key) and \
                            list(map_sheet.getProperty(key)) == value)

    def test_configlet_install(self):
        configTool = getToolByName(self.portal, 'portal_controlpanel', None)
        self.assert_(PROJECT_NAME in [a.getId() for a in \
                                      configTool.listActions()], \
                     'Configlet not found')

    def test_viewlets_install(self):
        VIEWLETS = ['plone.htmlhead.title',
                    'plone.resourceregistries',
                    'quintagroup.seoptimizer.seotags',
                    'quintagroup.seoptimizer.customscript']
        request = self.app.REQUEST
        # mark request with our browser layer
        alsoProvides(request, IPloneSEOLayer)
        view = queryMultiAdapter((self.portal, request), name="plone")
        manager = queryMultiAdapter((self.portal['front-page'], request, view),
                                     IViewletManager, name='plone.htmlhead')
        for p in VIEWLETS:
            self.assert_(manager.get(p) is not None, "Not registered '%s' " \
                         "viewlet" % p)

    def test_browser_layer(self):
        if not SUPPORT_BLAYER:
            return

        from plone.browserlayer import utils
        self.assert_(IPloneSEOLayer in utils.registered_layers(),
                     "Not registered 'IPloneSEOLayer' browser layer")

    def test_action_install(self):
        atool = getToolByName(self.portal, 'portal_actions')
        action_ids = [a.id for a in atool.listActions()]
        self.assert_("SEOProperties" in action_ids,
                     "Not added 'SEOProperties' action")


class TestUninstallation(TestCase):

    def afterSetUp(self):
        self.qi = self.portal.portal_quickinstaller
        self.qi.uninstallProducts([PROJECT_NAME])

    def test_propertysheet_uninstall(self):
        properties = getToolByName(self.portal, 'portal_properties')
        self.assert_(hasattr(properties.aq_base, PROPERTY_SHEET),
                     "'%s' property sheet not uninstalled" % PROPERTY_SHEET)

    def test_configlet_uninstall(self):
        self.assertNotEqual(self.qi.isProductInstalled(PROJECT_NAME), True,
            'qSEOptimizer is already installed')

        configTool = getToolByName(self.portal, 'portal_controlpanel', None)
        self.assertEqual(PROJECT_NAME in [a.getId() for a in \
                                          configTool.listActions()], False,
                         'Configlet found after uninstallation')

    def test_viewlets_uninstall(self):
        VIEWLETS = ['quintagroup.seoptimizer.seotags',
                    'quintagroup.seoptimizer.customscript']
        request = self.app.REQUEST
        view = queryMultiAdapter((self.portal, request), name="plone")
        manager = queryMultiAdapter((self.portal['front-page'], request, view),
                                    IViewletManager, name='plone.htmlhead')
        for p in VIEWLETS:
            self.assertEqual(manager.get(p) is None, True,
                "'%s' viewlet present after uninstallation" % p)

    def test_browserlayer_uninstall(self):
        if not SUPPORT_BLAYER:
            return

        from plone.browserlayer import utils
        self.assertEqual(IPloneSEOLayer in utils.registered_layers(), False,
            "Still registered 'IPloneSEOLayer' browser layer")

    def test_action_uninstall(self):
        atool = getToolByName(self.portal, 'portal_actions')
        action_ids = [a.id for a in atool.listActions()]
        self.assertEqual("SEOProperties" in action_ids, False,
                         "'SEOProperties' action not removed from " \
                         "portal_actions on uninstallation")


class TestReinstallation(TestCase):

    def afterSetUp(self):
        self.qi = self.portal.portal_quickinstaller
        self.types_tool = getToolByName(self.portal, 'portal_types')
        self.setup_tool = getToolByName(self.portal, 'portal_setup')
        self.pprops_tool = getToolByName(self.portal, 'portal_properties')
        self.seoprops_tool = getToolByName(self.pprops_tool, 'seo_properties',
                                           None)
        # Set earlier version profile (2.0.0) for using upgrade steps
        self.setup_tool.setLastVersionForProfile('%s:default' % PROJECT_NAME,
                                                 '2.0.0')

    def testChangeDomain(self):
        # Test changed of content type's domain from 'quintagroup.seoptimizer'
        # to 'plone'
        for type in SEO_CONTENT:
            i18n_domain = 'quintagroup.seoptimizer'
            self.types_tool.getTypeInfo(type).i18n_domain = i18n_domain
        self.qi.reinstallProducts([PROJECT_NAME])
        for type in SEO_CONTENT:
            self.assertEqual(self.types_tool.getTypeInfo(type).i18n_domain,
                             'plone', "Not changed of %s content type's " \
                             "domain to 'plone'" % type)

    def testCutItemsMetatagsOrderList(self):
        # Test changed format metatags order list from "metaname accessor"
        # to "metaname"
        value, expect_mto = ['name1 accessor1', 'name2 accessor2'], \
                            ['name1', 'name2']
        self.seoprops_tool.manage_changeProperties(metatags_order=value)
        self.qi.reinstallProducts([PROJECT_NAME])
        mto = list(self.seoprops_tool.getProperty('metatags_order'))
        mto.sort()
        self.assertEqual(mto, expect_mto,
                         "Not changed format metatags order list from \"" \
                         "metaname accessor\" to \"metaname\". %s != %s" \
                         % (mto, expect_mto))

    def testAddMetatagsOrderList(self):
        # Test added metatags order list if it was not there before
        self.seoprops_tool.manage_delProperties(['metatags_order'])
        self.qi.reinstallProducts([PROJECT_NAME])
        mto = list(self.seoprops_tool.getProperty('metatags_order'))
        mto.sort()
        self.assertEqual(mto, DEFAULT_METATAGS_ORDER,
                         "Not added metatags order list with default values." \
                         "%s != %s" % (mto, DEFAULT_METATAGS_ORDER))

    def testMigrationActions(self):
        # Test migrated actions from portal_types action to seoproperties tool
        self.seoprops_tool.content_types_with_seoproperties = ()

        # Add seoaction to content type for testing

        for type in CONTENTTYPES_WITH_SEOACTION:
            self.types_tool.getTypeInfo(type).addAction(
                                    id='seo_properties',
                                    name='SEO Properties',
                                    action=None,
                                    condition=None,
                                    permission=(u'Modify portal content',),
                                    category='object',
                                   )
            # Check presence seoaction in content type
            seoaction = [act.id for act in \
                         self.types_tool.getTypeInfo(type).listActions() \
                         if act.id == 'seo_properties']
            self.assertEqual(bool(seoaction), True,
                             "Not added seoaction to content type %s for " \
                             "testing" % type)

        self.qi.reinstallProducts([PROJECT_NAME])

        # Check presence seoaction in content type
        for type in CONTENTTYPES_WITH_SEOACTION:
            seoaction = [act.id for act in \
                         self.types_tool.getTypeInfo(type).listActions() \
                         if act.id == 'seo_properties']
            self.assertEqual(bool(seoaction), False,
                "Not removed seoaction in content type %s" % type)

        # Check added content type names in seo properties tool
        # if content types have seoaction
        ctws = list(self.seoprops_tool.content_types_with_seoproperties)
        ctws.sort()
        self.assertEqual(ctws, CONTENTTYPES_WITH_SEOACTION,
                         "Not added content type names in seo properties " \
                         "tool if content types have seoaction. %s != %s" \
                         % (ctws, CONTENTTYPES_WITH_SEOACTION))

    def testRemoveSkin(self):
        # Test remove layers
        layer = 'quintagroup.seoptimizer'
        skinstool = getToolByName(self.portal, 'portal_skins')
        for skin in skinstool.getSkinSelections():
            paths = ','.join((skinstool.getSkinPath(skin), layer))
            skinstool.addSkinSelection(skin, paths)
        self.qi.reinstallProducts([PROJECT_NAME])
        for skin in skinstool.getSkinSelections():
            path = skinstool.getSkinPath(skin)
            path = map(string.strip, string.split(path, ','))
            self.assertEqual(layer in path, False,
                             '%s layer found in %s after uninstallation' \
                             % (layer, skin))

    def testMigrateCanonical(self):
        """ Test Migrate qSEO_canonical property into PROPERTY_LINK
            for all portal objects, which use SEO
        """
        doc = self.portal.get('front-page')
        doc.manage_addProperty('qSEO_canonical', 'val', 'string')
        value = doc.getProperty('qSEO_canonical')
        assert doc.getProperty('qSEO_canonical') == 'val'

        self.qi.reinstallProducts([PROJECT_NAME])
        value = doc.getProperty(PROPERTY_LINK)
        has_prop = bool(doc.hasProperty('qSEO_canonical'))
        self.assertEqual(has_prop, False, "Property 'qSEO_canonical' is " \
                         "not deleted.")
        self.assertEqual(value == 'val', True, "Property not migrated from " \
                         "'qSEO_canonical' to '%s'." % PROPERTY_LINK)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBeforeInstallation))
    suite.addTest(makeSuite(TestInstallation))
    suite.addTest(makeSuite(TestUninstallation))
    suite.addTest(makeSuite(TestReinstallation))
    return suite
