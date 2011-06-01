from time import time
from DateTime import DateTime
from Acquisition import aq_inner
from zope.component import queryAdapter
from zope.component import queryMultiAdapter
from zope.schema.interfaces import InvalidValue

from plone.memoize import view, ram

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.utils import getSiteEncoding

from quintagroup.canonicalpath.interfaces import ICanonicalLink
from quintagroup.canonicalpath.adapters import PROPERTY_LINK \
                                               as CANONICAL_PROPERTY

from quintagroup.seoptimizer.browser.seo_configlet import ISEOConfigletSchema
from quintagroup.seoptimizer import SeoptimizerMessageFactory as _

SEPERATOR = '|'
SEO_PREFIX = 'seo_'
PROP_PREFIX = 'qSEO_'
SUFFIX = '_override'
PROP_CUSTOM_PREFIX = 'qSEO_custom_'


# Ram cache function, which depends on plone instance and time
def plone_instance_time(method, self, *args, **kwargs):
    return (self.pps.portal(), time() // (60 * 60))


class SEOContext(BrowserView):
    """ This class contains methods that allows to edit html header meta tags.
    """

    def __init__(self, *args, **kwargs):
        super(SEOContext, self).__init__(*args, **kwargs)
        self.pps = queryMultiAdapter((self.context, self.request),
                                     name="plone_portal_state")
        self.pcs = queryMultiAdapter((self.context, self.request),
                                     name="plone_context_state")
        self.gseo = queryAdapter(self.pps.portal(), ISEOConfigletSchema)
        self._seotags = self._getSEOTags()

    def __getitem__(self, key):
        return self._seotags.get(key, '')

    @view.memoize
    def _getSEOTags(self):
        seotags = {
            "seo_title": self.getSEOProperty('qSEO_title',
                                             default=self.pcs.object_title()),
            "seo_robots": self.getSEOProperty('qSEO_robots', default='ALL'),
            "seo_description": self.getSEOProperty('qSEO_description',
                                                   accessor='Description'),
            "seo_distribution": self.getSEOProperty('qSEO_distribution',
                                                    default="Global"),
            "seo_customMetaTags": self.seo_customMetaTags(),
            # "seo_localCustomMetaTags": self.seo_localCustomMetaTags(),
            # "seo_globalCustomMetaTags": self.seo_globalCustomMetaTags(),
            "seo_html_comment": self.getSEOProperty('qSEO_html_comment',
                                                    default=''),
            "meta_keywords": self.getSEOProperty('qSEO_keywords',
                                                 'Subject', ()),
            "seo_keywords": self.getSEOProperty('qSEO_keywords', default=()),
            "seo_canonical": self.getSEOProperty(CANONICAL_PROPERTY),
            # Add test properties
            "has_seo_title": self.context.hasProperty('qSEO_title'),
            "has_seo_robots": self.context.hasProperty('qSEO_robots'),
            "has_seo_description": \
                     self.context.hasProperty('qSEO_description'),
            "has_seo_distribution": \
                     self.context.hasProperty('qSEO_distribution'),
            "has_html_comment": self.context.hasProperty('qSEO_html_comment'),
            "has_seo_keywords": self.context.hasProperty('qSEO_keywords'),
            "has_seo_canonical": self.context.hasProperty(CANONICAL_PROPERTY),
            }
        #seotags["seo_nonEmptylocalMetaTags"] = \
        #    bool(seotags["seo_localCustomMetaTags"])
        return seotags

    def getSEOProperty(self, property_name, accessor='', default=None):
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

    def seo_customMetaTags(self):
        """Returned seo custom metatags from default_custom_metatags property
           in seo_properties (global seo custom metatags) with update from seo
           custom metatags properties in context (local seo custom metatags).
        """
        glob = self.seo_globalCustomMetaTags()
        loc = self.seo_localCustomMetaTags()
        gnames = set(map(lambda x: x['meta_name'], glob))
        lnames = set(map(lambda x: x['meta_name'], loc))
        # Get untouch global, override global in custom
        # and new custom meta tags
        untouchglob = [t for t in glob \
                         if t['meta_name'] in list(gnames - lnames)]
        return untouchglob + loc

    def seo_globalWithoutLocalCustomMetaTags(self):
        """Returned seo custom metatags from default_custom_metatags property
           in seo_properties (global seo custom metatags) without seo custom
           metatags from properties in context (local seo custom metatags).
        """
        glob = self.seo_globalCustomMetaTags()
        loc = self.seo_localCustomMetaTags()
        gnames = set(map(lambda x: x['meta_name'], glob))
        lnames = set(map(lambda x: x['meta_name'], loc))
        return [t for t in glob if t['meta_name'] in list(gnames - lnames)]

    def seo_localCustomMetaTags(self):
        """ Returned seo custom metatags from properties in
            context (local seo custom metatags).
        """
        result = []
        property_prefix = 'qSEO_custom_'
        context = aq_inner(self.context)
        for property, value in context.propertyItems():
            if property.startswith(property_prefix) and \
               property[len(property_prefix):]:
                result.append({'meta_name': property[len(property_prefix):],
                               'meta_content': value})
        return result

    @ram.cache(plone_instance_time)
    def seo_globalCustomMetaTags(self):
        """ Returned seo custom metatags from default_custom_metatags property
            in seo_properties.
        """
        result = []
        if self.gseo:
            for tag in self.gseo.default_custom_metatags:
                name_value = tag.split(SEPERATOR)
                if name_value[0]:
                    result.append({'meta_name': name_value[0],
                                   'meta_content': len(name_value) == 2 and \
                                                    name_value[1] or ''})
        return result

    # Not used
    def getCanonical(self):
        # TODO: rewrite function structure
        if self.context.hasProperty(CANONICAL_PROPERTY):
            canonical = queryAdapter(self.context, ICanonicalLink)
            return canonical and canonical.canonical_link or ""
        return ""


class SEOContextPropertiesView(BrowserView):
    """ This class contains methods that allows to manage seo properties.
    """
    template = ViewPageTemplateFile('templates/seo_context_properties.pt')

    def __init__(self, *args, **kwargs):
        super(SEOContextPropertiesView, self).__init__(*args, **kwargs)
        self.pps = queryMultiAdapter((self.context, self.request),
                                     name="plone_portal_state")
        self.gseo = queryAdapter(self.pps.portal(), ISEOConfigletSchema)

    def test(self, condition, first, second):
        """
        """
        return condition and first or second

    def validateSEOProperty(self, property, value):
        """ Validate a seo property.
        """
        return ''

    def setProperty(self, property, value, type='string'):
        """ Add a new property.

            Sets a new property with the given id, value and type or
            changes it.
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
        seo_items = dict([(k[len(SEO_PREFIX):], v) \
                         for k, v in kw.items() if k.startswith(SEO_PREFIX)])
        for key in seo_items.keys():
            if key.endswith(SUFFIX):
                seo_overrides_keys.append(key[:-len(SUFFIX)])
            else:
                seo_keys.append(key)
        for seo_key in seo_keys:
            if seo_key == 'custommetatags':
                self.manageSEOCustomMetaTagsProperties(**kw)
            else:
                if seo_key in seo_overrides_keys and \
                              seo_items.get(seo_key + SUFFIX):
                    seo_value = seo_items[seo_key]
                    if seo_key == 'canonical':
                        try:
                            i_canonical_link = ICanonicalLink(self.context)
                            i_canonical_link.canonical_link = seo_value
                        except InvalidValue, e:
                            state = "'%s' - wrong canonical url" % str(e)
                    else:
                        t_value = 'string'
                        if type(seo_value) == type([]) or \
                           type(seo_value) == type(()):
                            t_value = 'lines'
                        state = self.setProperty(PROP_PREFIX + seo_key,
                                                 seo_value, type=t_value)
                    if state:
                        return state
                elif seo_key == 'canonical':
                    del ICanonicalLink(self.context).canonical_link
                elif context.hasProperty(PROP_PREFIX + seo_key):
                    delete_list.append(PROP_PREFIX + seo_key)
        if delete_list:
            context.manage_delProperties(delete_list)
        return state

    def setSEOCustomMetaTags(self, custommetatags):
        """ Set seo custom metatags properties.
        """
        aq_inner(self.context)
        for tag in custommetatags:
            self.setProperty('%s%s' % (PROP_CUSTOM_PREFIX, tag['meta_name']),
                             tag['meta_content'])

    def delAllSEOCustomMetaTagsProperties(self):
        """ Delete all seo custom metatags properties.
        """
        context = aq_inner(self.context)
        delete_list = []
        for property, value in context.propertyItems():
            if property.startswith(PROP_CUSTOM_PREFIX) and \
                                   not property == PROP_CUSTOM_PREFIX:
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
                        {'meta_name': name_value[0],
                         'meta_content': len(name_value) > 1 and \
                                         name_value[1] or ''})
        for tag in custommetatags:
            meta_name, meta_content = tag['meta_name'], tag['meta_content']
            if meta_name:
                if not [gmt for gmt in globalCustomMetaTags \
                        if (gmt['meta_name'] == meta_name and \
                            gmt['meta_content'] == meta_content)]:
                    self.setProperty('%s%s' % (PROP_CUSTOM_PREFIX, meta_name),
                                     meta_content)

    def manageSEOCustomMetaTagsProperties(self, **kw):
        """ Update seo custom metatags properties, if enabled checkbox override
            or delete properties.

            Change object properties by passing either a mapping object
            of name:value pairs {'foo':6} or passing name=value parameters.
        """
        aq_inner(self.context)
        self.delAllSEOCustomMetaTagsProperties()
        if kw.get('seo_custommetatags_override'):
            custommetatags = kw.get('seo_custommetatags', {})
            self.updateSEOCustomMetaTagsProperties(custommetatags)

    def getPropertyStopWords(self):
        """ Get property 'stop_words' from SEO Properties tool.
        """
        enc = getSiteEncoding(self.context)
        # self.gseo.stop_words return list of unicode objects,
        # and may contains stop words in different languages.
        # So we must return encoded strings.
        sw = map(lambda x: unicode.encode(x, enc), self.gseo.stop_words)
        return str(sw)

    def getPropertyFields(self):
        """ Get property 'fields' from SEO Properties tool.
        """
        # self.gseo.fields return list of unicode objects,
        # so *str* use as encoding function from unicode to latin-1 string.
        fields_id = map(str, self.gseo.fields)
        return str(fields_id)

    def __call__(self):
        """ Perform the update seo properties and redirect if necessary,
            or render the page Call method.
        """
        context = aq_inner(self.context)
        request = self.request
        form = self.request.form
        submitted = form.get('form.submitted', False)
        if submitted:
            msgtype = "info"
            save = form.get('form.button.Save', False)
            if save:
                msg = self.manageSEOProps(**form)
                if not msg:
                    msg = _('seoproperties_saved',
                            default=u'Content SEO properties have been saved.')
                    kwargs = {'modification_date': DateTime()}
                    context.plone_utils.contentEdit(context, **kwargs)
                else:
                    msgtype = "error"
            else:
                # Cancel
                msg = _('seoproperties_canceled', default=u'No content SEO ' \
                        'properties have been changed.')

            context.plone_utils.addPortalMessage(msg, msgtype)
            if msgtype == "info":
                return request.response.redirect(self.context.absolute_url())

        return self.template()


class VisibilityCheckerView(BrowserView):
    """ This class contains methods that visibility checker.
    """

    def checkVisibilitySEOAction(self):
        """ Checks visibility 'SEO Properties' action for content
        """
        aq_inner(self.context)
        plone = queryMultiAdapter((self, self.request),
                                  name="plone_portal_state").portal()
        adapter = ISEOConfigletSchema(plone)
        return bool(self.context.portal_type in adapter.types_seo_enabled)
