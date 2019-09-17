# -*- coding: utf-8 -*-
"""
Created on Sun Jun 9 2019
@name:   Custom Variable Objects
@author: Jack Kirby Cook
"""

from numbers import Number
import numpy as np

from variables.variable import CustomVariable, VariableOverlapError, samevariable

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Category', 'Num', 'Range']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


@CustomVariable.register('category')
class Category: 
    @samevariable
    def __contains__(self, other): return all([item in self.values for item in other.values])
    
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
        if isinstance(other, Number): return self.factor(self.value * other, *args, factor=other, **kwargs)    
        else: return self.operation(other.__class__, *args, method='multiply', **kwargs)(self.value * other.value)
    
    def divide(self, other, *args, **kwargs): 
        if isinstance(other, Number): return self.factor(self.value / other, *args, factor=other, **kwargs)    
        else: return self.operation(other.__class__, *args, method='divide', **kwargs)(self.value / other.value) 

    # TRANSFORMATIONS
    def group(self, *args, groups, right=True, **kwargs):
        ranges = [[None, groups[0]], *[[groups[index], groups[index+1]] for index in range(len(groups)-1)], [groups[-1], None]]
        index = np.digitize([self.value], groups, right=right)[0]
        value = ranges[index]
        return self.unconsolidate(*args, how='group', **kwargs)(value)
    
    def uncumulate(self, *args, direction, **kwargs):
        assert direction == 'lower' or direction == 'upper'
        assert direction == self.numdirection
        value = [self.value if direction == 'upper' else None, self.value if direction == 'lower' else None]
        return self.unconsolidate(*args, how='uncumulate', direction=direction, axis=None, **kwargs)(value)
    
    def bracket(self, other, *args, **kwargs):
        assert isinstance(other, self.__class__)
        value = [min(self.value, other.value), max(self.value, other.value)]
        return self.moving(*args, how='bracket', axis=None, **kwargs)(value)
       
    @classmethod
    def unconsolidate(cls, *args, how, **kwargs): return cls.transformation(*args, method='unconsolidate', how=how, **kwargs)    
    @classmethod
    def moving(cls, *args, how, **kwargs): return cls.transformation(*args, method='moving', how=how, **kwargs)
    @classmethod
    def scale(cls, *args, how, **kwargs): return cls.transformation(*args, method='scale', how=how, **kwargs)
    @classmethod
    def factor(cls, *args, how, **kwargs): return cls.transformation(*args, method='factor', how=how, **kwargs)


