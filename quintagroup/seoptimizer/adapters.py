from zope.interface import implements
from zope.component import queryAdapter
from zope.component import queryMultiAdapter

from quintagroup.seoptimizer.util import SortedDict
from quintagroup.seoptimizer.interfaces import IMetaKeywords, IMappingMetaTags
from quintagroup.seoptimizer.browser.seo_configlet import ISEOConfigletSchema

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
        meta_keywords = []
        seo_context = queryMultiAdapter((self.context, self.context.REQUEST),
                                        name='seo_context')
        if seo_context:
            meta_keywords = list(seo_context['meta_keywords'])
        return ', '.join(meta_keywords)


class MappingMetaTags(object):
    implements(IMappingMetaTags)

    def __init__(self, context):
        self.context = context
        pps = queryMultiAdapter((self.context, self.context.REQUEST),
                                name="plone_portal_state")
        self.gseo = queryAdapter(pps.portal(), ISEOConfigletSchema)

    def getMappingMetaTags(self):
        """ See interface.
        """
        metadata_name = SortedDict()
        if self.gseo:
            for mt in self.gseo.metatags_order:
                if mt in METADATA_MAPS:
                    metadata_name[mt] = METADATA_MAPS[mt]
        return metadata_name
