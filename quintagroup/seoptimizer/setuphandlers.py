import logging
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression

logger = logging.getLogger('quintagroup.seoptimizer')
FIX_PTYPES_DOMAIN = ['Document', 'File', 'News Item']

def migrationActions(site):
    p_props = getToolByName(site, 'portal_properties')
    seo_props = getToolByName(p_props, 'seo_properties')
    ctws = list(seo_props.getProperty('content_types_with_seoproperties', []))

    for ptype in site.portal_types.objectValues():
        for idx, act in enumerate(ptype.listActions()):
            if act.id == 'seo_properties':
                if  ptype.id not in ctws:
                    ctws.append(ptype.id)
                ptype.deleteActions([idx])
                logger.log(logging.INFO, "Moved \"SEO Properties\" action from %s type in portal actions." % ptype.id)
    seo_props.manage_changeProperties(content_types_with_seoproperties=ctws)

def removeSkin(self, layer):
    """ Remove layers.
    """
    skinstool = getToolByName(self, 'portal_skins')
    for skinName in skinstool.getSkinSelections():
        original_path = skinstool.getSkinPath(skinName)
        original_path = [l.strip() for l in original_path.split(',')]
        new_path= []
        for l in original_path:
            if (l == layer) or (l.startswith(layer+'/')):
                logger.log(logging.INFO, "Removed %s layer from %s skin." % (l, skinName))
                continue
            new_path.append(l)
        skinstool.addSkinSelection(skinName, ','.join(new_path))

def removeActions(self):
    """ Remove actions.
    """
    tool = getToolByName(self, 'portal_types')
    for ptype in tool.objectValues():
        if ptype.getId() in ['File','Document','News Item']:
            acts = filter(lambda x: x.id == 'seo_properties', ptype.listActions())
            action = acts and acts[0] or None
            if action != None:
                acts = list(ptype.listActions())
                ptype.deleteActions([acts.index(a) for a in acts if a.getId()=='seo_properties'])
                logger.log(logging.INFO, "Deleted \"SEO Properties\" action for %s type." % ptype.id)

def remove_configlets(context, conf_ids):
    """ Remove configlets.
    """
    configTool = getToolByName(context, 'portal_controlpanel', None)
    if configTool:
        for id in conf_ids:
            configTool.unregisterConfiglet(id)
            logger.log(logging.INFO, "Unregistered \"%s\" configlet." % id)

def changeDomain(site):
    """ Fixes old versions bug: Change of content type's domain to 'plone'.
    """
    for ptype in [ptypes for ptypes in site.portal_types.objectValues() if ptypes.id in FIX_PTYPES_DOMAIN]:
        if ptype.i18n_domain == 'quintagroup.seoptimizer':
            ptype.i18n_domain = 'plone'
            logger.log(logging.INFO, "I18n Domain of the type \'%s\' changed to \'plone\'." % ptype.id)

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
    remove_configlets(site, ('quintagroup.seoptimizer',))
