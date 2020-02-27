# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 2020
@name:   Proximity Object
@author: Jack Kirby Cook

"""

from collections import namedtuple as ntuple

from variables.variable import Variable

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Proximity']
__copyright__ = "Copyright 2020, Jack Kirby Cook"
__license__ = ""


_aslist = lambda items: [items] if not isinstance(items, (list, tuple)) else list(items)
_filterempty = lambda items: [item for item in _aslist(items) if item is not None]

PROXIMITY = ()
DELIMITER = '|'
ProximitySgmts = ntuple('ProximitySgmts', ' '.join(PROXIMITY))


@Variable.register('proximity')    
class Proximity: 
    fields = PROXIMITY
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    