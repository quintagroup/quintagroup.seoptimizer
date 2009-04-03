from zope.component import getMultiAdapter
from zope.viewlet.interfaces import IViewlet
from Products.CMFPlone.utils import safe_unicode
from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFCore.utils import getToolByName
from AccessControl import Unauthorized
from quintagroup.seoptimizer.util import SortedDict
from quintagroup.seoptimizer.interfaces import IKeywords 

class TitleCommentViewlet(ViewletBase):

    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.context_state = getMultiAdapter((self.context, self.request),
                                             name=u'plone_context_state')
        self.page_title = self.context_state.object_title
        self.portal_title = self.portal_state.portal_title

        self.override_title = self.context.hasProperty('qSEO_title')
        self.override_comments = self.context.hasProperty('qSEO_html_comment')

    def render(self):
        std_title = u"<title>%s &mdash; %s</title>" % ( safe_unicode(self.page_title()),
                                                        safe_unicode(self.portal_title())
                                                      )
        seo_context = getMultiAdapter((self.context, self.request), name='seo_context')
        if not self.override_title:
            if not self.override_comments:
                return std_title
            else:
                qseo_comments = u"<!--%s-->"%safe_unicode(seo_context.seo_html_comment())
                return u"%s\n%s"%(std_title, qseo_comments)
        else:
            qseo_title = u"<title>%s</title>" % safe_unicode(seo_context.seo_title())
            if not self.override_comments:
                return qseo_title
            else:
                qseo_comments = u"<!--%s-->"%safe_unicode(seo_context.seo_html_comment())
                return u"%s\n%s"%(qseo_title, qseo_comments)

class HTTPEquiv(ViewletBase):
    
    def charset( self ):
        context = self.context.aq_inner
        site_properties = getToolByName( context, 'portal_properties').site_properties
        return site_properties.getProperty('default_charset', 'utf-8')
    
    def render( self ):
        return """<meta http-equiv="Content-Type" content="text/html; charset=%s" />"""%self.charset()
         
class BaseUrlViewlet( ViewletBase ):
    """
       simpel viewlet for base href rendering
    """
    def renderBase( self ):
        # returns correct base href
        context = self.context.aq_inner
        isFolder = getattr(context.aq_explicit, 'isPrincipiaFolderish', 0)
        base_url = context.absolute_url()

        # when accessing via WEBDAV you're not allowed to access aq_explicit
        try:
            return '%s/'%base_url and isFolder or base_url
        except (Unauthorized, 'Unauthorized'):
            pass

    def render( self ):
        return """<base href="%s" /><!--[if lt IE 7]></base><![endif]-->"""% self.renderBase()

class MetaTagsViewlet( ViewletBase ):

    def listMetaTags( self ):
        context = self.context.aq_inner
        portal_props = getToolByName(context, 'portal_properties')
        pu = getToolByName(context, 'plone_utils')
        seo_props = getToolByName(portal_props, 'seo_properties', None)
        if seo_props is None:
            return pu.listMetaTags(context)

        site_props = getToolByName(portal_props, 'site_properties')
        exposeDCMetaTags = site_props.exposeDCMetaTags

        metaTags = SortedDict()
        metaTags.update(pu.listMetaTags(context))
        metadataList = [
            ('seo_description', 'description'),
            ('seo_keywords',    'keywords'),
            ('seo_robots',      'robots'),
            ('seo_distribution','distribution')]

        if exposeDCMetaTags:
            metadataList.append(('qSEO_Distribution', 'DC.distribution'))

        seo_context = getMultiAdapter((self.context, self.request), name='seo_context')
        for accessor, key in metadataList:
            method = getattr(seo_context, accessor, None)
            if not callable(method):
                # ups
                continue
            # Catch AttributeErrors raised by some AT applications
            try:
                value = method()
            except AttributeError:
                value = None

            if not value:
                continue
            if isinstance(value, (tuple, list)):
                value = ', '.join(value)

            metaTags[key] = value

        # add custom meta tags (added from qseo tab by user) for given context
        property_prefix = 'qSEO_custom_'
        for property, value in context.propertyItems():
            idx = property.find(property_prefix)
            if idx == 0 and len(property) > len(property_prefix):
                metaTags[property[len(property_prefix):]] = value

        # Set the additional matching keywords, if any
        adapter = IKeywords(context, None)
        if adapter is not None:
            keywords = adapter.listKeywords()
            if keywords:
                metaTags['keywords'] = keywords

        return metaTags

    def render( self ):
        return '\n'.join([safe_unicode("""<meta name="%s" content="%s" />"""%(name, content)) \
                                       for name, content in self.listMetaTags().items()])

class CustomScriptViewlet( ViewletBase ):

    def getCustomScript( self ):
        context = self.context.aq_inner
        portal_props = getToolByName(context, 'portal_properties')
        seo_props = getToolByName(portal_props, 'seo_properties', None)
        if seo_props is None:
            return '' 
	return seo_props.getProperty('custom_script', '')

    def render( self ):
        return safe_unicode("""%s"""% self.getCustomScript())


class CanonicalUrlViewlet( ViewletBase ):
    """
       simple viewlet for canonical url link rendering
    """

    def render( self ):
        seo_context = getMultiAdapter((self.context, self.request), name='seo_context')
        return """<link rel="canonical" href="%s" />""" % seo_context.seo_canonical()

