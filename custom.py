# -*- coding: utf-8 -*-
"""
Created on Sun Jun 9 2019
@name:   Custom Variable Objects
@author: Jack Kirby Cook

"""

from variables.variable import CustomVariable, create_customvariable

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = []
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
class Num(CustomVariable):   
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
    def normalized(cls, *args, **kwargs): return create_customvariable(cls.spec.normalize(*args, **kwargs))
    @classmethod
    def standardized(cls, *args, **kwargs): return create_customvariable(cls.spec.standardize(*args, **kwargs))
    @classmethod
    def minmaxed(cls, *args, **kwargs): return create_customvariable(cls.spec.minmax(*args, **kwargs))


@CustomVariable.register('range')
class Range(CustomVariable):  
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
        return self.averaged(*args, weight=weight, **kwargs)(value)
    
    def cumulate(self, *args, **kwargs):
        direction = self.spec.direction(self.value)
        assert direction == 'lower' or direction == 'upper'
        value = [x for x in self.value if x is not None][0]
        return self.cumulated(*args, direction=direction, **kwargs)(value)
    
    @classmethod
    def averaged(cls, *args, **kwargs): return create_customvariable(cls.spec.average(*args, **kwargs))
    @classmethod
    def cumulated(cls, *args, **kwargs): return create_customvariable(cls.spec.cumulate(*args, **kwargs))

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    