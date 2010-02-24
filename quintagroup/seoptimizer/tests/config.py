from Products.CMFCore.permissions import ManagePortal

from quintagroup.seoptimizer.config import *

FIELDS = ['seo_title', 'seo_description', 'seo_keywords']

PROPS = {'stop_words':STOP_WORDS, 'fields':FIELDS, 'additional_keywords': []}

CUSTOM_METATAGS = [{'meta_name'    : 'metatag1',
                    'meta_content' : 'metatag1value'},
                   {'meta_name'    : 'metatag2',
                    'meta_content' : 'metatag2value'},
                   {'meta_name'    : 'metatag3',
                    'meta_content' : ''}
                  ]
VIEW_METATAGS = ['DC.creator', 'DC.format', 'DC.date.modified', 'DC.date.created', 'DC.type',
                   'DC.distribution', 'description', 'keywords', 'robots', 'distribution']

GLOBAL_CUSTOM_METATAGS = {'default_custom_metatags':'metatag1|global_metatag1value\nmetatag4|global_metatag4value'}

CONFIGLETS = ({'id':'qSEOptimizer',
    'name':'Search Engine Optimizer',
    'action':'string:${portal_url}/seo-controlpanel',
    'condition':'',
    'category':'Products',
    'visible':1,
    'appId':'qSEOptimizer',
    'permission':ManagePortal},)

qSEO_CONTENT = ['File','Document','News Item']
qSEO_FOLDER  = []
qSEO_TYPES   = qSEO_CONTENT + qSEO_FOLDER
