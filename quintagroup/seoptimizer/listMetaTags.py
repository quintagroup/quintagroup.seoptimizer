from Products.CMFPlone.PloneTool import PloneTool

originalListMetaTags = PloneTool.listMetaTags

def qsListMetaTags(self, context):
    """ Custom listMetaTags method
    """
    return {}

def qsListMetaTagsOriginal(self, context):
    """ Returned original method listMetaTags
    """
    return originalListMetaTags(self, context)
