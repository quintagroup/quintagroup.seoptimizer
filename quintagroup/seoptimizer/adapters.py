import re, commands

from zope.component import adapts
from zope.interface import implements
from zope.component import queryMultiAdapter

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName

from quintagroup.seoptimizer.util import SortedDict
from quintagroup.seoptimizer.interfaces import IMetaKeywords, IMappingMetaTags

METADATA_MAPS = dict([
    ("DC.publisher", "Publisher"),
    ("DC.description", "Description"),
    ("DC.contributors", "Contributors"),
    ("DC.creator", "Creator"),
    ("DC.format", "Format"),
    ("DC.rights", "Rights"),
    ("DC.language", "Language"),
    ("DC.date.modified", "ModificationDate"),
    ("DC.date.created", "CreationDate"),
    ("DC.type", "Type"),
    ("DC.subject", "Subject"),
    ("DC.distribution", "seo_distribution"),
    ("description", "seo_description"),
    ("keywords", "meta_keywords"),
    ("robots", "seo_robots"),
    ("distribution", "seo_distribution")])

class MetaKeywordsAdapter(object):
    implements(IMetaKeywords)

    def __init__(self, context):
        self.context = context

    def getMetaKeywords(self):
        """ See interface.
        """
        request = self.context.REQUEST
        meta_keywords = []
        filtered_keywords = []
        portal_props = getToolByName(self.context, 'portal_properties')
        seo_props = getToolByName(portal_props, 'seo_properties', None)
        seo_context = queryMultiAdapter((self.context, request), name='seo_context')
        if seo_context:
            meta_keywords = list(seo_context['meta_keywords'])
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
            pmn = self.seo_props.getProperty('metatags_order', ())
            for mt in pmn:
                if METADATA_MAPS.has_key(mt):
                    metadata_name[mt] = METADATA_MAPS[mt]
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
