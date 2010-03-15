import urllib, re, os, commands
from xml.dom import minidom, Node

from zope.interface import implements
from Products.Five.browser import BrowserView

from Products.CMFPlone.utils import safe_unicode, getSiteEncoding
from Products.CMFCore.utils import getToolByName

from interfaces import IValidateSEOKeywordsView
from quintagroup.seoptimizer import SeoptimizerMessageFactory as _

class ValidateSEOKeywordsView(BrowserView):

    implements(IValidateSEOKeywordsView)

    def validateKeywords(self):
        """ see interface """
        text = self.request.get('text')
        ts = getToolByName(self.context, 'translation_service')
        # extract keywords from text
        enc = getSiteEncoding(self.context)
        if text.lower().strip():
            keywords = filter(None, map(lambda x: safe_unicode(x.strip(), enc),
                                         text.lower().strip().split('\n')))
        else:
            return ts.utranslate(domain='quintagroup.seoptimizer',
                                 msgid=_(u'Keywords list is empty!'),
                                 context=self.context)
        # request html page of context object
        url = '%s?without_metatag_keywords=1' % self.context.absolute_url()

        # extract words from url page using lynx browser (test page by 'url'
        # randered without metatag keywords)
        page_text = commands.getoutput('lynx --dump --nolist %s' % url).lower()
        if page_text and page_text != 'sh: lynx: command not found':
            page_text = safe_unicode(page_text, 'utf-8')
        else:
            return ts.utranslate(domain='quintagroup.seoptimizer',
                                 msgid=_(u'Could not find lynx browser!'),
                                 context=self.context)

        # check every keyword on appearing in body of html page
        result = []
        for keyword in keywords:
            keyword_on_page = unicode(len(re.findall(u'\\b%s\\b' % keyword, page_text, re.I|re.U)))
            result.append(' - '.join((keyword, keyword_on_page)))
        return ts.utranslate(domain='quintagroup.seoptimizer',
                             msgid=_(u'number_keywords',
                               default=u'Number of keywords at page:\n${result}',
                               mapping={'result':'\n'.join(result)}),
                             context=self.context)

    def walkTextNodes(self, parent, page_words=[]):
        for node in parent.childNodes:
            if node.nodeType == Node.ELEMENT_NODE:
                self.walkTextNodes(node, page_words)
            elif node.nodeType == Node.TEXT_NODE:
                value = node.nodeValue
                if value is not None:
                    page_words.extend(map(lambda x: x.lower(), value.split()))

    def strip_tags(self, in_text):
        s_list = list(in_text)
        i,j = 0,0

        while i < len(s_list):
            if s_list[i] == '<':
                while s_list[i] != '>':
                    # pop everything from the the left-angle bracket until the right-angle bracket
                    s_list.pop(i)

                # pops the right-angle bracket, too
                s_list.pop(i)
            else:
                i=i+1

        # convert the list back into text
        join_char=''
        return join_char.join(s_list)