@CustomVariable.register('range')
class Range:  
    @property
    def leftvalue(self): return self.value[0]
    @property
    def rightvalue(self): return self.value[-1]
    
    @samevariable
    def __contains__(self, other): return not other <= self and not other >= self
    def contains(self, other): return other in self
    
    @samevariable
    def overlaps(self, other): 
        try: left = other.rightvalue < self.leftvalue
        except TypeError: left = False
        try: right = other.leftvalue > self.rightvalue
        except TypeError: right = False
        return left or right
     
    @samevariable
    def __gt__(self, other):
        try: left = other.leftvalue < self.leftvalue
        except TypeError: left = other.leftvalue is None and self.leftvalue is not None
        try: right = other.rightvalue < self.rightvalue
        except TypeError: right = other.rightvalue is not None and self.rightvalue is None
        return left and right
        
    @samevariable
    def __lt__(self, other):
        try: left = other.leftvalue > self.leftvalue
        except TypeError: left = other.leftvalue is not None and self.leftvalue is None
        try: right = other.rightvalue > self.rightvalue
        except TypeError: right = other.rightvalue is None and self.rightvalue is not None
        return left and right

    @samevariable
    def __ge__(self, other): return other == self or other > self
    @samevariable
    def __le__(self, other): return other == self or other < self
    
    # OPERATIONS
    def add(self, other, *args, **kwargs):
        if all([self.leftvalue == other.rightvalue, self.leftvalue is not None, other.rightvalue is not None]): value = [other.leftvalue, self.rightvalue]
        elif all([self.rightvalue == other.leftvalue, self.rightvalue is not None, other.leftvalue is not None]): value = [self.leftvalue, other.rightvalue]
        else: raise VariableOverlapError(self, other, 'add')
        return self.operation(other.__class__, *args, method='add', **kwargs)(value)

    def subtract(self, other, *args, **kwargs):
        if all([self.value.count(None) == 0, None not in other.value]):
            if all([self.leftvalue == other.leftvalue, other.rightvalue < self.rightvalue]): value = [other.rightvalue, self.rightvalue]
            elif all([self.rightvalue == other.rightvalue, other.leftvalue > self.leftvalue]): value = [self.leftvalue, other.leftvalue]
            else: raise ValueError(self.value)            
        elif all([self.value.count(None) == 1, other.value.count(None) <= 1]):
            value = self.value.copy()
            value[value.index(None)] = [item for item in other.value if item is not None][0]
        elif all([self.value.count(None) == 2, other.value.count(None) == 1]):
            if other.leftvalue is None: value = [other.rightvalue, self.rightvalue]
            elif other.rightvalue is None: value = [self.leftvalue, other.leftvalue]
            else: raise ValueError(other.value)
        else: raise VariableOverlapError(self, other, 'subtract')
        return self.operation(other.__class__, *args, method='subtract', **kwargs)(value)

    def merge(self, other, *args, **kwargs):
        try: leftvalue = min([other.leftvalue, self.leftvalue])
        except TypeError: leftvalue = None
        try: rightvalue = max([other.rightvalue, self.rightvalue])
        except TypeError: rightvalue = None
        return self.operation(other.__class__, *args, method='merge', **kwargs)([leftvalue, rightvalue])

    def multiply(self, other, *args, **kwargs): 
        if isinstance(other, Number): return self.factor([val*other for val in self.value], *args, factor=other, **kwargs)    
        else: return self.operation(other.__class__, *args, method='multiply', **kwargs)([val * other.value for val in self.value])
    
    def divide(self, other, *args, **kwargs): 
        if isinstance(other, Number): return self.factor([val/other for val in self.value], *args, factor=other, **kwargs)       
        else: return self.operation(other.__class__, *args, method='divide', **kwargs)([val / other.value for val in self.value])

    # TRANSFORMATIONS
    def bound(self, *args, bounds, **kwargs):
        self.spec.checkval(bounds)
        assert None not in bounds
        value = [bound if val is None else val for val, bound in zip(self.value, bounds)]
        return self.transformation(*args, method='bound', **kwargs)(value)
       
    def split(self, cut, *args, **kwargs):
        assert isinstance(cut, Number)
        values = ([self.leftvalue, cut], [cut, self.rightvalue])
        return [self.transformation(*args, method='split', **kwargs)(value) for value in values]        
    
    def average(self, *args, weight=0.5, **kwargs):
        assert isinstance(weight, Number)
        assert all([weight <=1, weight >=0])
        value = weight * self.leftvalue + (1-weight) * self.rightvalue
        return self.consolidate(*args, how='average', weight=weight, axis=None, **kwargs)(value)
    
    def cumulate(self, *args, direction, **kwargs):
        assert direction == self.spec.direction(self.value)
        assert direction == 'lower' or direction == 'upper'
        value = getattr(self, {'upper':'leftvalue', 'lower':'rightvalue'}[direction])
        return self.consolidate(*args, how='cumulate', direction=direction, axis=None, **kwargs)(value)
    
    def differential(self, *args, **kwargs):
        value = self.rightvalue - self.leftvalue
        return self.consolidate(*args, how='differential', axis=None, **kwargs)(value)
    
    @classmethod
    def consolidate(cls, *args, how, **kwargs): return cls.transformation(*args, method='consolidate', how=how, **kwargs)
    @classmethod
    def factor(cls, *args, how, **kwargs): return cls.transformation(*args, method='factor', how=how, **kwargs)
    
    

    
    
    