from Acquisition import aq_inner
from plone.app.controlpanel.form import ControlPanelView

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

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
           Return context's properties prefixed with qSEO_custom_
        """
        result = []
        added = []
        property_prefix = 'qSEO_custom_'

        context = aq_inner(self.context)

        for property, value in context.propertyItems():
            idx = property.find(property_prefix)
            if idx == 0 and len(property) > len(property_prefix):
                added.append(property[len(property_prefix):])
                result.append({'meta_name'    : property[len(property_prefix):],
                               'meta_content' : value})

        site_properties = getToolByName(context, 'portal_properties')
        if hasattr(site_properties, 'seo_properties'):
            names = getattr(site_properties.seo_properties, 'default_custom_metatags', [])
            for name in names:
                if name not in added:
                    result.append({'meta_name'    : name,
                                   'meta_content' : ''})
        return result
    
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

        site_props = getToolByName(self.portal_properties, 'site_properties')
        seo_props = getToolByName(self.portal_properties, 'seo_properties')

        form = self.request.form
        submitted = form.get('form.submitted', False)

        if submitted:
            site_props.manage_changeProperties(exposeDCMetaTags=exposeDCMetaTags)
            seo_props.manage_changeProperties(additional_keywords=additionalKeywords)
            seo_props.manage_changeProperties(default_custom_metatags=default_custom_metatags)

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
