# -*- coding: utf-8 -*-
"""
Created on Fri Jun 7 2019
@name:   Variable Objects
@author: Jack Kirby Cook

"""

from specs import specs_fromfile, specs_tofile

from variables.geography import Geography
from variables.date import Date, Datetime
from variables.custom import CustomVariable, create_customvariable, operation, transformation, VariableOverlapError, VariableOperationError

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Geography', 'Date', 'Datetime']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


VARIABLES = {'geography' : Geography, 'date' : Date, 'datetime' : Datetime}


class Variables(dict):
    def __init__(self, **kwargs): super().__init__(**VARIABLES, **kwargs)
       
    @classmethod
    def fromfile(cls, file, splitchar=';'):
        specs = specs_fromfile(file, splitchar=splitchar)
        return cls(**{key:create_customvariable(value) for key, value in specs.items()})
    
    def tofile(self, file, concatchar=';'):
        specs = {key:value.spec for key, value in self.items() if key not in VARIABLES.keys()}
        specs = specs_tofile(file, specs, concatchar=concatchar)


class Category(CustomVariable):
    variabletype = 'category'
    
    @operation
    def add(self, other, *args, **kwargs): 
        if any([item in self.values for item in other.values]): raise VariableOverlapError(self, other, 'add')
        return {*self.value, *other.value} 
    @operation
    def subtract(self, other, *args, **kwargs): 
        if any([item not in self.values for item in other.values]): raise VariableOverlapError(self, other, 'sub')
        return {value for value in self.values if value not in other.values}
    

class Num(CustomVariable):
    variabletype = 'num'
    
    @operation
    def add(self, other, *args, **kwargs): return self.value + other.value    
    @operation
    def subtract(self, other, *args, **kwargs): return self.value - other.value
    @operation
    def multiply(self, other, *args, **kwargs): return self.value * other.value  
    @operation
    def divide(self, other, *args, **kwargs): return self.value / other.value

    
class Range(CustomVariable):  
    variabletype = 'range'    
    
    @property
    def lower(self): return self.value[0]
    @property
    def upper(self): return self.value[-1]
    
    @operation
    def add(self, other, *args, **kwargs):
        if all([self.lower == other.upper, self.lower is not None, other.upper is not None]): value = [other.lower, self.upper]
        elif all([self.upper == other.lower, self.upper is not None, other.lower is not None]): value = [self.lower, other.upper]
        else: raise VariableOverlapError(self, other, 'add')
        return value

    @operation
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

    @transformation
    def consolidate(self, method, value, *args, **kwargs): return value

    def average(self, *args, wieght=0.5, **kwargs): 
        assert all([wieght >= 0, wieght <= 1]) 
        if self.spec.direction(self.value) != 'center' or self.spec.direction(self.value) != 'state': raise VariableOperationError(self, 'average')
        value = wieght * self.lower + (1-wieght) * self.upper
        return self.consolidate('average', value, *args, wieght=wieght, **kwargs)

    def cumulate(self, *args, **kwargs):
        if self.spec.direction(self.value) == 'lower': value = self.upper
        elif self.spec.direction(self.value) == 'upper': value = self.lower
        else: raise VariableOperationError(self, 'cumulative')
        return self.consolidate('cumulate', value, *args, direction=self.spec.direction, **kwargs)






