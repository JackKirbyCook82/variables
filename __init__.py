# -*- coding: utf-8 -*-
"""
Created on Fri Jun 7 2019
@name:   Variable Objects
@author: Jack Kirby Cook

"""

import json
from collections import OrderedDict as ODict

from variables.variable import VARIABLES, CUSTOM_VARIABLES, create_customvariable 
from variables.custom import *
from variables.date import *
from variables.geography import *

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Variables']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


_aslist = lambda items: [items] if not isinstance(items, (tuple, list)) else list(items)  
_flatten = lambda nesteditems: [item for items in nesteditems for item in items]


class Variables(ODict):
    def __repr__(self): 
        if self.name: return "{}(name='{}')".format(self.__class__.__name__, self.name)
        else: return "{}()".format(self.__class__.__name__)  
        
    def __init__(self, items, name=None):
        if isinstance(items, list): pass
        elif isinstance(items, dict): items = [(key, value) for key, value in items.items()]
        else: raise TypeError(tuple([item.__name__ for item in items]))    
        assert all([isinstance(item, tuple) for item in items])
        assert all([len(item) == 2 for item in items])
        self.__name = name
        super().__init__(items)      

    @property
    def name(self): return self.__name
    def __str__(self): 
        namestr = self.__class__.__name__ if not self.__name else ' '.join([self.__name, self.__class__.__name__])
        content = {'{} ({})'.format(key, value.name()):json.loads(value.jsonstr()) for key, value in self.items()}
        jsonstr = json.dumps(content, sort_keys=False, indent=3, separators=(',', ' : '), default=str)                
        return ' '.join([namestr, jsonstr]) 
    
    def copy(self, name=None): return self.__class__([(key, value) for key, value in self.items()], name=name if name else self.__name)
    def select(self, keys, name=None): return self.__class__([(key, self[key]) for key in _aslist(keys)], name=name if name else self.__name)
    
    def update(self, items, name=None): 
        assert isinstance(items, dict)
        updated = [(key, items.get(key, value)) for key, value in self.items()]
        new = [(key, value) for key, value in items.items() if key not in self.keys()]
        return self.__class__(updated+new, name=name if name else self.__name)

    @classmethod
    def create(cls, name=None, **specs):
        custom_variables = [(key, create_customvariable(spec)) for key, spec in specs.items()]
        return cls(custom_variables, name=name)   
        
    @classmethod
    def load(cls, *variables, name=None):
        variables = [(variable, VARIABLES[variable]) for variable in variables]
        return cls(variables, name=name)   
    
    
    
    
    
    
    
    
    
    
    
    
    
    
