# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 2018
@name:   Geography Objects
@author: Jack Kirby Cook

"""

import os.path
import csv
from collections import namedtuple as ntuple

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
ADDRESS = ('street', 'city', 'state', 'zipcode')
ADDRESSFORMAT = '{street}, {city}, {state} {zipcode}'
AddressSgmts = ntuple('AddressSgmts', ' '.join(ADDRESS))

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
    def __hash__(self): return hash((self.__class__.__name__, self.geoID,))   
    
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
    def geoID(self): return ''.join([self.__geonum(key, value) for key, value in zip(self.keys(), self.values())])

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


@Variable.register('geopath')
class Geopath: 
    def __geotype(self, value): return 'all' if value == ALLCHAR else 'each'

    def __init__(self, value): super().__init__(SODict([(key, value) for key, value in value.items()]))
    def __len__(self): return len(self.value)
    def __str__(self): return DELIMITER.join(['{key}={value}'.format(key=key, value=value) for key, value in self.items()])
    def __repr__(self): return '{}({})'.format(self.__class__.__name__, ', '.join(['{key}={value}'.format(key=key, value=value) for key, value in self.items()]))
    def __hash__(self): return hash((self.__class__.__name__, tuple(self.keys), tuple(self.values),))  
    
    def keys(self): return list(self.value.keys())
    def values(self): return list(self.value.values())
    def items(self): return zip(self.value.keys(), self.value.values())
    def asdict(self): return self.value
    
    def getkey(self, index): return list(self.value.keys())[index]    
    def getvalue(self, index): 
        if isinstance(index, int): return list(self.value.values())[index]  
        elif isinstance(index, str): return self.value[index]
        else: raise TypeError(index) 

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
        return cls(SODict([tuple([*item.split('=')]) for item in geostr.split(DELIMITER)]))


@Variable.register('address')
class Address: 
    fields = ADDRESS
        
    def __init__(self, **kwargs): super().__init__(AddressSgmts({field:kwargs[field] for field in self.fields})) 
    def __len__(self): return len(self.value)
    def __str__(self): return ADDRESSFORMAT.format(**self.todict())
    def __repr__(self): return '{}({})'.format(self.__class__.__name__, ', '.join(['{key}={value}'.format(key=key, value=value) for key, value in self.todict().items()]))
    def __hash__(self): return hash((self.__class__.__name__, *self.value,))  
    
    def keys(self): return list(self.value.todict().keys())
    def values(self): return list(self.value.todict().values())
    def todict(self): return self.value._asdict()
    
    def __getitem__(self, key): return self.value.todict()[key]
    def __getattr__(self, attr): return getattr(self.value, attr)  

    def __lt__(self, other): return str(self) < str(other)
    def __le__(self, other): return str(self) <= str(other)
    def __ge__(self, other): return str(self) >= str(other)
    def __gt__(self, other): return str(self) > str(other)
        
    @classmethod
    def fromstr(cls, addressstr, **kwargs): 
        street, city, state_zipcode = addressstr.split(',')
        state, zipcode = state_zipcode.split(' ')
        return cls(street, city, state, zipcode)



