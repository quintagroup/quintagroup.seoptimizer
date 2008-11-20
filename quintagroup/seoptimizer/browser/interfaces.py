from zope.interface import Interface

class IValidateSEOKeywordsView(Interface):
    """ View for validating keywords on qSEO_properties_edit_form """

    def validateKeywords(text):
        """ Parse text and validate each keyword (extracted from text) for appearing on the context page """