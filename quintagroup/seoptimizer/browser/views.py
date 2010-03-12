from sets import Set
from DateTime import DateTime 
from Acquisition import aq_inner
from zope.component import queryAdapter
from zope.component import queryMultiAdapter
from plone.memoize import view
from plone.app.controlpanel.form import ControlPanelView

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as pmf

from quintagroup.seoptimizer import interfaces
from quintagroup.seoptimizer.browser.seo_configlet import ISEOConfigletSchema
from quintagroup.seoptimizer import SeoptimizerMessageFactory as _

SEPERATOR = '|'
SEO_PREFIX = 'seo_'
PROP_PREFIX = 'qSEO_'
SUFFIX = '_override'
PROP_CUSTOM_PREFIX = 'qSEO_custom_'

class SEOContext( BrowserView ):
    """ This class contains methods that allows to edit html header meta tags.
    """

    def __init__(self, *args, **kwargs):
        super(SEOContext, self).__init__(*args, **kwargs)
        self.pps = queryMultiAdapter((self.context, self.request), name="plone_portal_state")
        self.pcs = queryMultiAdapter((self.context, self.request), name="plone_context_state")
        self.gseo = queryAdapter(self.pps.portal(), ISEOConfigletSchema)
        self._seotags = self._getSEOTags()

    def __getitem__(self, key):
        return self._seotags.get(key, '')

    @view.memoize
    def _getSEOTags(self):
        seotags = {
            "seo_title": self.getSEOProperty( 'qSEO_title', default=self.pcs.object_title() ),
            "seo_robots": self.getSEOProperty( 'qSEO_robots', default='ALL'),
            "seo_description": self.getSEOProperty( 'qSEO_description', accessor='Description' ),
            "seo_distribution": self.getSEOProperty( 'qSEO_distribution', default="Global"),
            "seo_customMetaTags": self.seo_customMetaTags(),
            "seo_localCustomMetaTags": self.seo_localCustomMetaTags(),
            "seo_globalCustomMetaTags": self.seo_globalCustomMetaTags(),
            "seo_html_comment": self.getSEOProperty( 'qSEO_html_comment', default='' ),
            "meta_keywords": self.getSEOProperty('qSEO_keywords', 'Subject', ()),
            "seo_keywords": self.getSEOProperty('qSEO_keywords', default=()),
            "seo_canonical": self.seo_canonical(),
            # Add test properties
            "has_seo_title": self.context.hasProperty('qSEO_title'),
            "has_seo_robots": self.context.hasProperty('qSEO_robots'),
            "has_seo_description": self.context.hasProperty( 'qSEO_description'),
            "has_seo_distribution": self.context.hasProperty( 'qSEO_distribution'),
            "has_html_comment": self.context.hasProperty('qSEO_html_comment'),
            "has_seo_keywords": self.context.hasProperty('qSEO_keywords'),
            "has_seo_canonical": self.context.hasProperty('qSEO_canonical'),
            }
        seotags["seo_nonEmptylocalMetaTags"] = bool(seotags["seo_localCustomMetaTags"])
        return seotags

    def getSEOProperty( self, property_name, accessor='', default=None ):
        """ Get value from seo property by property name.
        """
        context = aq_inner(self.context)

        if context.hasProperty(property_name):
            return context.getProperty(property_name, default)

        if accessor:
            method = getattr(context, accessor, default)
            if not callable(method):
                return default

            # Catch AttributeErrors raised by some AT applications
            try:
                value = method()
            except AttributeError:
                value = default

            return value
        return default

    def seo_customMetaTags( self ):
        """Returned seo custom metatags from default_custom_metatags property in seo_properties
        (global seo custom metatags) with update from seo custom metatags properties in context (local seo custom metatags).
        """
        glob, loc = self.seo_globalCustomMetaTags(), self.seo_localCustomMetaTags()
        gnames = set(map(lambda x: x['meta_name'], glob))
        lnames = set(map(lambda x: x['meta_name'], loc))
        # Get untouch global, override global in custom and new custom meta tags
        untouchglob = [t for t in glob if t['meta_name'] in list(gnames - lnames)]
        return untouchglob + loc

    def seo_globalWithoutLocalCustomMetaTags( self ):
        """Returned seo custom metatags from default_custom_metatags property in seo_properties
        (global seo custom metatags) without seo custom metatags from properties in context (local seo custom metatags).
        """
        glob, loc = self.seo_globalCustomMetaTags(), self.seo_localCustomMetaTags()
        gnames = set(map(lambda x: x['meta_name'], glob))
        lnames = set(map(lambda x: x['meta_name'], loc))
        return [t for t in glob if t['meta_name'] in list(gnames - lnames)]

    def seo_localCustomMetaTags( self ):
        """ Returned seo custom metatags from properties in context (local seo custom metatags).
        """
        result = []
        property_prefix = 'qSEO_custom_'
        context = aq_inner(self.context)
        for property, value in context.propertyItems():
            if property.startswith(property_prefix) and property[len(property_prefix):]:
                result.append({'meta_name'    : property[len(property_prefix):],
                               'meta_content' : value})
        return result

    def seo_globalCustomMetaTags( self ):
        """ Returned seo custom metatags from default_custom_metatags property in seo_properties.
        """
        result = []
        if self.gseo:
            for tag in self.gseo.default_custom_metatags:
                name_value = tag.split(SEPERATOR)
                if name_value[0]:
                    result.append({'meta_name'    : name_value[0],
                                   'meta_content' : len(name_value) == 2 and name_value[1] or ''})
        return result

    def seo_canonical( self ):
        """ Generate canonical URL from SEO properties.
        """
        canpath = queryAdapter(self.context, interfaces.ISEOCanonicalPath)
        return self.pps.portal_url() + canpath.canonical_path()


