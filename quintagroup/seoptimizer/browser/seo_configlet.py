from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema import Bool, Text, Choice, Tuple
from zope.app.form.browser import RadioWidget

from zope.formlib.form import FormFields
from zope.app.component.hooks import getSite
from zope.app.form.browser import TextAreaWidget

from plone.app.controlpanel.form import ControlPanelForm
from plone.app.controlpanel.widgets import MultiCheckBoxThreeColumnWidget

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot

from quintagroup.seoptimizer import SeoptimizerMessageFactory as _


# Global and local site keyword vocabularies
keywordsSGVocabulary = SimpleVocabulary((
    SimpleTerm(1, title="Plone categories override global SEO keywords"),
    SimpleTerm(2, title="Global SEO keywords override Plone categories"),
    SimpleTerm(3, title="Merge Plone categories and global SEO keywords"),
))

keywordsLGVocabulary = SimpleVocabulary((
    SimpleTerm(1, title="Global SEO keywords override local SEO keywords"),
    SimpleTerm(2, title="Merge global and local SEO keywords"),
))


# Custom Widgets
class TypedRadioWidgetNoValue(RadioWidget):
    _displayItemForMissingValue=False
    type = u'radio'

def SEORadioWidget(field, request):
    return TypedRadioWidgetNoValue(field, field.vocabulary, request)


# Configlet schema
class ISEOConfigletSchema(Interface):
    
    exposeDCMetaTags = Bool(
        title=_("label_exposeDCMetaTags",
                default='Expose <abbr title="Dublin Core">DC</abbr> meta tags'),
        description=_("description_seo_dc_metatags",
                default='Controls if <abbr title="Dublin Core">DC</abbr> '
                    'metatags are exposed to page header. They include '
                    'DC.description, DC.type, DC.format, DC.creator and '
                    'others.'),
        default=True,
        required=False)

    default_custom_metatags = Text(
        title=_("label_default_custom_metatags", default='Default custom metatags.'),
        description=_("help_default_custom_metatags",
                default='Fill in custom metatag names (one per line) which will'
                    'appear on qseo_properties edit tab. Example: '
                    '"metaname|metacontent" or "metaname".'),
        required=False)

    metatags_order = Text(
        title=_("label_metatags_order",
                default='Meta tags order in the page.'),
        description=_("help_metatags_order",
                default='Fill in meta tags (one per line) in the order in which'
                    ' they will appear on site source pages. Example: '
                    '"metaname accessor".'),
        required=False)

    additional_keywords = Text(
        title=_("label_additional_keywords",
                default='Additional keywords that should be added to the '
                    'content types.'),
        description=_("help_additional_keywords",
                default='Use this field when you want that your content types '
                    'receive additional keywords from the ones you manually '
                    'specify. Enter one keyword per line.'),
        required=False)
    
    settings_use_keywords_sg = Choice(
        title=_("label_settings_use_keywords_sg",
                default='Settings to control Plone categories and global SEO '
                    'keywords behaviour.'),
        description=_("help_settings_use_keywords_sg",
                default='Controls Plone categories (also known as keywords or '
                    'tags) and global SEO keywords behaviour.'),
        required=False,
        vocabulary=keywordsSGVocabulary)

    settings_use_keywords_lg = Choice(
        title=_("label_settings_use_keywords_lg",
                default='Settings to control global SEO keywords vs local SEO '
                    'keywords behaviour.'),
        description=_("help_settings_use_keywords_lg",
                default='Controls global and local SEO keywords behaviour.'),
        required=False,
        vocabulary=keywordsLGVocabulary)

    types_seo_enabled = Tuple(
        title=_("label_content_type_title", default='Content Types'),
        description=_("description_seo_content_types",
            default='Select content types that will have SEO properties '
                'enabled.'),
        required=False,
        missing_value=tuple(),
        value_type=Choice(
            vocabulary="plone.app.vocabularies.ReallyUserFriendlyTypes"))



class SEOConfigletAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(ISEOConfigletSchema)


    def __init__(self, context):
        super(SEOConfigletAdapter, self).__init__(context)
        self.portal = getSite()
        pprop = getToolByName(self.portal, 'portal_properties')
        self.context = pprop.seo_properties
        self.siteprops = pprop.site_properties
        self.ttool = getToolByName(context, 'portal_types')

    def getExposeDC(self):
        return self.siteprops.getProperty('exposeDCMetaTags')

    def setExposeDC(self, value):
        return self.siteprops._updateProperty('exposeDCMetaTags', bool(value))

    def getDefaultCustomMetatags(self):
        return '\n'.join(self.context.getProperty('default_custom_metatags'))
    
    def setDefaultCustomMetatags(self, value):
        value = value and value.strip().split('\n') or []
        self.context._updateProperty('default_custom_metatags', value)

    def getMetatagsOrder(self):
        return '\n'.join(self.context.getProperty('metatags_order'))
    
    def setMetatagsOrder(self, value):
        value = value and value.strip().split('\n') or []
        self.context._updateProperty('metatags_order', value)

    def getAdditionalKeywords(self):
        return '\n'.join(self.context.getProperty('additional_keywords'))
    
    def setAdditionalKeywords(self, value):
        value = value and value.strip().split('\n') or []
        self.context._updateProperty('additional_keywords', value)

    def getTypesSEOEnabled(self):
        ct_with_seo = self.context.content_types_with_seoproperties
        return [t for t in self.ttool.listContentTypes() if t in ct_with_seo]
    
    def setTypesSEOEnabled(self, value):
        value = [t for t in self.ttool.listContentTypes() if t in value]
        self.context._updateProperty('content_types_with_seoproperties', value)


    exposeDCMetaTags = property(getExposeDC, setExposeDC)
    metatags_order = property(getMetatagsOrder, setMetatagsOrder)
    default_custom_metatags = property(getDefaultCustomMetatags, setDefaultCustomMetatags)
    additional_keywords = property(getAdditionalKeywords, setAdditionalKeywords)
    types_seo_enabled = property(getTypesSEOEnabled, setTypesSEOEnabled)

    settings_use_keywords_sg = ProxyFieldProperty(ISEOConfigletSchema['settings_use_keywords_sg'])
    settings_use_keywords_lg = ProxyFieldProperty(ISEOConfigletSchema['settings_use_keywords_lg'])


class SmallTextAreaWidget(TextAreaWidget):
    height = 5


class SEOConfiglet(ControlPanelForm):

    form_fields = FormFields(ISEOConfigletSchema)
    form_fields['default_custom_metatags'].custom_widget = SmallTextAreaWidget
    form_fields['additional_keywords'].custom_widget = SmallTextAreaWidget
    form_fields['settings_use_keywords_sg'].custom_widget = SEORadioWidget
    form_fields['settings_use_keywords_lg'].custom_widget = SEORadioWidget
    form_fields['types_seo_enabled'].custom_widget = MultiCheckBoxThreeColumnWidget
    form_fields['types_seo_enabled'].custom_widget.cssClass='label'

    label = _("Search Engine Optimizer configuration")
    description = _("seo_configlet_description", default="You can select what "
                    "content types are qSEOptimizer-enabled, and control if "
                    "Dublin Core metatags are exposed in the header of content "
                    "pages.")
    form_name = _("")
