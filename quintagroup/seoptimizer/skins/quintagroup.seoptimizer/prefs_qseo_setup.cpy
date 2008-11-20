## Script (Python) "prefs_seo_config"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters= portalTypes=[], exposeDCMetaTags=None, additionalKeywords=[], default_custom_metatags=[]
##title=add action tab for selected portal types
##
from Products.CMFCore.utils import getToolByName

portal_props = getToolByName(context, 'portal_properties')
site_props = getToolByName(portal_props, 'site_properties')
seo_props = getToolByName(portal_props, 'seo_properties')
site_props.manage_changeProperties(exposeDCMetaTags=exposeDCMetaTags)
seo_props.manage_changeProperties(additional_keywords=additionalKeywords)
seo_props.manage_changeProperties(default_custom_metatags=default_custom_metatags)

pt = getToolByName(context, 'portal_types')
for ptype in pt.objectValues():
    try:
        #for Plone-2.5 and higher
        acts = filter(lambda x: x.id == 'seo_properties', ptype.listActions())
        action = acts and acts[0] or None
    except AttributeError:
        action = ptype.getActionById('seo_properties', default=None )

    if ptype.getId() in portalTypes:
        if action is None:
            ptype.addAction('seo_properties',
                            'SEO Properties',
                            'string:${object_url}/qseo_properties_edit_form',
                            '',
                            'Modify portal content',
                            'object',
                            visible=1)
    else:
        if action !=None:
            actions = list(ptype.listActions())
            ptype.deleteActions([actions.index(a) for a in actions if a.getId()=='seo_properties'])


msg = "Search Engine Optimizer configuration updated."
try:
    context.plone_utils.addPortalMessage(msg)
    return state
except AttributeError:
    return state.set(context=context, portal_status_message=msg)
