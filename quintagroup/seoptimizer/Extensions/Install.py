import logging
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.upgrade import _upgrade_registry

from quintagroup.seoptimizer.config import PROJECT_NAME

logger = logging.getLogger('quintagroup.seoptimizer')

# our GenericSetup profile names
INSTALL = 'profile-%s:default' % PROJECT_NAME
UNINSTALL = 'profile-%s:uninstall' % PROJECT_NAME


def install(portal, reinstall=False):
    """ (Re)Install this product.

        This external method is need, because portal_quickinstaller doens't
        know what GenericProfile profile to apply when reinstalling a product.
    """
    setup_tool = getToolByName(portal, 'portal_setup')
    if reinstall:
        step = None
        profile_id = 'quintagroup.seoptimizer:default'
        steps_to_run = [s['id'] for s in \
                        setup_tool.listUpgrades(profile_id, show_old=False)]
        for step_id in steps_to_run:
            step = _upgrade_registry.getUpgradeStep(profile_id, step_id)
            step.doStep(setup_tool)
            msg = "Ran upgrade step %s for profile %s" \
                  % (step.title, profile_id)
            logger.log(logging.INFO, msg)
        # We update the profile version to the last one we have reached
        # with running an upgrade step.
        if step and step.dest is not None and step.checker is None:
            setup_tool.setLastVersionForProfile(profile_id, step.dest)
        return "Ran all reinstall steps."
    else:
        setup_tool.runAllImportStepsFromProfile(INSTALL)
        return "Ran all install steps."


def uninstall(portal, reinstall=False):
    """ Uninstall this product.

        This external method is need, because portal_quickinstaller doens't
        know what GenericProfile profile to apply when uninstalling a product.
    """
    setup_tool = getToolByName(portal, 'portal_setup')
    if reinstall:
        return "Ran all reinstall steps."
    else:
        setup_tool.runAllImportStepsFromProfile(UNINSTALL)
        return "Ran all uninstall steps."
