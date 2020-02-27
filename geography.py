# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 2018
@name:   Geography Object
@author: Jack Kirby Cook

"""

import os.path
import csv

from utilities.dictionarys import SliceOrderedDict as SODict

from variables.variable import Variable

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Geography']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


DELIMITER = '|'
ALLCHAR = '*'
ALLID = 'X'


_DIR = os.path.dirname(os.path.realpath(__file__))
_GEOFILENAME = 'geography.csv'

with open(os.path.join(_DIR, _GEOFILENAME), mode='r') as infile:
    reader = csv.reader(infile)    
    GEOLENGTHS = {row[0]:int(row[1]) for row in reader}


@Variable.register('geography')
class Geography: 
    def __geotype(self, value): return 'all' if value == ALLCHAR else 'each'
    def __geonum(self, key, value): return GEOLENGTHS[key] * ALLID if self.__geotype(value) == 'all' else str(value).zfill(GEOLENGTHS[key])

    def __init__(self, value): super().__init__(SODict([(str(key), str(value)) for key, value in value.items()]))
    def __len__(self): return len(self.value)
    def __str__(self): return DELIMITER.join(['{key}={value}'.format(key=key, value=value) for key, value in self.items()])
    def __repr__(self): return '{}({})'.format(self.__class__.__name__, ', '.join(['{key}={value}'.format(key=key, value=value) for key, value in self.items()]))    
       
    def keys(self): return list(self.value.keys())
    def values(self): return list(self.value.values())
    def items(self): return zip(self.value.keys(), self.value.values())
    def asdict(self): return self.value
    
    def getkey(self, index): return list(self.value.keys())[index]    
    def getvalue(self, index): 
        if isinstance(index, int): return list(self.value.values())[index]  
        elif isinstance(index, str): return self.value[index]
        else: raise TypeError(index)
    
    @property
    def geoid(self): return ''.join([self.__geonum(key, value) for key, value in zip(self.keys(), self.values())])

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

    def __lt__(self, other): return self.geoid < other.geoid
    def __le__(self, other): return self.geoid <= other.geoid
    def __ge__(self, other): return self.geoid >= other.geoid
    def __gt__(self, other): return self.geoid > other.geoid

    def __add__(self, other): return self.add(other)
    def add(self, other, *args, **kwargs):
        assert self[:-1] == other[:-1]
        return self.__class__(SODict([(key, value) if key != self.getkey(-1) else (key, ALLCHAR) for key, value in self.items()]))

    def __contains__(self, other): return self.contains(other)
    def contains(self, other):
        for i in range(len(self)):
            if self.getkey(i) != other.getkey(i): return False
            if self.getvalue(i) != ALLCHAR and self.getvalue(i) != other.getvalue(i): return False
        return True
        
    @classmethod
    def fromstr(cls, geostr, **kwargs):
        return cls(SODict([tuple([*item.split('=')]) for item in geostr.split(DELIMITER)]))





