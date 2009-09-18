import re, commands
from zope.interface import implements
from zope.component import queryMultiAdapter
from Products.CMFCore.utils import getToolByName

from quintagroup.seoptimizer.interfaces import IKeywords, IMappingMetaTags
from quintagroup.seoptimizer.util import SortedDict


class AdditionalKeywords(object):
    implements(IKeywords)

    def __init__(self, context):
        self.context = context

    def listKeywords(self):
        portal_props = getToolByName(self.context, 'portal_properties')
        seo_props = getToolByName(portal_props, 'seo_properties', None)

        # now set type is not using because of it unordered behaviour
        #original = set(self.context.qSEO_Keywords())
        #additional = set(seo_props.additional_keywords)
        #text = set(self.context.SearchableText().split())
        #keywords = list(additional.intersection(text).union(original))

        request = self.context.REQUEST
        seo_context = queryMultiAdapter((self.context, request), name='seo_context')
        if seo_context:
            keywords = list(seo_context.seo_keywords())
            lower_keywords = map(lambda x: x.lower(), keywords)
            additional = seo_props.additional_keywords

            is_test = self.context.REQUEST.get('qseo_without_additional_keywords', None)

            if additional and is_test is None:
                # extract words from url page using lynx browser
                text = commands.getoutput('lynx --dump --nolist %s?qseo_without_additional_keywords=1' % self.context.absolute_url()).lower()
                if text and text != 'sh: lynx: command not found':
                    for keyword in additional:
                        if keyword.lower() not in lower_keywords and re.compile(r'\b%s\b' % keyword, re.I).search(text):
                            keywords.append(keyword)
            return ', '.join(keywords)
        return ''


class MappingMetaTags(object):
    implements(IMappingMetaTags)

    def __init__(self, context):
        self.context = context
        self.portal_props = getToolByName(self.context, 'portal_properties')
        self.seo_props = getToolByName(self.portal_props, 'seo_properties', None)

    def getMappingMetaTags(self):
        metadata_name = SortedDict()
        if self.seo_props:
            pmn = self.seo_props.getProperty('metatags_order')
            pmn = pmn and pmn or ''
            for mt in [mt.split(' ') for mt in pmn if len(mt.split(' '))==2]:
                metadata_name[mt[0]] = mt[1]
        return metadata_name
