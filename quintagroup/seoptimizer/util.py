from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

def createMultiColumnList(self,slist, numCols, sort_on='title_or_id'):
    try:
        mcl = self.createMultiColumnList(slist, numCols, sort_on=sort_on)
        return mcl
    except AttributeError:
        return [slist]

class SortedDict(dict):
    security = ClassSecurityInfo()
    security.declarePublic('items')    
    def items(self):
        primary_metatags = ['description', 'keywords']
        lst = [(name,self[name]) for name in primary_metatags                    \
                                                 if name in self.keys()] +       \
              [(name, self[name]) for name in self.keys()                        \
                                                 if name not in primary_metatags]
        return lst

try:
    InitializeClass(SortedDict)
except:
    pass
