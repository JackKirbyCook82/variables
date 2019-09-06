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
    def __init__(self, *args, **kwargs):
        argskwargs = [{key:value for key, value in arg.items()} for arg in args]
        for argkwargs in argskwargs: kwargs.update(argkwargs)
        super().__init__(**kwargs)        

    def copy(self): return self.__class__(super().copy())
    
    @classmethod
    def create(cls, **specs):
        custom_variables = {key:create_customvariable(spec) for key, spec in specs.items()}
        variables = {key:value for key, value in Variable.subclasses().items()}
        return cls(**variables, **custom_variables)  
    
    def __str__(self): 
        content = {}
        for key, value in self.items():
            try: content[value.name()] = {k:str(v) for k, v in value.spec.todict().items()}
            except: content[value.name()] = {}
        return ' '.join([self.__class__.__name__, json.dumps(content, sort_keys=True, indent=3, separators=(',', ' : '))])  
