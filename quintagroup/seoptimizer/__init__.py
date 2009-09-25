from AccessControl import allow_module
from zope.component import queryMultiAdapter

from Acquisition import aq_inner
from DateTime import DateTime

from Products.CMFCore.utils import getToolByName

from quintagroup.seoptimizer.interfaces import IKeywords, IMappingMetaTags
from quintagroup.seoptimizer.util import SortedDict

allow_module('quintagroup.seoptimizer.util')
qSEO_globals = globals()


try:
    from Products.CMFPlone.PloneTool import PloneTool, METADATA_DCNAME, \
        FLOOR_DATE, CEILING_DATE
    _present = hasattr(PloneTool, "listMetaTags")
except ImportError:
    _present = False


if _present:
    old_lmt = PloneTool.listMetaTags

    def listMetaTags(self, context):
        """Lists meta tags helper.

        Creates a mapping of meta tags.
        """

        from quintagroup.seoptimizer.browser.interfaces import IPloneSEOLayer
        if not IPloneSEOLayer.providedBy(self.REQUEST):
            return old_lmt(getToolByName(self, 'plone_utils'), context)

        result = SortedDict()
        site_props = getToolByName(self, 'portal_properties').site_properties
        use_all = site_props.getProperty('exposeDCMetaTags', None)

        seo_context = queryMultiAdapter((context, self.REQUEST), name='seo_context')
        adapter = IMappingMetaTags(context, None)
        mapping_metadata = adapter and adapter.getMappingMetaTags() or SortedDict()

        if not use_all:
            metadata_names = mapping_metadata.has_key('DC.description') and {'DC.description': mapping_metadata['DC.description']} or SortedDict()
            if mapping_metadata.has_key('description'):
                metadata_names['description'] = mapping_metadata['description']
        else:
            metadata_names = mapping_metadata

        for key, accessor in metadata_names.items():
            if accessor == 'seo_keywords':
                # Set the additional matching keywords, if any
                adapter = IKeywords(context, None)
                if adapter is not None:
                    keywords = adapter.listKeywords()
                    if keywords:
                        result['keywords'] = keywords
                continue

            method = getattr(seo_context, accessor, None)
            if method is None:
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

            # Special cases
            if accessor == 'Description' and not metadata_names.has_key('description'):
                result['description'] = value
            elif accessor == 'Subject' and not metadata_names.has_key('keywords'):
                result['keywords'] = value

            if accessor not in ('Description', 'Subject'):
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

        # add custom meta tags (added from qseo tab by user) for given context and default from configlet
        custom_meta_tags = seo_context and seo_context.seo_customMetaTags() or []
        for tag in custom_meta_tags:
            if tag['meta_content']:
                result[tag['meta_name']] = tag['meta_content']

        return result

    PloneTool.listMetaTags = listMetaTags