class SEOContextPropertiesView( BrowserView ):
    """ This class contains methods that allows to manage seo properties.
    """
    template = ViewPageTemplateFile('templates/seo_context_properties.pt')

    def __init__(self, *args, **kwargs):
        super(SEOContextPropertiesView, self).__init__(*args, **kwargs)
        self.pps = queryMultiAdapter((self.context, self.request),
                                     name="plone_portal_state")
        self.gseo = queryAdapter(self.pps.portal(), ISEOConfigletSchema)


    def test( self, condition, first, second ):
        """
        """
        return condition and first or second 

    def getMainDomain(self, url):
        """ Get a main domain.
        """
        url = url.split('//')[-1]
        dompath = url.split(':')[0]
        dom = dompath.split('/')[0]
        return '.'.join(dom.split('.')[-2:])

    def validateSEOProperty(self, property, value):
        """ Validate a seo property.
        """
        purl = getToolByName(self.context, 'portal_url')()
        state = ''
        if property == PROP_PREFIX+'canonical':
            # validate seo canonical url property
            pdomain = self.getMainDomain(purl)
            if not pdomain == self.getMainDomain(value):
                state = _('canonical_msg', default=u'Canonical URL mast be in ${pdomain} domain.', mapping={'pdomain': pdomain})
        return state

    def setProperty(self, property, value, type='string'):
        """ Add a new property.

        Sets a new property with the given id, value and type or changes it.
        """
        context = aq_inner(self.context)
        state = self.validateSEOProperty(property, value)
        if not state:
            if context.hasProperty(property):
                context.manage_changeProperties({property: value})
            else:
                context.manage_addProperty(property, value, type)
        return state

    def manageSEOProps(self, **kw):
        """ Manage seo properties.
        """
        context = aq_inner(self.context)
        state = ''
        delete_list, seo_overrides_keys, seo_keys = [], [], []
        seo_items = dict([(k[len(SEO_PREFIX):],v) for k,v in kw.items() if k.startswith(SEO_PREFIX)])
        for key in seo_items.keys():
            if key.endswith(SUFFIX):
                seo_overrides_keys.append(key[:-len(SUFFIX)])
            else:
                seo_keys.append(key)
        for seo_key in seo_keys:
            if seo_key == 'custommetatags':
                self.manageSEOCustomMetaTagsProperties(**kw)
            else:
                if seo_key in seo_overrides_keys and seo_items.get(seo_key+SUFFIX):
                    seo_value = seo_items[seo_key]
                    t_value = 'string'
                    if type(seo_value)==type([]) or type(seo_value)==type(()): t_value = 'lines'
                    state = self.setProperty(PROP_PREFIX+seo_key, seo_value, type=t_value)
                    if state:
                        return state
                elif context.hasProperty(PROP_PREFIX+seo_key):
                    delete_list.append(PROP_PREFIX+seo_key)
        if delete_list:
            context.manage_delProperties(delete_list)
        return state

    def setSEOCustomMetaTags(self, custommetatags):
        """ Set seo custom metatags properties.
        """
        context = aq_inner(self.context)
        for tag in custommetatags:
            self.setProperty('%s%s' % (PROP_CUSTOM_PREFIX, tag['meta_name']), tag['meta_content'])

    def delAllSEOCustomMetaTagsProperties(self):
        """ Delete all seo custom metatags properties.
        """
        context = aq_inner(self.context)
        delete_list = []
        for property, value in context.propertyItems():
            if property.startswith(PROP_CUSTOM_PREFIX)  and not property == PROP_CUSTOM_PREFIX:
                delete_list.append(property)
        if delete_list:
            context.manage_delProperties(delete_list)

    def updateSEOCustomMetaTagsProperties(self, custommetatags):
        """ Update seo custom metatags properties.
        """
        globalCustomMetaTags = []
        if self.gseo:
            custom_meta_tags = self.gseo.default_custom_metatags
            for tag in custom_meta_tags:
                name_value = tag.split(SEPERATOR)
                if name_value[0]:
                    globalCustomMetaTags.append(
                        {'meta_name' : name_value[0],
                         'meta_content' : len(name_value) == 1 and '' or name_value[1]})
        for tag in custommetatags:
            meta_name, meta_content = tag['meta_name'], tag['meta_content']
            if meta_name:
                if not [gmt for gmt in globalCustomMetaTags \
                        if (gmt['meta_name']==meta_name and gmt['meta_content']==meta_content)]:
                    self.setProperty('%s%s' % (PROP_CUSTOM_PREFIX, meta_name), meta_content)

    def manageSEOCustomMetaTagsProperties(self, **kw):
        """ Update seo custom metatags properties, if enabled checkbox override or delete properties.

        Change object properties by passing either a mapping object
        of name:value pairs {'foo':6} or passing name=value parameters.
        """
        context = aq_inner(self.context)
        self.delAllSEOCustomMetaTagsProperties()
        if kw.get('seo_custommetatags_override'):
            custommetatags = kw.get('seo_custommetatags', {})
            self.updateSEOCustomMetaTagsProperties(custommetatags)

    def __call__( self ):
        """ Perform the update seo properties and redirect if necessary, or render the page Call method.
        """
        context = aq_inner(self.context)
        request = self.request
        form = self.request.form
        submitted = form.get('form.submitted', False)
        if submitted:
            state = self.manageSEOProps(**form)
            if not state:
                state = _('seoproperties_saved', default=u'Content SEO properties have been saved.')
                context.plone_utils.addPortalMessage(state)
                kwargs = {'modification_date' : DateTime()} 
                context.plone_utils.contentEdit(context, **kwargs)
                return request.response.redirect(self.context.absolute_url())
            context.plone_utils.addPortalMessage(state, 'error')
        return self.template()


class VisibilityCheckerView( BrowserView ):
    """ This class contains methods that visibility checker.
    """

    def checkVisibilitySEOAction(self):
        """ Checks visibility 'SEO Properties' action for content
        """
        context = aq_inner(self.context)
        plone = queryMultiAdapter((self, self.request),name="plone_portal_state").portal()
        adapter = ISEOConfigletSchema(plone)
        return bool(self.context.portal_type in adapter.types_seo_enabled)
