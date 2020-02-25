# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 2020
@name:   Crime Object
@author: Jack Kirby Cook

"""

from variables.variable import Variable

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Crime']
__copyright__ = "Copyright 2020, Jack Kirby Cook"
__license__ = ""


_CRIME = ('shooting', 'arson', 'burglary', 'assault', 'vandalism', 'robbery', 'arrest', 'other', 'theft')


@Variable.register('crime')
class Crime:
    fields = _CRIME
    delimiter = '|'    
    
    def __init__(self, **kwargs): super().__init__({attr:int(kwargs.get(attr, 0)) for attr in self.fields})
    def __getattr__(self, attr): return self.value[attr]
    def __getitem__(self, attr): return self.value[attr]
    
    def __len__(self): return len(self.value)
    def __repr__(self): return '{}({})'.format(self.__class__.__name__,  ', '.join(['{}={}'.format(key, str(value)) for key, value in self.items()])) 
    def __str__(self): return self.delimiter.join(['{}={}'.format(key, str(value)) for key, value in self.items() if value > 0])
    
    def items(self): return zip(self.value.keys(), self.value.values())
    def asdict(self): return self.value
    
    @classmethod
    def fromstr(cls, crimestr, **kwargs):
        return cls({item.split('=')[0]:item.split('=')[1] for item in crimestr.split(cls.delimiter)})