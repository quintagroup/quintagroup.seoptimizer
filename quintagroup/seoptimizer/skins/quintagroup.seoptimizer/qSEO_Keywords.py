## Script (Python) "listMetaTags"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Generate Keywords from SEO properties
##

prop_name = 'qSEO_keywords'
add_keywords = 'additional_keywords'

keywords = []
if context.hasProperty(prop_name):
    keywords = context.getProperty(prop_name)

pprops = context.portal_properties
sheet = getattr(pprops, 'seo_properties', None)
if sheet and sheet.hasProperty(add_keywords):
    keywords += sheet.getProperty(add_keywords)

if keywords:
    return keywords

accessor = 'Subject'

method = getattr(context, accessor, None)
if not callable(method):
    # ups
    return None

# Catch AttributeErrors raised by some AT applications
try:
    value = method()
except AttributeError:
    value = None

return value
