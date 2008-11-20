from zope.interface import Interface

class IKeywords(Interface):
    """Handle the available keywords.
    """
    def listKeywords():
        """Returns all the existing keywords for the current content type.
        """
