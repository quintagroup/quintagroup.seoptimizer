from Acquisition import aq_inner
from zope.component import queryAdapter
from plone.app.controlpanel.form import ControlPanelView

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

SEPERATOR = '|'
HAS_CANONICAL_PATH = True
SEO_PREFIX = 'seo_'
PROP_PREFIX = 'qSEO_'
SUFFIX = '_override'
PROP_CUSTOM_PREFIX = 'qSEO_custom_'

try:
    from quintagroup.canonicalpath.interfaces import ICanonicalPath
except ImportError:
    HAS_CANONICAL_PATH = False

class SEOContext( BrowserView ):
    """
    """
    def getSEOProperty( self, property_name, accessor='' ):
        """
        """
        context = aq_inner(self.context)

        if context.hasProperty(property_name):
            return context.getProperty(property_name)
        
        if accessor:
            method = getattr(context, accessor, None)
            if not callable(method):
                return None

            # Catch AttributeErrors raised by some AT applications
            try:
                value = method()
            except AttributeError:
                value = None
        
            return value

    def seo_title( self ):
        """
        """
        return self.getSEOProperty( 'qSEO_title', accessor='Title' )

    def seo_robots( self ):
        """
        """
        robots = self.getSEOProperty( 'qSEO_robots' )
        return robots and robots or 'ALL'

    def seo_description( self ):
        """
            Generate Description from SEO properties 
        """
        
        return self.getSEOProperty( 'qSEO_description', accessor = 'Description')

    def seo_distribution( self ):
        """
           Generate Description from SEO properties
        """
        dist = self.getSEOProperty( 'qSEO_distribution' )

        return dist and dist or 'Global'

    def seo_customMetaTags( self ):
        """
        """
        tags = self.seo_globalCustomMetaTags()
        loc = self.seo_localCustomMetaTags()

        names = [i['meta_name'] for i in tags]
        add_tags = []
        for i in loc:
            if i['meta_name'] in names:
                for t in tags:
                    if t['meta_name'] == i['meta_name']:
                        t['meta_content'] = i['meta_content']
            else:
                add_tags.append(i)
        tags.extend(add_tags)
        return tags

    def seo_globalWithoutLocalCustomMetaTags( self ):
        """
        """
        glob = self.seo_globalCustomMetaTags()
        loc = self.seo_localCustomMetaTags()
        names = [i['meta_name'] for i in loc]
        tags = []
        for i in glob:
            if i['meta_name'] not in names:
                tags.append(i)
        return tags

    def seo_localCustomMetaTags( self ):
        """
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
        """
        """
        result = []
        context = aq_inner(self.context)
        site_properties = getToolByName(context, 'portal_properties')
        if hasattr(site_properties, 'seo_properties'):
            custom_meta_tags = getattr(site_properties.seo_properties, 'default_custom_metatags', [])
            for tag in custom_meta_tags:
                name_value = tag.split(SEPERATOR)
                if name_value[0]:
                    result.append({'meta_name'    : name_value[0],
                                   'meta_content' : len(name_value) == 2 and name_value[1] or ''})
        return result

    def seo_nonEmptylocalMetaTags( self ):
        """
        """
        return bool(self.seo_localCustomMetaTags())

    def seo_html_comment( self ):
        """
        """
        html_comment = self.getSEOProperty( 'qSEO_html_comment' )
        return html_comment and html_comment or '' 
        
    def seo_keywords( self ):
        """
           Generate Keywords from SEO properties
        """

        prop_name = 'qSEO_keywords'
        add_keywords = 'additional_keywords'
        accessor = 'Subject'
        context = aq_inner(self.context)

        keywords = []
        if context.hasProperty(prop_name):
            keywords = context.getProperty(prop_name)

        pprops = getToolByName(context, 'portal_properties')
        sheet = getattr(pprops, 'seo_properties', None)
        if sheet and sheet.hasProperty(add_keywords):
            keywords += sheet.getProperty(add_keywords)

        if keywords:
            return keywords

        method = getattr(context, accessor, None)
        if not callable(method):
            return None

        # Catch AttributeErrors raised by some AT applications
        try:
            value = method()
        except AttributeError:
            value = None

        return value
    
    def seo_canonical( self ):
        """
           Get canonical URL
        """
        canonical = self.getSEOProperty( 'qSEO_canonical' )

        if not canonical and HAS_CANONICAL_PATH:
            canpath = queryAdapter(self.context, ICanonicalPath)
            if canpath:
                purl = getToolByName(self.context, 'portal_url')()
                cpath = canpath.canonical_path()
                canonical = purl + cpath

        return canonical and canonical or self.context.absolute_url()


class SEOControlPanel( ControlPanelView ):
    """
    """
    template = ViewPageTemplateFile('templates/seo_controlpanel.pt')

    @property
    def portal_properties( self ):
        """
        """
        context = aq_inner(self.context)
        return getToolByName(context, 'portal_properties')

    @property
    def portal_types( self ):
        """
        """
        context = aq_inner(self.context)
        return getToolByName(context, 'portal_types')

    def hasSEOAction( self, type_info ):
        """
        """
        return filter(lambda x:x.id == 'seo_properties', type_info.listActions())

    def test( self, condition, first, second ):
        """
        """
        return condition and first or second 

    def getExposeDCMetaTags( self ):
        """
        """
        sp = self.portal_properties.site_properties
        return sp.getProperty('exposeDCMetaTags')

    def getDefaultCustomMetatags( self ):
        """
        """
        seo = self.portal_properties.seo_properties
        return seo.getProperty('default_custom_metatags')

    def getMetaTagsOrder( self ):
        """
        """
        seo = self.portal_properties.seo_properties
        return seo.getProperty('metatags_order')

    def getAdditionalKeywords( self ):
        """
        """
        seo = self.portal_properties.seo_properties
        return seo.getProperty('additional_keywords')

    def createMultiColumnList( self ):
        """
        """
        context = aq_inner(self.context)
        allTypes = self.portal_types.listContentTypes()
        try:
            return context.createMultiColumnList(allTypes, sort_on='title_or_id')
        except AttributeError:
            return [slist]

    def __call__( self ):
        """
        """
        context = aq_inner(self.context)
        request = self.request

        portalTypes=request.get( 'portalTypes', [] )
        exposeDCMetaTags=request.get( 'exposeDCMetaTags', None )
        additionalKeywords=request.get('additionalKeywords', [])
        default_custom_metatags=request.get('default_custom_metatags', [])
        metatags_order=request.get('metatags_order', [])

        site_props = getToolByName(self.portal_properties, 'site_properties')
        seo_props = getToolByName(self.portal_properties, 'seo_properties')

        form = self.request.form
        submitted = form.get('form.submitted', False)

        if submitted:
            site_props.manage_changeProperties(exposeDCMetaTags=exposeDCMetaTags)
            seo_props.manage_changeProperties(additional_keywords=additionalKeywords)
            seo_props.manage_changeProperties(default_custom_metatags=default_custom_metatags)
            seo_props.manage_changeProperties(metatags_order=metatags_order)

            for ptype in self.portal_types.objectValues():
                acts = filter(lambda x: x.id == 'seo_properties', ptype.listActions())
                action = acts and acts[0] or None
                if ptype.getId() in portalTypes:
                    if action is None:
                        ptype.addAction('seo_properties',
                                        'SEO Properties',
                                        'string:${object_url}/qseo_properties_edit_form',
                                        '',
                                        'Modify portal content',
                                        'object',
                                        visible=1)
                else:
                    if action !=None:
                        actions = list(ptype.listActions())
                        ptype.deleteActions([actions.index(a) for a in actions if a.getId()=='seo_properties'])
            return request.response.redirect('%s/%s'%(self.context.absolute_url(), '@@seo-controlpanel'))
        else:
            return self.template(portalTypes=portalTypes, exposeDCMetaTags=exposeDCMetaTags)

    def typeInfo( self, type_name ):
        """
        """
        return self.portal_types.getTypeInfo( type_name )


class SEOContextPropertiesView( BrowserView ):
    """
    """
    template = ViewPageTemplateFile('templates/seo_context_properties.pt')


    def test( self, condition, first, second ):
        """
        """
        return condition and first or second 
      
    def setProperty(self, property, value, type='string'):
        context = aq_inner(self.context)
        if context.hasProperty(property):
            context.manage_changeProperties({property: value})
        else:
            context.manage_addProperty(property, value, type)

    def manageSEOProps(self, **kw):
        context = aq_inner(self.context)
        delete_list, overrides, values = [], [], []
        seo_items = dict([(k[len(SEO_PREFIX):],v) for k,v in kw.items() if k.startswith(SEO_PREFIX)])
        for key in seo_items.keys():
            if key.endswith(SUFFIX):
                overrides.append(key[:-len(SUFFIX)])
            else:
                values.append(key)

        for val in values:
            if val in overrides and seo_items[val+SUFFIX]:
                self.setProperty(PROP_PREFIX+val, seo_items[val])
            elif context.hasProperty(PROP_PREFIX+val):
                delete_list.append(PROP_PREFIX+val)
        if delete_list: context.manage_delProperties(delete_list)

    def setSEOCustomMetaTags(self, custommetatags):
        context = aq_inner(self.context)
        for k, v in custommetatags.items():
            self.setProperty('%s%s' % (PROP_CUSTOM_PREFIX, meta_name), meta_content)   

    def delAllSEOCustomMetaTagsByNames(self):
        context = self.context
        delete_list = []
        for property, value in context.propertyItems():
            if property.find(PROP_CUSTOM_PREFIX) == 0 and len(property) > len(PROP_CUSTOM_PREFIX):
                delete_list.append(property)
        if delete_list: context.manage_delProperties(delete_list)        

    def delSEOCustomMetaTagByName(self, custommetatagname):
        context = self.context
        seo_custom_prop = PROP_CUSTOM_PREFIX + custommetatagname
        if context.hasProperty(seo_custom_prop):
            context.manage_delProperties([seo_custom__prop])

    def updateSEOCustomMetaTags(self, custommetatags):
        context = aq_inner(self.context)
        site_properties = getToolByName(context, 'portal_properties')
        globalCustomMetaTags = []

        if hasattr(site_properties, 'seo_properties'):
            custom_meta_tags = getattr(site_properties.seo_properties, 'default_custom_metatags', [])
            for tag in custom_meta_tags:
                name_value = tag.split(SEPERATOR)
                if name_value[0]:
                    globalCustomMetaTags.append({'meta_name'    : name_value[0],
                                                 'meta_content' : len(name_value) == 1 and '' or name_value[1]})
  
        for tag in custommetatags:
            metalist = []
            meta_name, meta_content = tag['meta_name'], tag['meta_content']
            if meta_name:
                if not [gmt for gmt in globalCustomMetaTags if (gmt['meta_name']==meta_name and gmt['meta_content']==meta_content)]:
                    metalist.append(tag)
                self.setSEOCustomMetaTags(metalist)
      
    def manageSEOCustomMetaTags(self, **kw):
        context = aq_inner(self.context)
        if kw.has_key('seo_custommetatags_override'):
            if kw.get('seo_custommetatags_override'):
                custommetatags = kw.get('seo_custommetatags', {})
                self.updateSEOCustomMetaTags(custommetatags)
            else:
                self.delAllSEOCustomMetaTagsByNames()
        elif kw.get('seo_custommetatags'):
            self.delAllSEOCustomMetaTagsByNames()

    def __call__( self ):
        """
        """
        context = aq_inner(self.context)
        request = self.request
        form = self.request.form
        submitted = form.get('form.submitted', False)
        if submitted:
            self.manageSEOProps(**form)
            self.manageSEOCustomMetaTags(**form)
            msg = 'Content SEO properties have been saved.'
            context.plone_utils.addPortalMessage(msg)
            return request.response.redirect(self.context.absolute_url())
        else:
            return self.template()
