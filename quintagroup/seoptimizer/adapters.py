import re, commands

from zope.component import adapts
from zope.interface import implements
from zope.component import queryMultiAdapter

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName

from quintagroup.seoptimizer.util import SortedDict
from quintagroup.seoptimizer.interfaces import IMetaKeywords, IMappingMetaTags


class MetaKeywordsAdapter(object):
    implements(IMetaKeywords)

    def __init__(self, context):
        self.context = context

    def getMetaKeywords(self):
        """ See interface.
        """
        request = self.context.REQUEST
        meta_keywords = ''
        filtered_keywords = []
        portal_props = getToolByName(self.context, 'portal_properties')
        seo_props = getToolByName(portal_props, 'seo_properties', None)
        seo_context = queryMultiAdapter((self.context, request), name='seo_context')
        if seo_context:
            meta_keywords = list(seo_context.meta_keywords())
        return ', '.join(meta_keywords)


class MappingMetaTags(object):
    implements(IMappingMetaTags)

    def __init__(self, context):
        self.context = context
        self.portal_props = getToolByName(self.context, 'portal_properties')
        self.seo_props = getToolByName(self.portal_props, 'seo_properties', None)

    def getMappingMetaTags(self):
        """ See interface.
        """
        metadata_name = SortedDict()
        if self.seo_props:
            pmn = self.seo_props.getProperty('metatags_order')
            pmn = pmn and pmn or ''
            for mt in [mt.split(' ') for mt in pmn if len(mt.split(' '))==2]:
                metadata_name[mt[0]] = mt[1]
        return metadata_name


class canonicalPathAdapter(object):
    """Adapts base content to canonical path, with taking into consideration
       SEO canonical path value.
    """

    def __init__(self, context):
        self.context = context

    def canonical_path(self):
        purl = getToolByName(self.context,'portal_url')

        # Calculate canonical path from qSEO_canonical property
        prop = aq_inner(self.context).getProperty('qSEO_canonical', None)
        if prop is not None:
            return prop[len(purl()):]
        
        # Fallback for canonical path calculation
        return '/'+'/'.join(purl.getRelativeContentPath(self.context))
