# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 2020
@name:   Community Object
@author: Jack Kirby Cook

"""

from collections import namedtuple as ntuple

from variables.variable import Variable

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Community']
__copyright__ = "Copyright 2020, Jack Kirby Cook"
__license__ = ""


_aslist = lambda items: [items] if not isinstance(items, (list, tuple)) else list(items)
_filterempty = lambda items: [item for item in _aslist(items) if item is not None]


COMMUNITY = {}
DELIMITER = '|'
SEPARATOR = '&'
CommunitySgmts = ntuple('CommunitySgmts', ' '.join(list(COMMUNITY.keys())))


@Variable.register('community')    
class Community: 
    fields = tuple(COMMUNITY.keys())
        

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        