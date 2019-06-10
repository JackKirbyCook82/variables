# -*- coding: utf-8 -*-
"""
Created on Fri Jun 7 2019
@name:   Variable Objects
@author: Jack Kirby Cook

"""

from variables.geography import Geography
from variables.date import Date, Datetime
from variables.custom import CustomVariable, VariableOverlapError, VariableOperationError, create_customvariable

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Geography', 'Date', 'Datetime', 'create_customvariable']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


class Category(CustomVariable):
    variabletype = 'category'
    
    def add(self, other, *args, **kwargs): 
        cls = create_customvariable(self.spec.add(other.spec, *args, **kwargs))
        if any([item in self.values for item in other.values]): raise VariableOverlapError(self, other, 'add')
        return cls({*self.value, *other.value})  

    def subtract(self, other, *args, **kwargs): 
        cls = create_customvariable(self.spec.subtract(other.spec, *args, **kwargs))
        if any([item not in self.values for item in other.values]): raise VariableOverlapError(self, other, 'sub')
        return cls({value for value in self.values if value not in other.values}) 
    

class Num(CustomVariable):
    variabletype = 'num'
    
    def add(self, other, *args, **kwargs): 
        cls = create_customvariable(self.spec.add(other.spec, *args, **kwargs))
        return cls(self.value + other.value)   
        
    def subtract(self, other, *args, **kwargs): 
        cls = create_customvariable(self.spec.subtract(other.spec, *args, **kwargs))
        return cls(self.value - other.value)

    def multiply(self, other, *args, **kwargs): 
        cls = create_customvariable(self.spec.multiply(other.spec, *args, **kwargs))
        return cls(self.value * other.value)   
        
    def divide(self, other, *args, **kwargs): 
        cls = create_customvariable(self.spec.divide(other.spec, *args, **kwargs))
        return cls(self.value / other.value)    
    
    
class Range(CustomVariable):  
    variabletype = 'range'    
    
    @property
    def lower(self): return self.value[0]
    @property
    def upper(self): return self.value[-1]
    
    def add(self, other, *args, **kwargs):
        cls = create_customvariable(self.spec.add(other.spec, *args, **kwargs))
        if all([self.lower == other.upper, self.lower is not None, other.upper is not None]): value = [other.lower, self.upper]
        elif all([self.upper == other.lower, self.upper is not None, other.lower is not None]): value = [self.lower, other.upper]
        else: raise VariableOverlapError(self, other, 'add')
        return cls(value)

    def subtract(self, other, *args, **kwargs):
        cls = create_customvariable(self.spec.subtract(other.spec, *args, **kwargs))
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
        return cls(value)

    def average(self, *args, wieght=0.5, **kwargs): 
        cls = create_customvariable(self.spec.consolidate('average', *args, **kwargs))
        assert all([wieght >= 0, wieght <= 1]) 
        if self.spec.direction(self.value) != 'center' or self.spec.direction(self.value) != 'state': raise VariableOperationError(self, 'average')
        value = wieght * self.lower + (1-wieght) * self.upper
        return cls(value)

    def cumulate(self, *args, **kwargs):
        cls = create_customvariable(self.spec.consolidate('cumulate', *args, **kwargs))
        if self.spec.direction(self.value) == 'lower': value = self.upper
        elif self.spec.direction(self.value) == 'upper': value = self.lower
        else: raise VariableOperationError(self, 'cumulative')
        return cls(value)






