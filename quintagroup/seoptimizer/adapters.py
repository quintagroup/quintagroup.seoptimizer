import re, commands
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from quintagroup.seoptimizer.interfaces import IKeywords


class AdditionalKeywords(object):
    implements(IKeywords)

    def __init__(self, context):
        self.context = context

    def listKeywords(self):
        portal_props = getToolByName(self.context, 'portal_properties')
        seo_props = getToolByName(portal_props, 'seo_properties')

        # now set type is not using because of it unordered behaviour
        #original = set(self.context.qSEO_Keywords())
        #additional = set(seo_props.additional_keywords)
        #text = set(self.context.SearchableText().split())
        #keywords = list(additional.intersection(text).union(original))

        keywords = list(self.context.qSEO_Keywords())
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
