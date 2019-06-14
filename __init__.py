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

from variables.geography import Geography
from variables.date import Date, Datetime
from variables.custom import CustomVariable, create_customvariable, operation, transformation, VariableOverlapError, VariableOperationError

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Geography', 'Date', 'Datetime']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


VARIABLES = {'geography' : Geography, 'date' : Date, 'datetime' : Datetime}

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
        data = {key:{item:value for item, value in values.items() if not _allnull(_aslist(value))} for key, values in dataframe.transpose().to_dict().items() if not _allnull(_aslist(values))}
        specdata = {key:values for key, values in data.items() if values['datatype'] != 'variable'}
        specs = {key:Spec(**values) for key, values in specdata.items()}
        custom_variables = {key:create_customvariable(spec) for key, spec in specs.items()}
        variables = {key:VARIABLES[key] for key in data.keys() if key in VARIABLES.keys()}
        return cls(**custom_variables, **variables)
        
    def tofile(self, file, concatchar=';'):
        specdata = {key:value.spec.todict() for key, value in self.items() if key not in VARIABLES.keys()}
        variabledata = {key:{'datatype':'variable'} for key in self.keys() if key in VARIABLES.keys()}
        dataframe = pd.DataFrame({**specdata, **variabledata}).transpose()
        dataframe.index.name = _INDEXKEY
        dataframe = dfs.dataframe_parser(dataframe, default=lambda item: antiparser(item, concatchar))
        dataframe.reset_index(drop=False, inplace=True)
        dfs.dataframe_tofile(file, dataframe, index=False, header=True)


class Category(CustomVariable):
    variabletype = 'category'
    
    @operation('add')
    def add(self, other, *args, **kwargs): 
        if any([item in self.values for item in other.values]): raise VariableOverlapError(self, other, 'add')
        return {*self.value, *other.value} 
    @operation('subtract')
    def subtract(self, other, *args, **kwargs): 
        if any([item not in self.values for item in other.values]): raise VariableOverlapError(self, other, 'sub')
        return {value for value in self.values if value not in other.values}
    

class Num(CustomVariable):
    variabletype = 'num'
    
    @operation('add')
    def add(self, other, *args, **kwargs): return self.value + other.value    
    @operation('subtract')
    def subtract(self, other, *args, **kwargs): return self.value - other.value
    @operation('multiply')
    def multiply(self, other, *args, **kwargs): return self.value * other.value  
    @operation('divide')
    def divide(self, other, *args, **kwargs): return self.value / other.value

    
class Range(CustomVariable):  
    variabletype = 'range'    
    
    @property
    def lower(self): return self.value[0]
    @property
    def upper(self): return self.value[-1]
    
    @operation('add')
    def add(self, other, *args, **kwargs):
        if all([self.lower == other.upper, self.lower is not None, other.upper is not None]): value = [other.lower, self.upper]
        elif all([self.upper == other.lower, self.upper is not None, other.lower is not None]): value = [self.lower, other.upper]
        else: raise VariableOverlapError(self, other, 'add')
        return value

    @operation('subtract')
    def subtract(self, other, *args, **kwargs):
        if other.lower == other.upper: raise VariableOverlapError(self, other, 'sub')
        if self.lower == other.lower: 
            if other.upper is None: raise VariableOverlapError(self, other, 'sub')
            else: 
                if other.upper > self.upper: raise VariableOverlapError(self, other, 'sub')
                else: value = [other.upper, self.upper]
        elif self.upper == other.upper: 
            if other.lower is None: raise VariableOverlapError(self, other, 'sub')
            else: 
                if other.lower < self.lower: raise VariableOverlapError(self, other, 'sub')
                else: value = [self.lower, other.lower]
        else: raise VariableOverlapError(self, other, 'sub')
        return value

    @transformation('consolidate', 'average')
    def average(self, *args, wieght=0.5, **kwargs): 
        assert all([wieght >= 0, wieght <= 1]) 
        if self.spec.direction(self.value) != 'center' or self.spec.direction(self.value) != 'state': raise VariableOperationError(self, 'average')
        value = wieght * self.lower + (1-wieght) * self.upper
        return value

    @transformation('consolidate', 'cumulate')
    def cumulate(self, *args, **kwargs):
        if self.spec.direction(self.value) == 'lower': value = self.upper
        elif self.spec.direction(self.value) == 'upper': value = self.lower
        else: raise VariableOperationError(self, 'cumulative')
        return value






