# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 2018
@name:   Geography Object
@author: Jack Kirby Cook

"""

import os.path
import csv
from collections import OrderedDict as ODict

from utilities.dictionarys import SliceOrderedDict as SODict

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Geography']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


_DIR = os.path.dirname(os.path.realpath(__file__))
_GEOFORMATS = {'all':'{key}={allchar}', 'each':'{key}={name}({value})'}
_GEOFILENAME = 'geography.csv'
_DELIMITER = ', '
_ALLCHAR = '*'

with open(os.path.join(_DIR, _GEOFILENAME), mode='r') as infile:
    reader = csv.reader(infile)    
    _GEOLENGTHS = {row[0]:int(row[1]) for row in reader}
    _GEOGRAPHYS = {row[0] for row in reader}


class Geography(object): 
    def __init__(self, **items): 
        self.__items = SODict([(key, str(value['id'])) if isinstance(value, (dict, ODict, SODict)) else (key, str(value)) for key, value in items.items()])
        names = {key:value.get('name', None) for key, value in items.items() if isinstance(value, (dict, ODict, SODict))}
        names = {key:value for key, value in names.items() if value}
        self.__setnames(names)   
                    
    def __setnames(self, names): self.__names = SODict([(key, names[key]) for key in self.__items.keys() if key in names.keys()])
        
    def keys(self): return list(self.__items.keys())
    def values(self): return list(self.__items.values())
    def names(self): return [self.__names.get(key, '') for key in self.__items.keys()]
    def items(self): return zip(self.keys(), self.values(), self.names())
    
    def getkey(self, index): return self.keys()[index]    
    def getvalue(self, index): return self.values()[index]  
    def getname(self, index): return self.names()[index]
        
    def geonum(self, key, value): return _GEOLENGTHS[key] * 'X' if value == _ALLCHAR else str(value).zfill(_GEOLENGTHS[key])
    def geoformat(self, key, value, name): return _GEOFORMATS['all' if value == _ALLCHAR else 'each'].format(key=key, value=self.geonum(key, value), name=name, allchar=_ALLCHAR)
    
    @property
    def geoid(self): return ''.join([self.geonum(key, value) for key, value in zip(self.keys(), self.values())])
    def __str__(self): return self.delimiter.join([self.geoformat(key, value, name) for key, value, name in self.items()])
    def __repr__(self): return '{}({})'.format(self.__class__.__name__, {key:({'id':value, 'name':name} if name else value) for key, value, name in self.items()})
    
    def withnames(self, names): return self.__class__(**{key:{'id':value, 'name':names.get(key, None)} for key, value in zip(self.keys(), self.values())})
    
    def __getitem__(self, key):
        if isinstance(key, str): return self.__class__(**{key:{'id':self.__items[key], 'name':self.__names[key]}})
        elif isinstance(key, int): return self.__class__(**{self.getkey(key):{'id':self.getvalue(key), 'name':self.getname(key)}})
        elif isinstance(key, slice): return self.__class__(**{geokey:{'id':geovalue, 'name':self.__names.get(geokey, None)} for geokey, geovalue in self.__items[key].items()})
        else: raise TypeError(type(key))

    def __eq__(self, other):
        if not isinstance(other, self.__class__): raise TypeError(type(other))
        return all([self.keys() == other.keys(), self.values() == other.values()])
    def __ne__(self, other): return not self.__eq__(other)  








