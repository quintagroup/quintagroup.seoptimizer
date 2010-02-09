from zope.interface import Interface

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

try:
    from quintagroup.canonicalpath.interfaces import ICanonicalPath
except:
    class ICanonicalPath(Interface):
        """canonical_path provider interface
        """

        def canonical_path():
            """Return canonical path for the object
            """
