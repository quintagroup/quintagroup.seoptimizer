from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer

class IPloneSEOLayer(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 skin layer bound to a Skin
       Selection in portal_skins.
    """

class IValidateSEOKeywordsView(Interface):
    """ View for validating keywords on qSEO_properties_edit_form """

    def validateKeywords(text):
        """ Parse text and validate each keyword (extracted from text) for appearing on the context page """
