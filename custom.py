# -*- coding: utf-8 -*-
"""
Created on Sun Jun 9 2019
@name:   Custom Variable Objects
@author: Jack Kirby Cook

"""

from variables.variable import CustomVariable

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
        return self.operation('add', other, *args, **kwargs)({*self.value, *other.value}) 

    def subtract(self, other, *args, **kwargs): 
        if any([item not in self.values for item in other.values]): raise VariableOverlapError(self, other, 'sub')
        return self.operation('subtract', other, *args, **kwargs)({value for value in self.values if value not in other.values})
        

@CustomVariable.register('num')
class Num(CustomVariable):
    # OPERATIONS
    def add(self, other, *args, **kwargs): return self.operation('add', other, *args, **kwargs)(self.value + other.value)   
    def subtract(self, other, *args, **kwargs): return self.operation('subtract', other, *args, **kwargs)(self.value - other.value)
    def multiply(self, other, *args, **kwargs): return self.operation('multiply', other, *args, **kwargs)(self.value * other.value  )
    def divide(self, other, *args, **kwargs): return self.operation('divide', other, *args, **kwargs)(self.value / other.value  )

    # TRANSFORMATIONS
    @classmethod
    def normalize(cls, *args, **kwargs): return cls.transformation('normalize', *args, **kwargs)
    @classmethod
    def standardize(cls, *args, **kwargs): return cls.transformation('standardize', *args, **kwargs)
    @classmethod
    def minmax(cls, *args, **kwargs): return cls.transformation('minmax', *args, **kwargs)
    @classmethod
    def scale(cls, method, *args, **kwargs): return cls.transformation(method, *args, **kwargs)


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
        return self.operation('add', other, *args, **kwargs)(value)

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
        return self.operation('subtract', other, *args, **kwargs)(value)

    # TRANSFORMATIONS
    @classmethod
    def average(cls, *args, **kwargs): return cls.transformation('average', *args, **kwargs)
    @classmethod
    def cumulate(cls, *args, **kwargs): return cls.transformation('cumulate', *args, **kwargs)
    @classmethod
    def consolidate(cls, method, *args, **kwargs): return cls.transformation(method, *args, **kwargs)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    