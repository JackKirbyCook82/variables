# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 2018
@name:   GeoPath Object
@author: Jack Kirby Cook

"""

from utilities.dictionarys import SliceOrderedDict as SODict

from variables.variable import Variable

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Geopath']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


@Variable.register('geopath')
class Geopath: 
    delimiter = '|'
    allChar = '*'
    allID = 'X'
    
    def __geotype(self, value): return 'all' if value == self.allChar else 'each'

    def __init__(self, value): super().__init__(SODict([(key, value) for key, value in value.items()]))
    def __hash__(self): return hash(str(self))
    
    def keys(self): return list(self.value.keys())
    def values(self): return list(self.value.values())
    def items(self): return zip(self.value.keys(), self.value.values())
    def asdict(self): return self.value
    
    def getkey(self, index): return list(self.value.keys())[index]    
    def getvalue(self, index): 
        if isinstance(index, int): return list(self.value.values())[index]  
        elif isinstance(index, str): return self.value[index]
        else: raise TypeError(index)

    def __len__(self): return len(self.value)
    def __str__(self): return self.delimiter.join(['{key}={value}'.format(key=key, value=value) for key, value in self.items()])
    def __repr__(self): return '{}({})'.format(self.__class__.__name__, ', '.join(['{key}={value}'.format(key=key, value=value) for key, value in self.items()]))

    def get(self, key, default): return self.value.get(key, default)   
    def __getitem__(self, key):
        if isinstance(key, str): return self.__class__({key:self.value[key]})
        elif isinstance(key, int): return self.__class__({self.getkey(key):self.getvalue(key)})
        elif isinstance(key, slice): return self.__class__(self.value[key])
        else: raise TypeError(type(key))

    def __eq__(self, other):
        if not isinstance(other, self.__class__): raise TypeError(type(other))
        return all([self.keys() == other.keys(), self.values() == other.values()])
    def __ne__(self, other): return not self.__eq__(other)  

    @classmethod
    def fromstr(cls, geostr, **kwargs):
        return cls(SODict([tuple([*item.split('=')]) for item in geostr.split(cls.delimiter)]))





