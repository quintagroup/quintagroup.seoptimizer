from AccessControl import allow_module
from zope.i18nmessageid import MessageFactory

SeoptimizerMessageFactory = MessageFactory('quintagroup.seoptimizer')

allow_module('quintagroup.seoptimizer.util')
