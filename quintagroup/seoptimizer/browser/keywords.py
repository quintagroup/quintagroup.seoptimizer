import re, commands, urllib2
from xml.dom import Node

from zope.interface import implements
from zope.component import queryAdapter
from zope.component import queryMultiAdapter
from Products.Five.browser import BrowserView

from Products.CMFPlone.utils import safe_unicode, getSiteEncoding
from Products.CMFCore.utils import getToolByName

from interfaces import IValidateSEOKeywordsView
from quintagroup.seoptimizer import SeoptimizerMessageFactory as _
from quintagroup.seoptimizer.browser.seo_configlet import ISEOConfigletSchema

class ValidateSEOKeywordsView(BrowserView):

    implements(IValidateSEOKeywordsView)

    def validateKeywords(self):
        """ see interface """
        text = self.request.get('text')
        ts = getToolByName(self.context, 'translation_service')
        transforms = getToolByName(self.context, 'portal_transforms')
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        isExternal = queryAdapter(portal, ISEOConfigletSchema).external_keywords_test
        # extract keywords from text
        enc = getSiteEncoding(self.context)
        if text.lower().strip():
            keywords = filter(None, map(lambda x: safe_unicode(x.strip(), enc),
                                         text.lower().strip().split('\n')))
        else:
            return ts.utranslate(domain='quintagroup.seoptimizer',
                                 msgid=_(u'Keywords list is empty!'),
                                 context=self.context)
        # Get html page internally or with external request
        if isExternal:
            # Not pass timeout option because:
            # 1. its value get from the global default timeout settings by default.
            # 2. timeout option added in python 2.6 (so acceptable only in plone4+)
            try:
                try:
                    resp = urllib2.urlopen(self.context.absolute_url())
                    html = resp.read()
                finally:
                    'resp' in locals().keys() and resp.close()
            except Exception:
                # In case of exceed timeout period or other URL connection errors.
                html = None
        else:
            html = unicode(self.context()).encode(enc)

        # If no html - information about problem with page retrieval should be returned
        result = []
        if html is not None:
            page_text = transforms.convert("html_to_text", html).getData()
            # check every keyword on appearing in body of html page
            for keyword in keywords:
                keyword_on_page = unicode(len(re.findall(u'\\b%s\\b' % keyword, page_text, re.I|re.U)))
                result.append(' - '.join((keyword, keyword_on_page)))
        else:
            result.append("Problem with page retrieval")

        return ts.utranslate(domain='quintagroup.seoptimizer',
                             msgid=_(u'number_keywords',
                               default=u'Number of keywords at page:\n${result}',
                               mapping={'result':'\n'.join(result)}),
                             context=self.context)
