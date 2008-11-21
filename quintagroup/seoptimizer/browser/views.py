from Acquisition import aq_inner
from plone.app.controlpanel.form import ControlPanelView

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

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
