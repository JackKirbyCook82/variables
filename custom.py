# -*- coding: utf-8 -*-
"""
Created on Sun Jun 9 2019
@name:   Custom Variable Objects
@author: Jack Kirby Cook

"""

from variables.variable import CustomVariable, create_customvariable

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Category', 'Num', 'Range']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


class VariableOverlapError(Exception):
    def __init__(self, instance, other, operation): 
        super().__init__('{}.{}({})'.format(repr(instance), operation, repr(other))) 


@CustomVariable.register('category')
class Category: 
    # OPERATIONS
    def add(self, other, *args, **kwargs): 
        if any([item in self.values for item in other.values]): raise VariableOverlapError(self, other, 'add')
        return self.added(other.__class__, *args, **kwargs)({*self.value, *other.value}) 

    def subtract(self, other, *args, **kwargs): 
        if any([item not in self.values for item in other.values]): raise VariableOverlapError(self, other, 'sub')
        return self.subtracted(other.__class__, *args, **kwargs)({value for value in self.values if value not in other.values})
        

@CustomVariable.register('num')
class Num:   
    # OPERATIONS
    def add(self, other, *args, **kwargs): return self.added(other.__class__, other, *args, **kwargs)(self.value + other.value)   
    def subtract(self, other, *args, **kwargs): return self.subtracted(other.__class__, other, *args, **kwargs)(self.value - other.value)
    
    def multiply(self, other, *args, **kwargs): 
        if isinstance(other, (int, float)): return self.__class__(self.value * other)    
        else: return self.multiplied(other.__class__, other, *args, **kwargs)(self.value * other.value  )
    
    def divide(self, other, *args, **kwargs): 
        if isinstance(other, (int, float)): return self.__class__(self.value * other)    
        else: return self.divided(other.__class__, other, *args, **kwargs)(self.value / other.value  )

    # TRANSFORMATIONS
    @classmethod
    def scale(cls, *args, method, **kwargs): return create_customvariable(getattr(cls.spec, method)(*args, **kwargs))


@CustomVariable.register('range')
class Range:  
    @property
    def lower(self): return self.value[0]
    @property
    def upper(self): return self.value[-1]
    
    # OPERATIONS
    def add(self, other, *args, **kwargs):
        if all([self.lower == other.upper, self.lower is not None, other.upper is not None]): value = [other.lower, self.upper]
        elif all([self.upper == other.lower, self.upper is not None, other.lower is not None]): value = [self.lower, other.upper]
        else: raise VariableOverlapError(self, other, 'add')
        return self.added(other.__class__, other, *args, **kwargs)(value)

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
        return self.subtracted(other.__class__, other, *args, **kwargs)(value)

    # TRANSFORMATIONS
    def average(self, *args, weight=0.5, **kwargs):
        assert isinstance(weight, (float, int))
        assert all([weight <=1, weight >=0])
        value = weight * self.lower + (1-weight) * self.upper
        return self.consolidate(*args, weight=weight, method='average', **kwargs)(value)
    
    def cumulate(self, *args, direction, **kwargs):
        assert direction == self.spec.direction(self.value)
        assert direction == 'lower' or direction == 'upper'
        value = [x for x in self.value if x is not None][0]
        return self.consolidate(*args, direction=direction, method='cumulate', **kwargs)(value)
    
    @classmethod
    def consolidate(cls, *args, method, **kwargs): return create_customvariable(getattr(cls.spec, method)(*args, **kwargs))
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    