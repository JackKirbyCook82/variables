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

from variables.variable import Variable

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Geography']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


_DIR = os.path.dirname(os.path.realpath(__file__))
_GEOFILENAME = 'geography.csv'
_ALLCHAR = '*'
_DELIMITER = ' & '
_ALLID = 'X'

with open(os.path.join(_DIR, _GEOFILENAME), mode='r') as infile:
    reader = csv.reader(infile)    
    _GEOLENGTHS = {row[0]:int(row[1]) for row in reader}

_geotype = lambda value: 'all' if value == _ALLCHAR else 'each'

_geoformats = {'all': lambda kwargs: '{key}={allchar}',
               'each': lambda kwargs: '{key}={name}|{value}' if kwargs['name'] else '{key}={value}'}
_geonum = lambda kwargs: _GEOLENGTHS[kwargs['key']] * _ALLID if _geotype(kwargs['value']) == 'all' else str(kwargs['value']).zfill(_GEOLENGTHS[kwargs['key']])
_geoformat = lambda kwargs: _geoformats[_geotype(kwargs['value'])](kwargs).format(**kwargs, allchar=_ALLCHAR)

_geounformats = lambda item, string: {'key': string.split('=')[0],
                                      'geocode': string.split('=')[-1].split('|')[1] if '|' in string.split('=')[-1] else string.split('=')[-1],
                                      'geoname': string.split('=')[-1].split('|')[0] if '|' in string.split('=')[-1] else None}[item]  
_geounformat = lambda string: tuple([_geounformats('key', string), {item:_geounformats(item, string) for item in ('geocode', 'geoname')}])


@Variable.register('geography')
class Geography(Variable): 
    delimiter = _DELIMITER

    def __init__(self, **items): 
        geocodes = SODict([(key, str(value['geocode'])) if isinstance(value, (dict, ODict, SODict)) else (key, str(value)) for key, value in items.items()])
        geonames = {key:value.get('geoname', None) for key, value in items.items() if isinstance(value, (dict, ODict, SODict))}
        geonames = {key:value for key, value in geonames.items() if value}
        geonames = SODict([(key, geonames[key]) for key in geocodes.keys() if key in geonames.keys()])
        super().__init__(dict(geocodes=geocodes, geonames=geonames))

    @property
    def geocodes(self): return self.value['geocodes']
    @property
    def geonames(self): return self.value['geonames']

    def keys(self): return list(self.geocodes.keys())
    def values(self): return list(self.geocodes.values())
    def names(self): return [self.geonames.get(key, '') for key in self.geocodes.keys()]
    def items(self): return zip(self.keys(), self.values(), self.names())
    
    def getkey(self, index): return self.keys()[index]    
    def getvalue(self, index): return self.values()[index]  
    def getname(self, index): return self.names()[index]
    
    @property
    def geoid(self): return ''.join([_geonum(dict(key=key, value=value)) for key, value in zip(self.keys(), self.values())])
    def __len__(self): return len(self.value['geocodes'])
    def __str__(self): return self.delimiter.join([_geoformat(dict(key=key, value=value, name=name)) for key, value, name in self.items()])
    def __repr__(self): 
        string = lambda kwargs: str({key:value for key, value in kwargs.items() if value})
        return '{}({})'.format(self.__class__.__name__, ', '.join([key + '=' + string(dict(value=value, name=name)) for key, value, name in self.items()]))
    
    def withnames(self, names): return self.__class__(**{key:{'geocode':value, 'geoname':names.get(key, None)} for key, value in zip(self.keys(), self.values())})
    
    def __getitem__(self, key):
        if isinstance(key, str): return self.__class__(**{key:{'geocode':self.geocodes[key], 'geoname':self.geonames[key]}})
        elif isinstance(key, int): return self.__class__(**{self.getkey(key):{'geocode':self.getvalue(key), 'geoname':self.getname(key)}})
        elif isinstance(key, slice): return self.__class__(**{geokey:{'geocode':geovalue, 'geoname':self.geonames.get(geokey, None)} for geokey, geovalue in self.geocodes[key].items()})
        else: raise TypeError(type(key))

    def __eq__(self, other):
        if not isinstance(other, self.__class__): raise TypeError(type(other))
        return all([self.keys() == other.keys(), self.values() == other.values()])
    def __ne__(self, other): return not self.__eq__(other)  

    @classmethod
    def fromstr(cls, geostr, **kwargs):
        items = ODict([_geounformat(item) for item in geostr.split(cls.delimiter)])
        return cls(**items)

