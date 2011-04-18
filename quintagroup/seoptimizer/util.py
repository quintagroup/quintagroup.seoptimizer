from AccessControl import ClassSecurityInfo

try:
    from App.class_init import InitializeClass
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
