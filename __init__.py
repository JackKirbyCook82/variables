# -*- coding: utf-8 -*-
"""
Created on Fri Jun 7 2019
@name:   Variable Objects
@author: Jack Kirby Cook

"""

import json
from collections import OrderedDict as ODict

from variables.variable import Variable, CustomVariable, create_customvariable 
from variables.date import Date, Datetime
from variables.geography import Geography
from variables.custom import *

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Variables', 'Geography', 'Date', 'Datetime']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


_aslist = lambda items: [items] if not isinstance(items, (tuple, list)) else list(items)  
_flatten = lambda nesteditems: [item for items in nesteditems for item in items]


class Variables(ODict):
    def __init__(self, items, name=None):
        if isinstance(items, list): pass
        elif isinstance(items, dict): items = [(key, value) for key, value in items.items()]
        else: raise TypeError(items)    
        assert all([isinstance(item, tuple) for item in items])
        assert all([len(item) == 2 for item in items])
        self.__name = name
        super().__init__(items)      

    @property
    def name(self): return self.__name
    def __str__(self): 
        namestr = self.__class__.__name__ if not self.__name else ' '.join([self.__name, self.__class__.__name__])
        content = {}
        for key, value in self.items():
            try: content[value.name()] = {k:str(v) for k, v in value.spec.todict().items()}
            except: content[value.name()] = {}
        jsonstr = json.dumps(content, sort_keys=True, indent=3, separators=(',', ' : '))                
        return ' '.join([namestr, jsonstr]) 
    
    def copy(self): return self.__class__([(key, value) for key, value in self.items()], name=self.__name)
    def select(self, keys): 
        assert isinstance(keys, list)
        return self.__class__([(key, self[key]) for key in keys], name=self.__name)
    def update(self, items): 
        assert isinstance(items, list)
        assert all([isinstance(item, tuple) for item in items])
        assert all([len(item) == 2 for item in items])
        items = ODict(items)
        updated = [(key, items.get(key, value)) for key, value in self.items()]
        new = [(key, value) for key, value in items.items() if key not in self.keys()]
        return self.__class__(updated + new, name=self.__name)

    @classmethod
    def create(cls, name=None, **specs):
        custom_variables = [(key, create_customvariable(spec)) for key, spec in specs.items()]
        variables = [(key, value) for key, value in Variable.subclasses().items()]
        return cls(variables + custom_variables, name=name)   
    
    
    
    
    
    
    
    
    
    
    
    
    
    
