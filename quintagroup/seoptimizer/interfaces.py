from zope.interface import Interface
from quintagroup.canonicalpath.interfaces import ICanonicalPath

class IMetaKeywords(Interface):
    """Handle the available keywords.
    """
    def getMetaKeywords():
        """Returns all the existing keywords for the current content type.
        """

class IMappingMetaTags(Interface):
    """
    """
    def getMappingMetaTags():
        """Returns mapping {meta_name:accssesor} all the meta tags.
        """

class ISEOCanonicalPath(ICanonicalPath):
    """ Descendent of ICanonicalPath interface.
    Designed for three goals:
    1) calculation CANONICAL url metatag SPECIAL for Google SEO;
    2) as more specific canonical path interface;
    3) implementation this interface also work for ICanonicalPath too.
    """
