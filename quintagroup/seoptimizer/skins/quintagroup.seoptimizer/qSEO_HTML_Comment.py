## Script (Python) "qSEO_HTML_Comment"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Generate Description from SEO properties
##

prop_name = 'qSEO_html_comment'

if context.hasProperty(prop_name):
    return context.getProperty(prop_name)

# No comment by default
return ''
