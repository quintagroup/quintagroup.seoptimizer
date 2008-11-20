## Script (Python) "qSEO_CustomMetaTags"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Return context's properties prefixed with qSEO_custom_
##

result = []
added = []
property_prefix = 'qSEO_custom_'
for property, value in context.propertyItems():
    idx = property.find(property_prefix)
    if idx == 0 and len(property) > len(property_prefix):
        added.append(property[len(property_prefix):])
        result.append({'meta_name'    : property[len(property_prefix):],
                       'meta_content' : value})

from Products.CMFCore.utils import getToolByName
site_properties = getToolByName(context, 'portal_properties')
if hasattr(site_properties, 'seo_properties'):
    names = getattr(site_properties.seo_properties, 'default_custom_metatags', [])
    for name in names:
        if name not in added:
            result.append({'meta_name'    : name,
                           'meta_content' : ''})

return result