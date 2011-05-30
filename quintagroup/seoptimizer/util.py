from AccessControl import ClassSecurityInfo
from htmlentitydefs import entitydefs
import re

try:
    from App.class_init import InitializeClass
    InitializeClass
except ImportError:
    from Globals import InitializeClass


class SortedDict(dict):
    """ A sorted dictionary.
    """
    security = ClassSecurityInfo()

    security.declarePublic('items')

    def items(self):
        primary_metatags = self.pmt
        lst = [(name, self[name]) for name in primary_metatags \
                                  if name in self.keys()] + \
              [(name, self[name]) for name in self.keys() \
                                  if name not in primary_metatags]
        return lst

    security.declarePublic('__init__')

    def __init__(self, *args, **kwargs):
        super(SortedDict, self).__init__(*args, **kwargs)
        self.pmt = []
    security.declarePublic('__setitem__')

    def __setitem__(self, i, y):
        super(SortedDict, self).__setitem__(i, y)
        if i not in self.pmt:
            self.pmt.append(i)
    security.declarePublic('pop')

    def pop(self, k, *args, **kwargs):
        super(SortedDict, self).pop(k, *args, **kwargs)
        if k in self.pmt:
            self.pmt.remove(k)

try:
    InitializeClass(SortedDict)
except:
    pass


def _group_unescape(m):
    if m.group("ent"):
        try:
            return unescape(entitydefs[m.group("ent")])
        except KeyError:
            return m.group(0)
    if m.group("dec"):
        return unichr(int(m.group("dec")))
    if m.group("hex"):
        return unichr(int(m.group("hex"), 16))

expr = re.compile(r'&(?:(?P<ent>\w+?)|'\
                   '#(?P<dec>\d{1,10})|'\
                   '#x(?P<hex>[0-9a-fA-F]{1,8}));')


def unescape(s):
    return expr.sub(_group_unescape, s)
