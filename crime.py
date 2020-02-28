# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 2020
@name:   Crime Object
@author: Jack Kirby Cook

"""

from collections import namedtuple as ntuple

from variables.variable import Variable

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Crime']
__copyright__ = "Copyright 2020, Jack Kirby Cook"
__license__ = ""


CRIME = ('shooting', 'arson', 'burglary', 'assault', 'vandalism', 'robbery', 'arrest', 'other', 'theft')
DELIMITER = '|'
CrimeSgmts = ntuple('CrimeSgmts', ' '.join(CRIME))


@Variable.register('crime')    
class Crime: 
    fields = CRIME
        
    def __init__(self, **kwargs): super().__init__(CrimeSgmts({field:int(kwargs.get(field, 0)) for field in self.fields}))
    def __len__(self): return len(self.value)
    def __str__(self): return DELIMITER.join(['{}={}'.format(key, str(value)) for key, value in self.items() if value > 0])
    def __repr__(self): return '{}({})'.format(self.__class__.__name__, ', '.join(['{key}={value}'.format(key=key, value=value) for key, value in self.todict().items()]))
    
    def keys(self): return list(self.value.todict().keys())
    def values(self): return list(self.value.todict().values())
    def todict(self): return self.value._asdict()
    
    def __getitem__(self, key): return self.value.todict()[key]
    def __getattr__(self, attr): return getattr(self.value, attr)  

    @classmethod
    def fromstr(cls, crimestr, **kwargs):
        return cls({item.split('=')[0]:item.split('=')[1] for item in crimestr.split(DELIMITER)})







