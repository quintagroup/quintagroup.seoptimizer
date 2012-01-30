import cgi 
from DateTime import DateTime
from Acquisition import aq_inner

from zope.component import queryAdapter
from zope.component import queryMultiAdapter
from zope.component import getMultiAdapter
from plone.app.layout.viewlets.common import ViewletBase

from Products.CMFPlone.utils import safe_unicode, getSiteEncoding

from quintagroup.seoptimizer.util import SortedDict
from quintagroup.seoptimizer.interfaces import IMetaKeywords
from quintagroup.seoptimizer.interfaces import IMappingMetaTags
from quintagroup.seoptimizer.browser.seo_configlet import ISEOConfigletSchema

from Products.CMFPlone.PloneTool import FLOOR_DATE, CEILING_DATE


def escape(value):
    """Extended escape"""
    value = cgi.escape(value, True)
    return value.replace("'","&apos;")


class SEOTagsViewlet(ViewletBase):
    """ Simple viewlet for custom title rendering.
    """

    def render(self):
        TEMPLATE = '<meta name="%s" content="%s"/>'
        enc = getSiteEncoding(self.context)
        sfuncd = lambda x, enc=enc: safe_unicode(x, enc)
        return u'\n'.join([TEMPLATE % tuple(map(sfuncd, (k, v))) \
                           for k, v in self.listMetaTags().items()])

    def listMetaTags(self):
        """Calculate list metatags"""

        result = SortedDict()
        pps = queryMultiAdapter((self.context, self.request),
                                name="plone_portal_state")
        seo_global = queryAdapter(pps.portal(), ISEOConfigletSchema)
        seo_context = queryMultiAdapter((self.context, self.request),
                                        name='seo_context')

        use_all = seo_global.exposeDCMetaTags
        adapter = IMappingMetaTags(self.context, None)
        mapping_metadata = adapter and adapter.getMappingMetaTags() \
                           or SortedDict()

        if not use_all:
            metadata_names = 'DC.description' in mapping_metadata and \
                {'DC.description': mapping_metadata['DC.description']} \
                or SortedDict()
            if 'description' in mapping_metadata:
                metadata_names['description'] = mapping_metadata['description']
        else:
            metadata_names = mapping_metadata

        for key, accessor in metadata_names.items():
            if accessor == 'meta_keywords':
                # Render all the existing keywords for the current content type
                adapter = IMetaKeywords(self.context, None)
                if adapter is not None:
                    keywords = adapter.getMetaKeywords()
                    if keywords:
                        result['keywords'] = keywords
                continue

            if accessor in seo_context._seotags:
                value = seo_context._seotags.get(accessor, None)
            else:
                method = getattr(seo_context, accessor, None)
                if method is None:
                    method = getattr(aq_inner(self.context).aq_explicit,
                                     accessor, None)

                if not callable(method):
                    continue

                # Catch AttributeErrors raised by some AT applications
                try:
                    value = method()
                except AttributeError:
                    value = None

            if not value:
                # No data
                continue
            if accessor == 'Publisher' and value == 'No publisher':
                # No publisher is hardcoded (TODO: still?)
                continue
            if isinstance(value, (list, tuple)):
                # convert a list to a string
                value = ', '.join(value)

            # Special cases
            if accessor == 'Description' and \
               not 'description' in metadata_names:
                result['description'] = escape(value)
            elif accessor == 'Subject' and \
                 not 'keywords' in metadata_names:
                result['keywords'] = escape(value)

            if accessor not in ('Description', 'Subject'):
                result[key] = escape(value)

        if use_all:
            created = self.context.CreationDate()

            try:
                effective = self.context.EffectiveDate()
                if effective == 'None':
                    effective = None
                if effective:
                    effective = DateTime(effective)
            except AttributeError:
                effective = None

            try:
                expires = self.context.ExpirationDate()
                if expires == 'None':
                    expires = None
                if expires:
                    expires = DateTime(expires)
            except AttributeError:
                expires = None

            # Filter out DWIMish artifacts on effective / expiration dates
            if effective is not None and \
               effective > FLOOR_DATE and \
               effective != created:
                eff_str = effective.Date()
            else:
                eff_str = ''

            if expires is not None and expires < CEILING_DATE:
                exp_str = expires.Date()
            else:
                exp_str = ''

            if exp_str or exp_str:
                result['DC.date.valid_range'] = '%s - %s' % (eff_str, exp_str)

        # add custom meta tags (added from qseo tab by user)
        # for given context and default from configlet
        custom_meta_tags = seo_context and \
                           seo_context['seo_customMetaTags'] or []
        for tag in custom_meta_tags:
            if tag['meta_content']:
                result[tag['meta_name']] = escape(tag['meta_content'])

        return result


class TitleCommentViewlet(ViewletBase):
    """ Simple viewlet for custom title rendering.
    """

    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.context_state = getMultiAdapter((self.context, self.request),
                                             name=u'plone_context_state')
        self.seo_context = getMultiAdapter((self.context, self.request),
                                             name=u'seo_context')

        self.override_title = self.seo_context['has_seo_title']
        self.has_comments = self.seo_context['has_html_comment']

    def std_title(self):
        page_title = safe_unicode(self.context_state.object_title())
        portal_title = safe_unicode(self.portal_state.portal_title())
        if page_title == portal_title:
            return u"<title>%s</title>" % (escape(portal_title))
        else:
            return u"<title>%s &mdash; %s</title>" % (
                escape(safe_unicode(page_title)),
                escape(safe_unicode(portal_title)))

    def render(self):
        if self.override_title:
            qseo_title = u"<title>%s</title>" % escape(safe_unicode(
                self.seo_context["seo_title"]))
        else:
            qseo_title = self.std_title()

        comments = ""
        if self.has_comments:
            comments = u"\n<!--%s-->" % escape(safe_unicode(
                self.seo_context["seo_html_comment"]))

        return qseo_title + comments


class CustomScriptViewlet(ViewletBase):
    """ Simple viewlet for custom script rendering.
    """
    def getCustomScript(self):
        pps = queryMultiAdapter((self.context, self.request),
                                name="plone_portal_state")
        gseo = queryAdapter(pps.portal(), ISEOConfigletSchema)
        if gseo:
            return gseo.custom_script
        return ''

    def render(self):
        return safe_unicode("""%s""" % self.getCustomScript())


class CanonicalUrlViewlet(ViewletBase):
    """ Simple viewlet for canonical url link rendering.
    """
    def render(self):
        seoc = getMultiAdapter((self.context, self.request),
                               name=u'seo_context')
        if seoc['seo_canonical']:
            return """<link rel="canonical" href="%s" />""" \
                   % seoc['seo_canonical']
        return ""
