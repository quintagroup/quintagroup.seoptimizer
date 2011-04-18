from Products.CMFPlone.PloneTool import PloneTool

originalListMetaTags = PloneTool.listMetaTags


def qsListMetaTags(self, context):
    """ Custom listMetaTags method
    """
    from quintagroup.seoptimizer.browser.interfaces import IPloneSEOLayer
    if not IPloneSEOLayer.providedBy(self.REQUEST):
        return originalListMetaTags(self, context)
    return {}


def qsListMetaTagsOriginal(self, context):
    """ Returned original method listMetaTags
    """
    return originalListMetaTags(self, context)
