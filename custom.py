# -*- coding: utf-8 -*-
"""
Created on Sun Jun 9 2019
@name:   Custom Variable Objects
@author: Jack Kirby Cook
"""

from numbers import Number
import numpy as np

from variables.variable import CustomVariable, samevariable

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
        return self.operation(other.__class__, *args, method='add', **kwargs)({*self.value, *other.value}) 

    def subtract(self, other, *args, **kwargs): 
        if any([item not in self.values for item in other.values]): raise VariableOverlapError(self, other, 'sub')
        return self.operation(other.__class__, *args, method='subtract', **kwargs)({value for value in self.values if value not in other.values})
        

@CustomVariable.register('num')
class Num:   
    # OPERATIONS
    def add(self, other, *args, **kwargs): return self.operation(other.__class__, *args, method='add', **kwargs)(self.value + other.value)   
    def subtract(self, other, *args, **kwargs): return self.operation(other.__class__, *args, method='subtract', **kwargs)(self.value - other.value)
    
    def multiply(self, other, *args, **kwargs): 
        if isinstance(other, Number): return self.__class__(self.value * other)    
        else: return self.operation(other.__class__, *args, method='multiply', **kwargs)(self.value * other.value)
    
    def divide(self, other, *args, **kwargs): 
        if isinstance(other, Number): return self.__class__(self.value * other)    
        else: return self.operation(other.__class__, *args, method='divide', **kwargs)(self.value / other.value) 

    # TRANSFORMATIONS
    def group(self, *args, groups, right=True, **kwargs):
        ranges = [[None, groups[0]], *[[groups[index], groups[index+1]] for index in range(len(groups)-1)], [groups[-1], None]]
        index = np.digitize([self.value], groups, right=right)[0]
        value = ranges[index]
        return self.unconsolidate(*args, method='group', **kwargs)(value)
    
    def cumulate(self, *args, direction, **kwargs):
        assert direction == 'lower' or direction == 'upper'
        value = self.value
        return self.transformation(*args, method='cumulate', direction=direction, **kwargs)(value)    
    
    @classmethod
    def scale(cls, *args, method, **kwargs): return cls.transformation(*args, method=method, **kwargs)
    @classmethod
    def unconsolidate(cls, *args, method, **kwargs): return cls.transformation(*args, method=method, **kwargs)
    

@CustomVariable.register('range')
class Range:  
    @property
    def leftvalue(self): return self.value[0]
    @property
    def rightvalue(self): return self.value[-1]
    
    @samevariable
    def __lt__(self, other): 
        try: return self.leftvalue < other.leftvalue
        except TypeError: return self.leftvalue is None and other.leftvalue is not None
    @samevariable
    def __gt__(self, other): 
        try: return self.rightvalue > other.rightvalue
        except TypeError: return self.rightvalue is None and other.rightvalue is not None
    
    # OPERATIONS
    def add(self, other, *args, **kwargs):
        if all([self.leftvalue == other.rightvalue, self.leftvalue is not None, other.rightvalue is not None]): value = [other.leftvalue, self.rightvalue]
        elif all([self.rightvalue == other.leftvalue, self.rightvalue is not None, other.leftvalue is not None]): value = [self.leftvalue, other.rightvalue]
        else: raise VariableOverlapError(self, other, 'add')
        return self.operation(other.__class__, *args, method='add', **kwargs)(value)

    def subtract(self, other, *args, **kwargs):
        if other.leftvalue == other.rightvalue: raise VariableOverlapError(self, other, 'sub')
        if self.leftvalue == other.leftvalue: 
            if other.rightvalue is None: raise VariableOverlapError(self, other, 'sub')
            else: 
                if other.rightvalue > self.rightvalue: raise VariableOverlapError(self, other, 'sub')
                else: value = [other.rightvalue, self.rightvalue]
        elif self.rightvalue == other.rightvalue: 
            if other.leftvalue is None: raise VariableOverlapError(self, other, 'sub')
            else: 
                if other.leftvalue < self.leftvalue: raise VariableOverlapError(self, other, 'sub')
                else: value = [self.leftvalue, other.leftvalue]
        else: raise VariableOverlapError(self, other, 'sub')
        return self.operation(other.__class__, *args, method='subtract', **kwargs)(value)

    def multiply(self, other, *args, **kwargs): 
        if isinstance(other, Number): return self.__class__(self.value * other)    
        else: return self.operation(other.__class__, *args, method='multiply', **kwargs)([val * other.value for val in self.value])
    
    def divide(self, other, *args, **kwargs): 
        if isinstance(other, Number): return self.__class__(self.value * other)    
        else: return self.operation(other.__class__, *args, method='divide', **kwargs)([val / other.value for val in self.value])

    # TRANSFORMATIONS
    def average(self, *args, weight=0.5, **kwargs):
        assert isinstance(weight, Number)
        assert all([weight <=1, weight >=0])
        value = weight * self.leftvalue + (1-weight) * self.rightvalue
        return self.consolidate(*args, weight=weight, method='average', **kwargs)(value)
    
    def cumulate(self, *args, direction, **kwargs):
        assert direction == 'lower' or direction == 'upper'
        value = getattr(self, {'upper':'leftvalue', 'lower':'rightvalue'}[direction])
        return self.consolidate(*args, method='cumulate', datatype='num',  direction=direction, numdirection=direction, **kwargs)(value)
    
    def boundary(self, *args, boundarys, **kwargs):
        self.spec.checkval(boundarys)
        assert None not in boundarys
        value = [bound if val is None else val for val, bound in zip(self.value, boundarys)]
        return self.__class__(value)
    
    @classmethod
    def consolidate(cls, *args, method, **kwargs): return cls.transformation(*args, method=method, **kwargs)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    