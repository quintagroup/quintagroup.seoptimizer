from Products.CMFCore.utils import getToolByName

from quintagroup.seoptimizer.config import PROJECT_NAME

# our GenericSetup profile names
INSTALL = 'profile-%s:default' % PROJECT_NAME
REINSTALL = 'profile-%s:reinstall' % PROJECT_NAME
UNINSTALL = 'profile-%s:uninstall' % PROJECT_NAME

def install(portal, reinstall=False):
    """ (Re)Install this product.

        This external method is need, because portal_quickinstaller doens't know
        what GenericProfile profile to apply when reinstalling a product.
    """
    setup_tool = getToolByName(portal, 'portal_setup')
    if reinstall:
        setup_tool.runAllImportStepsFromProfile(REINSTALL)
        return "Ran all reinstall steps."
    else:
        setup_tool.runAllImportStepsFromProfile(INSTALL)
        return "Ran all install steps."

def uninstall(portal, reinstall=False):
    """ Uninstall this product.

        This external method is need, because portal_quickinstaller doens't know
        what GenericProfile profile to apply when uninstalling a product.
    """
    setup_tool = getToolByName(portal, 'portal_setup')
    if reinstall:
        return "Ran all reinstall steps."
    else:
        setup_tool.runAllImportStepsFromProfile(UNINSTALL)
        return "Ran all uninstall steps."
