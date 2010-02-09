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
            filter_keywords_by_content = seo_props.getProperty('filter_keywords_by_content', None)
            meta_keywords = list(seo_context.meta_keywords())
            is_test = self.context.REQUEST.get('without_metatag_keywords', None)
            if filter_keywords_by_content and meta_keywords and is_test is None:
                # extract words from url page using lynx browser (test page randered without metatag keywords)
                text = commands.getoutput('lynx --dump --nolist %s?without_metatag_keywords=1' % self.context.absolute_url()).lower()

                # for tests package
                if text and 'lynx: can\'t access startfile http://nohost/plone/my_doc?without_metatag_keywords=1' in text:
                    text = self.context.getText()

                if text and text != 'sh: lynx: command not found':
                    text = text.decode('utf8')
                    for meta_keyword in meta_keywords:
                        if re.compile(u'\\b%s\\b' % meta_keyword.decode('utf8').lower(), re.I|re.U).search(text):
                            filtered_keywords.append(meta_keyword)
                    meta_keywords = filtered_keywords
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

        prop = aq_inner(self.context).getProperty('qSEO_canonical', None)
        if prop is not None:
            return prop[len(purl()):]
        
        return '/'+'/'.join(purl.getRelativeContentPath(self.context))
