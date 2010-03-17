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
