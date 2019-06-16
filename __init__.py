# -*- coding: utf-8 -*-
"""
Created on Fri Jun 7 2019
@name:   Variable Objects
@author: Jack Kirby Cook

"""

import os.path
import pandas as pd

import utilities.dataframes as dfs
from specs import Spec

from variables.variable import create_customvariable, Variable, CustomVariable
from variables.custom import *
from variables.date import *
from variables.geography import *

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Variables']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


_INDEXKEY = 'key'

_aslist = lambda items: [items] if not isinstance(items, (list, tuple)) else list(items)
_allnull = lambda items: all([pd.isnull(item) for item in items])

def parser(item, splitby): 
    if _allnull(_aslist(item)): return ''
    else: return item.split(splitby) if splitby in item else str(item)
    
def antiparser(item, concatby): 
    if _allnull(_aslist(item)): return ''
    else: return concatby.join([str(i) for i in item]) if isinstance(item, (set, tuple, list)) else str(item)


class Variables(dict):
    @classmethod
    def fromfile(cls, file, splitchar=';'):
        if not os.path.isfile(file): raise FileNotFoundError(file)
        dataframe = dfs.dataframe_fromfile(file)
        dataframe = dfs.dataframe_parser(dataframe, default=lambda item: parser(item, splitchar))
        dataframe.set_index(_INDEXKEY, drop=True, inplace=True)
        specdata = {key:{item:value for item, value in values.items() if not _allnull(_aslist(value))} for key, values in dataframe.transpose().to_dict().items() if not _allnull(_aslist(values))}
        specs = {key:Spec(**values) for key, values in specdata.items()}
        custom_variables = {key:create_customvariable(spec) for key, spec in specs.items()}
        variables = {key:value for key, value in Variable.subclasses().items()}
        return cls(**custom_variables, **variables)
        
    def tofile(self, file, concatchar=';'):
        specdata = {key:value.spec.todict() for key, value in self.items() if key not in Variable.subclasses().keys()}
        dataframe = pd.DataFrame(specdata).transpose()
        dataframe.index.name = _INDEXKEY
        dataframe = dfs.dataframe_parser(dataframe, default=lambda item: antiparser(item, concatchar))
        dataframe.reset_index(drop=False, inplace=True)
        dfs.dataframe_tofile(file, dataframe, index=False, header=True)
        
    @property
    def variable_registry(self): return Variable.subclasses()
    @property
    def customvariable_registry(self): return CustomVariable.subclasses()
    @property
    def customvariable_createdregistry(self): return CustomVariable.custom_subclasses()
            
            
        
        
        
        
        
        
        
        
        
        
        
        
        
        