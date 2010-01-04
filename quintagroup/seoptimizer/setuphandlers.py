from Products.CMFCore.utils import getToolByName

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

def remove_configlets( context, conf_ids ):
    """ Remove configlets.
    """
    configTool = getToolByName(context, 'portal_controlpanel', None)
    if configTool:
        for id in conf_ids:
            configTool.unregisterConfiglet(id)

def uninstall( context ):
    """ Do customized uninstallation.
    """
    if context.readDataFile('seo_uninstall.txt') is None:
        return
    site = context.getSite()
    removeSkin( site, 'quintagroup.seoptimizer' )
    removeActions( site )
    remove_configlets( site, ('quintagroup.seoptimizer',))
