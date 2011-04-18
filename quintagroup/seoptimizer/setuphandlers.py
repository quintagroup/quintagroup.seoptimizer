import logging

from zope.component import getSiteManager

from config import SUPPORT_BLAYER

from Products.CMFCore.utils import getToolByName

logger = logging.getLogger('quintagroup.seoptimizer')


def removeActions(site):
    """ Remove actions.
    """
    types_tool = getToolByName(site, 'portal_types')
    for ptype in types_tool.objectValues():
        idxs = [idx_act[0] for idx_act in enumerate(ptype.listActions()) \
                           if idx_act[1].id == 'seo_properties']
        if idxs:
            ptype.deleteActions(idxs)
            msg_delete = "Deleted \"SEO Properties\" action for %s type."
            logger.log(logging.INFO, msg_delete % ptype.id)


def removeConfiglet(site):
    """ Remove configlet.
    """
    conf_id = 'quintagroup.seoptimizer'
    controlpanel_tool = getToolByName(site, 'portal_controlpanel')
    if controlpanel_tool:
        controlpanel_tool.unregisterConfiglet(conf_id)
        logger.log(logging.INFO, "Unregistered \"%s\" configlet." % conf_id)


def removeBrowserLayer(site):
    """ Remove browser layer.
    """
    if not SUPPORT_BLAYER:
        return

    from plone.browserlayer.utils import unregister_layer
    from plone.browserlayer.interfaces import ILocalBrowserLayerType

    name = "qSEOptimizer"
    site = getSiteManager(site)
    registeredLayers = [r.name for r in site.registeredUtilities()
                        if r.provided == ILocalBrowserLayerType]
    if name in registeredLayers:
        unregister_layer(name, site_manager=site)
        logger.log(logging.INFO, "Unregistered \"%s\" browser layer." % name)


def uninstall(context):
    """ Do customized uninstallation.
    """
    if context.readDataFile('seo_uninstall.txt') is None:
        return
    site = context.getSite()
    removeActions(site)
    removeConfiglet(site)
    removeBrowserLayer(site)
