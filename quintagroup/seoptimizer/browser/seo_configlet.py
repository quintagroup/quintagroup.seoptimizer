import re
from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema import Bool, Text, Choice, Tuple, List
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

    default_custom_metatags = List(
        title=_("label_default_custom_metatags", default='Default custom metatags.'),
        description=_("help_default_custom_metatags",
                default='Fill in custom metatag names (one per line) which will'
                    'appear on qseo_properties edit tab. Example: '
                    '"metaname|metacontent" or "metaname".'),
        required=False)

    metatags_order = List(
        title=_("label_metatags_order",
                default='Meta tags order in the page.'),
        description=_("help_metatags_order",
                default='Fill in meta tags (one per line) in the order in which'
                    ' they will appear on site source pages. Example: '
                    '"metaname accessor".'),
        required=False)

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

    def getTypesSEOEnabled(self):
        ct_with_seo = self.context.content_types_with_seoproperties
        return [t for t in self.ttool.listContentTypes() if t in ct_with_seo]
    
    def setTypesSEOEnabled(self, value):
        value = [t for t in self.ttool.listContentTypes() if t in value]
        self.context._updateProperty('content_types_with_seoproperties', value)


    exposeDCMetaTags = property(getExposeDC, setExposeDC)
    default_custom_metatags = ProxyFieldProperty(ISEOConfigletSchema['default_custom_metatags'])
    metatags_order = ProxyFieldProperty(ISEOConfigletSchema['metatags_order'])
    types_seo_enabled = property(getTypesSEOEnabled, setTypesSEOEnabled)
    

class SmallTextAreaWidget(TextAreaWidget):
    height = 5
    splitter = re.compile(u'\\r?\\n', re.S|re.U)

    def _toFieldValue(self, value):
        return filter(None, self.splitter.split(value))

    def _toFormValue(self, value):
        return u'\r\n'.join(list(value))


class SEOConfiglet(ControlPanelForm):

    form_fields = FormFields(ISEOConfigletSchema)
    form_fields['default_custom_metatags'].custom_widget = SmallTextAreaWidget
    form_fields['metatags_order'].custom_widget = SmallTextAreaWidget
    form_fields['types_seo_enabled'].custom_widget = MultiCheckBoxThreeColumnWidget
    form_fields['types_seo_enabled'].custom_widget.cssClass='label'

    label = _("Search Engine Optimizer configuration")
    description = _("seo_configlet_description", default="You can select what "
                    "content types are qSEOptimizer-enabled, and control if "
                    "Dublin Core metatags are exposed in the header of content "
                    "pages.")
    form_name = _("")
