# -*- coding: utf-8 -*-
"""
Created on Sun Jun 9 2019
@name:   Custom Variable Objects
@author: Jack Kirby Cook

"""

from variables.variable import CustomVariable, custom_operation, custom_transformation

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = []
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


class VariableOverlapError(Exception):
    def __init__(self, instance, other, operation): 
        super().__init__('{}.{}({})'.format(repr(instance), operation, repr(other)))

class VariableOperationError(Exception):
    def __init__(self, instance, operation):
        super().__init__('{}.{}()'.format(repr(instance), operation))    


@CustomVariable.register('category')
class Category:
    @custom_operation('add')
    def add(self, other, *args, **kwargs): 
        if any([item in self.values for item in other.values]): raise VariableOverlapError(self, other, 'add')
        return {*self.value, *other.value} 
    @custom_operation('subtract')
    def subtract(self, other, *args, **kwargs): 
        if any([item not in self.values for item in other.values]): raise VariableOverlapError(self, other, 'sub')
        return {value for value in self.values if value not in other.values}
    

@CustomVariable.register('num')
class Num(CustomVariable):
    @custom_operation('add')
    def add(self, other, *args, **kwargs): return self.value + other.value    
    @custom_operation('subtract')
    def subtract(self, other, *args, **kwargs): return self.value - other.value
    @custom_operation('multiply')
    def multiply(self, other, *args, **kwargs): return self.value * other.value  
    @custom_operation('divide')
    def divide(self, other, *args, **kwargs): return self.value / other.value

    
@CustomVariable.register('range')
class Range(CustomVariable):  
    @property
    def lower(self): return self.value[0]
    @property
    def upper(self): return self.value[-1]
    
    @custom_operation('add')
    def add(self, other, *args, **kwargs):
        if all([self.lower == other.upper, self.lower is not None, other.upper is not None]): value = [other.lower, self.upper]
        elif all([self.upper == other.lower, self.upper is not None, other.lower is not None]): value = [self.lower, other.upper]
        else: raise VariableOverlapError(self, other, 'add')
        return value

    @custom_operation('subtract')
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

    @custom_transformation('consolidate', 'average')
    def average(self, *args, wieght=0.5, **kwargs): 
        assert all([wieght >= 0, wieght <= 1]) 
        if self.spec.direction(self.value) != 'center' or self.spec.direction(self.value) != 'state': raise VariableOperationError(self, 'average')
        value = wieght * self.lower + (1-wieght) * self.upper
        return value

    @custom_transformation('consolidate', 'cumulate')
    def cumulate(self, *args, **kwargs):
        if self.spec.direction(self.value) == 'lower': value = self.upper
        elif self.spec.direction(self.value) == 'upper': value = self.lower
        else: raise VariableOperationError(self, 'cumulative')
        return value



    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    