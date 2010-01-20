from Products.CMFCore.utils import getToolByName
from quintagroup.seoptimizer.config import PROJECT_NAME

def install(portal, reinstall=False):
    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.setBaselineContext('profile-%s:uninstall'%PROJECT_NAME)
    if reinstall:
        setup_tool.setBaselineContext('profile-%s:reinstall'%PROJECT_NAME)
        setup_tool.runAllImportStepsFromProfile('profile-%s:reinstall'%PROJECT_NAME)
        return "Ran reinstall steps."
    else:
        setup_tool.setBaselineContext('profile-%s:uninstall'%PROJECT_NAME)
        setup_tool.runAllImportStepsFromProfile('profile-%s:default'%PROJECT_NAME)
        return "Ran all install steps."

def uninstall(portal, reinstall=False):
    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.setBaselineContext('profile-%s:uninstall'%PROJECT_NAME)
    if reinstall:
        return "Ran reinstall steps."
    else:
        setup_tool.runAllImportStepsFromProfile('profile-%s:uninstall'%PROJECT_NAME)
        return "Ran all uninstall steps."
