from cgi import escape
from zope.component import getMultiAdapter
from Products.CMFPlone.utils import safe_unicode
from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFCore.utils import getToolByName


class TitleCommentViewlet(ViewletBase):
    """ Simple viewlet for custom title rendering.
    """

    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.context_state = getMultiAdapter((self.context, self.request),
                                             name=u'plone_context_state')
        self.page_title = self.context_state.object_title
        self.portal_title = self.portal_state.portal_title

        self.override_title = self.context.hasProperty('qSEO_title')
        self.override_comments = self.context.hasProperty('qSEO_html_comment')

    def std_title(self):
        portal_title = safe_unicode(self.portal_title())
        page_title = safe_unicode(self.page_title())
        if page_title == portal_title:
            return u"<title>%s</title>" % (escape(portal_title))
        else:
            return u"<title>%s &mdash; %s</title>" % (
                escape(safe_unicode(page_title)),
                escape(safe_unicode(portal_title)))

    def render(self):
        std_title = self.std_title()
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


class CustomScriptViewlet( ViewletBase ):
    """ Simple viewlet for custom script rendering.
    """
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
    """ Simple viewlet for canonical url link rendering.
    """

    def render( self ):
        seo_context = getMultiAdapter((self.context, self.request), name='seo_context')
        return """<link rel="canonical" href="%s" />""" % seo_context.seo_canonical()
