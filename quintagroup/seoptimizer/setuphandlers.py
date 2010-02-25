import logging
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression

logger = logging.getLogger('quintagroup.seoptimizer')
FIX_PTYPES_DOMAIN = ['Document', 'File', 'News Item']

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
        idxs = [idx_act[0] for idx_act in enumerate(ptype.listActions()) if idx_act[1].id == 'seo_properties']
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

def changeDomain(site):
    """ Fixes old versions bug: Change of content type's domain to 'plone'.
    """
    types_tool = getToolByName(site, 'portal_types')
    for ptype in [ptypes for ptypes in types_tool.objectValues() if ptypes.id in FIX_PTYPES_DOMAIN]:
        if ptype.i18n_domain == 'quintagroup.seoptimizer':
            ptype.i18n_domain = 'plone'
            logger.log(logging.INFO, "I18n Domain of the type \'%s\' changed to \'plone\'." % ptype.id)

def migrationActions(site):
    """ Migration actions from portal_types action to portal_actions.
    """
    types_tool = getToolByName(site, 'portal_types')
    pprops_tool = getToolByName(site, 'portal_properties')
    seoprops_tool = getToolByName(pprops_tool, 'seo_properties')
    ctws = list(seoprops_tool.getProperty('content_types_with_seoproperties', []))

    for ptype in types_tool.objectValues():
        idxs = [idx_act[0] for idx_act in enumerate(ptype.listActions()) if idx_act[1].id == 'seo_properties']
        if idxs:
            if ptype.id not in ctws:
                ctws.append(ptype.id)
            ptype.deleteActions(idxs)
            logger.log(logging.INFO, "Moved \"SEO Properties\" action from %s type in portal actions." % ptype.id)
    seoprops_tool.manage_changeProperties(content_types_with_seoproperties=ctws)

def importVarious(context):
    """ Do customized installation.
    """
    if context.readDataFile('seo_install.txt') is None:
        return

def reinstall(context):
    """ Do customized reinstallation.
    """
    if context.readDataFile('seo_reinstall.txt') is None:
        return
    site = context.getSite()
    migrationActions(site)
    changeDomain(site)

def uninstall(context):
    """ Do customized uninstallation.
    """
    if context.readDataFile('seo_uninstall.txt') is None:
        return
    site = context.getSite()
    removeSkin(site, 'quintagroup.seoptimizer' )
    removeActions(site)
    removeConfiglet(site, 'quintagroup.seoptimizer')
