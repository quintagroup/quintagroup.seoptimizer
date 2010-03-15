import logging

from zope.component import getSiteManager
from plone.browserlayer.utils import unregister_layer
from plone.browserlayer.interfaces import ILocalBrowserLayerType

from Products.CMFCore.utils import getToolByName

logger = logging.getLogger('quintagroup.seoptimizer')

def removeSkin(site, layer):
    """ Remove layers.
    """
    skins_tool = getToolByName(site, 'portal_skins')
    for skinName in skins_tool.getSkinSelections():
        skin_paths = skins_tool.getSkinPath(skinName).split(',') 
        paths = [l.strip() for l in skin_paths if not (l == layer or l.startswith(layer+'/'))]
        logger.log(logging.INFO, "Removed layers from %s skin." % skinName)
        skins_tool.addSkinSelection(skinName, ','.join(paths))

def removeActions(site):
    """ Remove actions.
    """
    types_tool = getToolByName(site, 'portal_types')
    for ptype in types_tool.objectValues():
        idxs = [idx_act[0] for idx_act in enumerate(ptype.listActions()) \
                           if idx_act[1].id == 'seo_properties']
        if idxs:
            ptype.deleteActions(idxs)
            logger.log(logging.INFO, "Deleted \"SEO Properties\" action for %s type." % ptype.id)

def removeConfiglet(site, conf_id):
    """ Remove configlet.
    """
    controlpanel_tool = getToolByName(site, 'portal_controlpanel')
    if controlpanel_tool:
        controlpanel_tool.unregisterConfiglet(conf_id)
        logger.log(logging.INFO, "Unregistered \"%s\" configlet." % conf_id)

def removeBrowserLayer(site):
    """ Remove configlet.
    """
    name="qSEOptimizer"
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
    removeSkin(site, 'quintagroup.seoptimizer' )
    removeActions(site)
    removeConfiglet(site, 'quintagroup.seoptimizer')
    removeBrowserLayer(site)
