from AccessControl import allow_module
from util import SortedDict
from Acquisition import aq_inner
from DateTime import DateTime

from Products.CMFCore.utils import getToolByName

allow_module('quintagroup.seoptimizer.util')
qSEO_globals = globals()


try:
    from Products.CMFPlone.PloneTool import PloneTool, METADATA_DCNAME
    _present = hasattr(PloneTool, "listMetaTags")
except ImportError:
    _present = False



if _present:
    old_lmt = PloneTool.listMetaTags

    def listMetaTags(self, context):
        """Lists meta tags helper.

        Creates a mapping of meta tags -> values for the listMetaTags script.
        """
        result = {}
        site_props = getToolByName(self, 'portal_properties').site_properties
        use_all = site_props.getProperty('exposeDCMetaTags', None)

        if not use_all:
            metadata_names = {'Description': METADATA_DCNAME['Description']}
        else:
            metadata_names = METADATA_DCNAME

        for accessor, key in metadata_names.items():
            method = getattr(aq_inner(context).aq_explicit, accessor, None)
            if not callable(method):
                continue

            # Catch AttributeErrors raised by some AT applications
            try:
                value = method()
            except AttributeError:
                value = None

            if not value:
                # No data
                continue
            if accessor == 'Publisher' and value == 'No publisher':
                # No publisher is hardcoded (TODO: still?)
                continue
            if isinstance(value, (list, tuple)):
                # convert a list to a string
                value = ', '.join(value)

#          Exclusion meta tag description and keywords
#            # Special cases
#            if accessor == 'Description':
#                result['description'] = value
#            elif accessor == 'Subject':
#                result['keywords'] = value

            if use_all:
                result[key] = value

        if use_all:
            created = context.CreationDate()

            try:
                effective = context.EffectiveDate()
                if effective == 'None':
                    effective = None
                if effective:
                    effective = DateTime(effective)
            except AttributeError:
                effective = None

            try:
                expires = context.ExpirationDate()
                if expires == 'None':
                    expires = None
                if expires:
                    expires = DateTime(expires)
            except AttributeError:
                expires = None

            # Filter out DWIMish artifacts on effective / expiration dates
            if effective is not None and \
               effective > FLOOR_DATE and \
               effective != created:
                eff_str = effective.Date()
            else:
                eff_str = ''

            if expires is not None and expires < CEILING_DATE:
                exp_str = expires.Date()
            else:
                exp_str = ''

            if exp_str or exp_str:
                result['DC.date.valid_range'] = '%s - %s' % (eff_str, exp_str)

        return result

    PloneTool.listMetaTags = listMetaTags
