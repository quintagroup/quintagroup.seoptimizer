import re
import sys
import urllib2

from zope.interface import implements
from zope.component import getUtility
from zope.component import queryAdapter

from Products.Five.browser import BrowserView

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode, getSiteEncoding
from Products.PortalTransforms.interfaces import IPortalTransformsTool

from interfaces import IValidateSEOKeywordsView
from quintagroup.seoptimizer import SeoptimizerMessageFactory as _
from quintagroup.seoptimizer.browser.seo_configlet import ISEOConfigletSchema


class ValidateSEOKeywordsView(BrowserView):

    implements(IValidateSEOKeywordsView)

    def validateKeywords(self):
        """ see interface """
        text = self.request.get('text')
        ts = getToolByName(self.context, 'translation_service')
        transforms = getUtility(IPortalTransformsTool)
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        query_adapter = queryAdapter(portal, ISEOConfigletSchema)
        isExternal = query_adapter.external_keywords_test
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
        error_url = ""
        if isExternal:
            # Not pass timeout option because:
            # 1. its value get from the global default timeout settings.
            # 2. timeout option added in python 2.6
            #    (so acceptable only in plone4+)
            try:
                resp = urllib2.urlopen(self.context.absolute_url())
                try:
                    html = resp.read()
                finally:
                    resp.close()
            except (urllib2.URLError, urllib2.HTTPError):
                # In case of exceed timeout period or
                # other URL connection errors.
                # Get nearest to context error_log object
                # (stolen from Zope2/App/startup.py)
                html = None
                info = sys.exc_info()
                elog = getToolByName(self.context, "error_log")
                error_url = elog.raising(info)
        else:
            html = unicode(self.context()).encode(enc)

        # If no html - information about problem with page retrieval
        # should be returned
        result = []
        if html is None:
            result.append("Problem with page retrieval.")
            if error_url:
                result.append("Details at %s." % error_url)
        else:
            page_text = transforms.convert("html_to_text", html).getData()
            # check every keyword on appearing in body of html page
            for keyword in keywords:
                keyword_on_page = unicode(len(re.findall(u'\\b%s\\b' % keyword,
                                              page_text, re.I | re.U)))
                result.append(' - '.join((keyword, keyword_on_page)))

        return ts.utranslate(domain='quintagroup.seoptimizer',
                             msgid=_(u'number_keywords',
                                     default=u'Number of keywords at page:\n'
                                              '${result}',
                                     mapping={'result': '\n'.join(result)}),
                             context=self.context)
