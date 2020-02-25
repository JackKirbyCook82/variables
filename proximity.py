# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 2020
@name:   Proximity Object
@author: Jack Kirby Cook

"""

from variables.variable import Variable

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Proximity']
__copyright__ = "Copyright 2020, Jack Kirby Cook"
__license__ = ""


_aslist = lambda items: [items] if not isinstance(items, (list, tuple)) else list(items)
_filterempty = lambda items: [item for item in _aslist(items) if item is not None]


_PROXIMITY = ()


@Variable.register('quality')
class Proximity:
    fields = _PROXIMITY
    
    def __init__(self, **kwargs): pass ### WORKING ###
    def __getattr__(self, attr): pass ### WORKING ###
    def __getitem__(self, attr): pass ### WORKING ###
    
    def __len__(self): pass ### WORKING ###
    def __repr__(self): pass ### WORKING ###
    def __str__(self): pass ### WORKING ###
    
    def items(self): pass ### WORKING ###
    def asdict(self): pass ### WORKING ###
    
    @classmethod
    def fromstr(cls, communitystr, **kwargs): pass ### WORKING ###


        