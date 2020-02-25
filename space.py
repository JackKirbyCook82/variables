# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 2020
@name:   Space Object
@author: Jack Kirby Cook

"""

from variables.variable import Variable

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Space']
__copyright__ = "Copyright 2020, Jack Kirby Cook"
__license__ = ""


_aslist = lambda items: [items] if not isinstance(items, (list, tuple)) else list(items)
_filterempty = lambda items: [item for item in _aslist(items) if item is not None]

_SPACE = ('sqft', 'bedrooms', 'rooms')
                

@Variable.register('space')
class Space:
    fields = _SPACE
    delimiter = '|'    
    
    def __init__(self, **kwargs): super().__init__({attr:kwargs.get(attr, None) for attr in self.fields})
    def __getattr__(self, attr): return self.value[attr]
    def __getitem__(self, attr): return self.value[attr]
    
    def __len__(self): return len(_filterempty(list(self.value.values())))
    def __repr__(self): return '{}({})'.format(self.__class__.__name__,  ', '.join(['{}={}'.format(key, value) for key, value in self.items() if value is not None])) 
    def __str__(self): return self.delimiter.join(['{}={}'.format(key, str(value)) for key, value in self.items() if value is not None])
    
    def items(self): return zip(self.value.keys(), self.value.values())
    def asdict(self): return self.value
    
    @classmethod
    def fromstr(cls, spacestr, **kwargs):
        return cls({item.split('=')[0]:item.split('=')[1] for item in spacestr.split(cls.delimiter)})    
