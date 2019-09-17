# -*- coding: utf-8 -*-
"""
Created on Fri Jun 7 2019
@name:   Variable Objects
@author: Jack Kirby Cook

"""

import json

from variables.variable import Variable, CustomVariable, create_customvariable 
from variables.date import Date, Datetime
from variables.geography import Geography
from variables.custom import *

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Variables', 'Geography', 'Date', 'Datetime']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


class Variables(dict):
    def __init__(self, *args, name, **kwargs):
        self.__name = name
        argskwargs = [{key:value for key, value in arg.items()} for arg in args]
        for argkwargs in argskwargs: kwargs.update(argkwargs)
        super().__init__(**kwargs)        

    @property
    def name(self): return self.__class__.__name__ if not self.__name else '_'.join([self.__name, self.__class__.__name__])
    @property
    def jsonstr(self): 
        content = {}
        for key, value in self.items():
            try: content[value.name()] = {k:str(v) for k, v in value.spec.todict().items()}
            except: content[value.name()] = {}
        return json.dumps(content, sort_keys=True, indent=3, separators=(',', ' : '))

    def __str__(self): return ' '.join([self.name, self.jsonstr]) 
    def copy(self): return self.__class__(super().copy(), name=self.__name)
    def select(self, *keys): return self.__class__({key:value for key, value in self.items() if key in keys}, name=self.__name)
    def update(self, **kwargs): 
        asdict = {key:value for key, value in self.items()}
        asdict.update(kwargs)
        return self.__class__(asdict, name=self.__name)
    
    @classmethod
    def create(cls, name=None, **specs):
        custom_variables = {key:create_customvariable(spec) for key, spec in specs.items()}
        variables = {key:value for key, value in Variable.subclasses().items()}
        return cls(**variables, **custom_variables,name=name)   
