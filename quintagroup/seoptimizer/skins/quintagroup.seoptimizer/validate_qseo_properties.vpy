## Controller Python Script "qseo_properties_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##title=validates SEO Properties
##parameters=title=None,description=None,canonical=None,keywords=None,html_comment=None,robots=None,distribution=None,title_override=0,description_override=0,canonical_override=0,keywords_override=0,html_comment_override=0,robots_override=0,distribution_override=0,custommetatags=[]

from Products.CMFCore.utils import getToolByName
from quintagroup.seoptimizer import SeoptimizerMessageFactory as _

def getMainDomain(url):
    url = url.split('//')[-1]
    dompath = url.split(':')[0]
    dom = dompath.split('/')[0]
    return '.'.join(dom.split('.')[-2:])

purl = getToolByName(context, 'portal_url')()
if canonical:
    pdomain = getMainDomain(purl)
    if not pdomain == getMainDomain(canonical):
        state.setError('canonical', _(u'Canonical URL mast be in "%s" domain' % pdomain), "canonical")

if state.getErrors():
    context.plone_utils.addPortalMessage(_(u'Please correct the indicated errors.'))
    return state.set(status='failure')
else:
    return state
