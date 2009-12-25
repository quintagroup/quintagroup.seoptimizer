import urllib, re, os, commands
from xml.dom import minidom, Node

from zope.interface import implements
from Products.Five.browser import BrowserView

from Products.CMFCore.utils import getToolByName

from interfaces import IValidateSEOKeywordsView
from quintagroup.seoptimizer import SeoptimizerMessageFactory as _

class ValidateSEOKeywordsView(BrowserView):

    implements(IValidateSEOKeywordsView)

    def validateKeywords(self, text):
        """ see interface """
        ts = getToolByName(self.context, 'translation_service')
        # extract keywords from text
        if text.lower().strip():
            keywords = map(lambda x: x.strip(), text.lower().strip().split('\n'))
        else:
            return ts.utranslate(None, _(u'Keywords list is empty!'), context=self.context)
        # request html page of context object
        url = '%s?qseo_without_additional_keywords=1' % self.context.absolute_url()
        #try:
            #page = urllib.urlopen(url)
        #except IOError:
            #return _('Could not find requested page')

        #page_html = page.read()
        #if not page_html:
            #return _('Page is empty')

        # extract words from body from html page

        # this block work only with valid html
        #doc = minidom.parseString(page_html)
        #rootNode = doc.documentElement
        #bodies = rootNode.getElementsByTagName('body')
        #if len(bodies) > 0:
            #body = bodies[0]
        #else:
            #return _(u'Invalid page html')
        #page_words = []
        #self.walkTextNodes(body, page_words)

        # this block work even with invalid html
        #pattern = re.compile('<\s*body[^>]*>(.*?)<\s*/\s*body\s*>', re.S|re.M|re.I)
        #search = pattern.search(page_html)
        #if search:
            #body_html = search.group(1)
        #else:
            #return _('Invalid html code on page')

        #page_text = self.strip_tags(body_html)
        #page_words = page_text.lower().split()

        # extract words from url page using lynx browser
        page_text = commands.getoutput('lynx --dump --nolist %s' % url).lower()
        if page_text and page_text != 'sh: lynx: command not found':
            #page_words = page_text.lower().split()
            page_text = page_text.decode('utf8')
        else:
            return _(u'Could not find lynx browser!')

        # check every keyword on appearing in body of html page
        missing = []
        finding = []
        added = {}
        finded = {}
        for keyword in keywords:
            keyword = keyword.decode('utf8')
            if keyword:
                keyword_on_page =  len(re.findall(u'\\b%s\\b' % keyword, page_text, re.I|re.U))
                if keyword not in added.keys() and not keyword_on_page:
                    missing.append(keyword)
                    added[keyword] = 1
                if keyword not in finded.keys() and keyword_on_page:
                    finding.append(keyword+u' - '+repr(keyword_on_page))
                    finded[keyword] = 1
        # return list of missing keywords
        if missing:
            msg = ts.utranslate(None, _('missing_keywords', default=u'Next keywords did not appear on the page:\n${missing}', mapping={'missing':'\n'.join(missing)}), context=self.context)
        else:
            msg = ts.utranslate(None, _('finded_keywords', default=u'All keywords found on the page!\nMore detailed:\n${found}', mapping={'found': '\n'.join(finding)}), context=self.context)
        return msg

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
