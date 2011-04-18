import re
from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts
from zope.schema import Bool, Choice, Tuple, List
from zope.schema import SourceText

from zope.app.component.hooks import getSite
from zope.app.form.browser import TextAreaWidget

from plone.fieldsets.fieldsets import FormFieldsets
from plone.app.controlpanel.form import ControlPanelForm
from plone.app.controlpanel.widgets import MultiCheckBoxThreeColumnWidget

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot

from quintagroup.seoptimizer import SeoptimizerMessageFactory as _


# Configlet schemas
class ISEOConfigletBaseSchema(Interface):

    exposeDCMetaTags = Bool(
        title=_("label_exposeDCMetaTags",
                default='Expose <abbr title="Dublin Core">DC</abbr> ' \
                'meta tags'),
        description=_("description_seo_dc_metatags",
                      default='Controls if <abbr title="Dublin Core">DC</abbr>'
                      ' metatags are exposed to page header. They include '
                      'DC.description, DC.type, DC.format, DC.creator and '
                      'others.'),
        default=True,
        required=False)

    metatags_order = List(
        title=_("label_metatags_order",
                default='Meta tags order in the page.'),
        description=_("help_metatags_order",
                      default='Fill in meta tags (one per line) in the order '
                      'in which they will appear on site source pages. '
                      'Example: "metaname accessor".'),
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

    default_custom_metatags = List(
        title=_("label_default_custom_metatags",
                default='Default custom metatags.'),
        description=_("help_default_custom_metatags",
                      default='Fill in custom metatag names (one per line) ' \
                      'which will appear on qseo_properties edit tab. ' \
                      'Example: "metaname|metacontent" or "metaname".'),
        required=False)


class ISEOConfigletAdvancedSchema(Interface):
    custom_script = SourceText(
        title=_("label_custom_script", default=u'Header JavaScript'),
        description=_("help_custom_script",
                default=u"This JavaScript code will be included in "
                         "the rendered HTML as entered in the page header."),
        default=u'',
        required=False)

    fields = List(
        title=_("label_fields", default='Fields for keywords statistic '
                'calculation.'),
        description=_("help_fields", default='Fill in filds (one per line)'
                      'which statistics of keywords usage should '
                      'be calculated for.'),
        required=False)

    stop_words = List(
        title=_("label_stop_words", default='Stop words.'),
        description=_("help_stop_words", default='Fill in stop words '
                      '(one per line) which will be excluded from kewords '
                      'statistics calculation.'),
        required=False)

    external_keywords_test = Bool(
        title=_("label_external_keywords_test",
                default='External keywords check'),
        description=_("description_external_keywords_test",
                default='Make keywords test by opening context url as '
                    'external resource with urllib2.openurl(). This is '
                    'useful when xdv/Deliverance transformation is used '
                    'on the site.'),
        default=False,
        required=False)


class ISEOConfigletSchema(ISEOConfigletBaseSchema,
                          ISEOConfigletAdvancedSchema):
    """Combined schema for the adapter lookup.
    """


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
        self.encoding = pprop.site_properties.default_charset

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

    def getCustomScript(self):
        description = getattr(self.context, 'custom_script', u'')
        return safe_unicode(description)

    def setCustomScript(self, value):
        if value is not None:
            self.context.custom_script = value.encode(self.encoding)
        else:
            self.context.custom_script = ''

    exposeDCMetaTags = property(getExposeDC, setExposeDC)
    seo_default_custom_metatag = ISEOConfigletSchema['default_custom_metatags']
    default_custom_metatags = ProxyFieldProperty(seo_default_custom_metatag)
    metatags_order = ProxyFieldProperty(ISEOConfigletSchema['metatags_order'])
    types_seo_enabled = property(getTypesSEOEnabled, setTypesSEOEnabled)
    custom_script = property(getCustomScript, setCustomScript)
    fields = ProxyFieldProperty(ISEOConfigletSchema['fields'])
    stop_words = ProxyFieldProperty(ISEOConfigletSchema['stop_words'])
    seo_external_keywords_test = ISEOConfigletSchema['external_keywords_test']
    external_keywords_test = ProxyFieldProperty(seo_external_keywords_test)


class Text2ListWidget(TextAreaWidget):
    height = 5
    splitter = re.compile(u'\\r?\\n', re.S | re.U)

    def _toFieldValue(self, input):
        if input == self._missing:
            return self.context._type()
        else:
            return self.context._type(filter(None, self.splitter.split(input)))

    def _toFormValue(self, value):
        if value == self.context.missing_value or \
           value == self.context._type():
            return self._missing
        else:
            return u'\r\n'.join(list(value))


# Fieldset configurations
baseset = FormFieldsets(ISEOConfigletBaseSchema)
baseset.id = 'seobase'
baseset.label = _(u'label_seobase', default=u'Base')

advancedset = FormFieldsets(ISEOConfigletAdvancedSchema)
advancedset.id = 'seoadvanced'
advancedset.label = _(u'label_seoadvanced', default=u'Advanced')


class SEOConfiglet(ControlPanelForm):

    form_fields = FormFieldsets(baseset, advancedset)
    type_seo_enabled = MultiCheckBoxThreeColumnWidget

    form_fields['default_custom_metatags'].custom_widget = Text2ListWidget
    form_fields['metatags_order'].custom_widget = Text2ListWidget
    form_fields['types_seo_enabled'].custom_widget = type_seo_enabled
    form_fields['types_seo_enabled'].custom_widget.cssClass = 'label'
    form_fields['fields'].custom_widget = Text2ListWidget
    form_fields['stop_words'].custom_widget = Text2ListWidget

    label = _("Search Engine Optimizer configuration")
    description = _("seo_configlet_description", default="You can select what "
                    "content types are qSEOptimizer-enabled, and control if "
                    "Dublin Core metatags are exposed in the header of content"
                    " pages.")
    form_name = _("")
