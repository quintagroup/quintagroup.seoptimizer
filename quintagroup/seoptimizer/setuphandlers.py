import logging
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger('quintagroup.seoptimizer')


def migrationActions(site):
    old = 'qseo_properties_edit_form'
    new = '@@seo-context-properties'
    for ptype in site.portal_types.objectValues():
        acts = filter(lambda x: x.id == 'seo_properties' and old in x.getActionExpression(), ptype.listActions())
        for act in acts:
            ac_exp = act.getActionExpression()
            if old in ac_exp:
                act.setActionExpression(ac_exp.replace(old, new))
                logger.log(logging.INFO, "For %s type changed URL Expression \"SEO Properties\" action's from %s to %s." % (ptype.id, old, new))

def importVarious(context):
    """ Do customized installation.
    """
    if context.readDataFile('seo_install.txt') is None:
        return
    site = context.getSite()
    migrationActions(site)

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

def remove_configlets( context, conf_ids ):
    """ Remove configlets.
    """
    configTool = getToolByName(context, 'portal_controlpanel', None)
    if configTool:
        for id in conf_ids:
            configTool.unregisterConfiglet(id)
            logger.log(logging.INFO, "Unregistered \"%s\" configlet." % id)

def uninstall( context ):
    """ Do customized uninstallation.
    """
    if context.readDataFile('seo_uninstall.txt') is None:
        return
    site = context.getSite()
    removeSkin( site, 'quintagroup.seoptimizer' )
    removeActions( site )
    remove_configlets( site, ('quintagroup.seoptimizer',))
