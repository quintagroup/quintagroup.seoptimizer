## Controller Python Script "qseo_properties_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##title=Update SEO Properties
##parameters=title=None,description=None,canonical=None,keywords=None,html_comment=None,robots=None,distribution=None,title_override=0,description_override=0,canonical_override=0,keywords_override=0,html_comment_override=0,robots_override=0,distribution_override=0,custommetatags=[],custommetatags_override=0

from Products.CMFCore.utils import getToolByName
SEPERATOR = '|'

def setProperty(context, property, value, type='string'):
    if context.hasProperty(property):
        context.manage_changeProperties({property: value})
    else:
        context.manage_addProperty(property, value, type)

delete_list = []

# update custom meta tags
property_prefix = 'qSEO_custom_'
custom_existing = []
for property, value in context.propertyItems():
    if property.find(property_prefix) == 0 and len(property) > len(property_prefix):
        custom_existing.append(property)

if not custommetatags_override: custommetatags=[]

globalCustomMetaTags = []
site_properties = getToolByName(context, 'portal_properties')
if hasattr(site_properties, 'seo_properties'):
    custom_meta_tags = getattr(site_properties.seo_properties, 'default_custom_metatags', [])
    for tag in custom_meta_tags:
        name_value = tag.split(SEPERATOR)
        if name_value[0]:
            globalCustomMetaTags.append({'meta_name'    : name_value[0],
                                         'meta_content' : len(name_value) == 1 and '' or name_value[1]})

custom_updated = []
for tag in custommetatags:
    meta_name, meta_content = tag['meta_name'], tag['meta_content']
    if meta_name:
        if not [gmt for gmt in globalCustomMetaTags if (gmt['meta_name']==meta_name and gmt['meta_content']==meta_content)]:
            setProperty(context, '%s%s' % (property_prefix, meta_name), meta_content)
        custom_updated.append('%s%s' % (property_prefix, meta_name))

#add not updated custom metatags to delete list
for tag in custom_existing:
    if tag not in custom_updated:
        delete_list.append(tag)

setProperty(context, 'qSEO_title', title)
setProperty(context, 'qSEO_description', description)
setProperty(context, 'qSEO_keywords', keywords, 'lines')
setProperty(context, 'qSEO_html_comment', html_comment)
setProperty(context, 'qSEO_robots', robots)
setProperty(context, 'qSEO_distribution', distribution)
setProperty(context, 'qSEO_canonical', canonical)

if not title_override:        delete_list.append('qSEO_title')
if not description_override:  delete_list.append('qSEO_description')
if not keywords_override:     delete_list.append('qSEO_keywords')
if not html_comment_override: delete_list.append('qSEO_html_comment')
if not robots_override:       delete_list.append('qSEO_robots')
if not distribution_override: delete_list.append('qSEO_distribution')
if not canonical_override:    delete_list.append('qSEO_canonical')

if delete_list: context.manage_delProperties(delete_list)

msg ='Content SEO properties have been saved.'
try:
    context.plone_utils.addPortalMessage(msg)
    return state
except AttributeError:
    return state.set(context=context, portal_status_message=msg)
