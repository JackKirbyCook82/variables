# -*- coding: utf-8 -*-
"""
Created on Mon Dec 2 2019
@name:   Address Object
@author: Jack Kirby Cook

"""

from collections import namedtuple as ntuple

from variables.variable import Variable

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Address']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


ADDRESS = ('street', 'city', 'state', 'zipcode')
ADDRESSFORMAT = '{street}, {city}, {state} {zipcode}'
AddressSgmts = ntuple('AddressSgmts', ' '.join(ADDRESS))


@Variable.register('address')
class Address: 
    fields = ADDRESS
        
    def __init__(self, **kwargs): super().__init__(AddressSgmts({field:kwargs[field] for field in self.fields})) 
    def __len__(self): return len(self.value)
    def __str__(self): return ADDRESSFORMAT.format(**self.todict())
    def __repr__(self): return '{}({})'.format(self.__class__.__name__, ', '.join(['{key}={value}'.format(key=key, value=value) for key, value in self.todict().items()]))
    
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

















