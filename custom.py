# -*- coding: utf-8 -*-
"""
Created on Sun Jun 9 2019
@name:   Custom Variable Objects
@author: Jack Kirby Cook
"""

from numbers import Number

from utilities.dispatchers import keyword_singledispatcher as keydispatcher

from variables.variable import CustomVariable, VariableOverlapError, samevariable

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Category', 'Num', 'Range']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


def within_threshold(value, other, threshold):
    if value == other == None: return True
    elif None in (value, other): return False
    else: return abs(value - other) <= threshold


@CustomVariable.register('category')
class Category: 
    @samevariable
    def contains(self, other): return all([item in self.values for item in other.values])
    @samevariable
    def overlaps(self, other): return any([item in self.values for item in other.values])
    
    @samevariable
    def __contains__(self, other): return self.contains(other)
    def __iter__(self): 
        for item in self.value: yield item
    
    # OPERATIONS
    def add(self, other, *args, **kwargs): 
        if any([item in self.value for item in other.value]): raise VariableOverlapError(self, other, 'add')
        return self.operation(other.__class__, *args, method='add', **kwargs)({*self.value, *other.value}) 

    def subtract(self, other, *args, **kwargs): 
        if any([item not in self.values for item in other.values]): raise VariableOverlapError(self, other, 'sub')
        return self.operation(other.__class__, *args, method='subtract', **kwargs)({value for value in self.values if value not in other.values})

    def divide(self, other, *args, **kwargs): 
        if other.value != self.spec.categories: raise VariableOverlapError(self, other, 'divide')
        return self.operation(other.__class__, *args, method='divide', **kwargs)(self.value)   

    def couple(self, other, *args, **kwargs):   
        return self.operation(other.__class__, *args, method='couple', **kwargs)({*self.value, *other.value})   


@CustomVariable.register('num')
class Num:
    @keydispatcher('how')
    def unconsolidate(self, *args, how, **kwargs): raise KeyError(how)    
    
    # OPERATIONS
    def add(self, other, *args, **kwargs): return self.operation(other.__class__, *args, method='add', **kwargs)(self.value + other.value)   
    def subtract(self, other, *args, **kwargs): return self.operation(other.__class__, *args, method='subtract', **kwargs)(self.value - other.value)
    
    def multiply(self, other, *args, **kwargs): 
        if isinstance(other, Number): return self.transformation(*args, method='factor', how='multiply', factor=other, **kwargs)(self.value * other)    
        elif isinstance(other, Num): return self.operation(other.__class__, *args, method='multiply', **kwargs)(self.value * other.value)
        else: raise TypeError(type(other))
    
    def divide(self, other, *args, **kwargs): 
        if isinstance(other, Number): return self.transformation(*args, method='factor', how='divide', factor=other, **kwargs)(self.value / other)    
        elif isinstance(other, Num): return self.operation(other.__class__, *args, method='divide', **kwargs)(self.value / other.value) 
        else: raise TypeError(type(other))

    @unconsolidate.register('couple')
    def couple(self, other, *args, how='couple', **kwargs):
        assert how == 'couple'
        return self.operation(other.__class__, *args, method='unconsolidate', how=how, **kwargs)([min(self.value, other.value), max(self.value, other.value)])

    # TRANSFORMATIONS
    @unconsolidate.register('uncumulate')
    def uncumulate(self, *args, how='uncumulate', direction, **kwargs):
        assert how == 'uncumulate'
        assert direction == 'lower' or direction == 'upper'
        assert direction == self.numdirection
        value = [self.value if direction == 'upper' else None, self.value if direction == 'lower' else None]
        return self.transformation(*args, method='unconsolidate', how=how, direction=direction, **kwargs)(value)    


@CustomVariable.register('range')
class Range:  
    @property
    def leftvalue(self): return self.value[0]
    @property
    def rightvalue(self): return self.value[-1]
    
    @property
    def lower(self): return self.value[0]
    @property
    def upper(self): return self.value[-1]
    
    @samevariable
    def contains(self, other): 
        try: left = self.leftvalue <= other.leftvalue
        except: left = self.leftvalue is None
        try: right = self.rightvalue >= other.rightvalue
        except: right = self.rightvalue is None
        return left and right      
    
    @samevariable
    def overlaps(self, other):
        try: left = not self.leftvalue >= other.rightvalue
        except TypeError: left = any([self.leftvalue is None, other.rightvalue is None])
        try: right = not self.rightvalue <= other.leftvalue
        except TypeError: right = any([self.rightvalue is None, other.leftvalue is None])
        return left and right
    
    @samevariable
    def __lt__(self, other):
        try: left = self.leftvalue < other.leftvalue
        except TypeError: left = self.leftvalue is None and other.leftvalue is not None
        try: right = self.rightvalue < other.rightvalue
        except TypeError: right = self.rightvalue is not None and other.rightvalue is None
        return left and right    
    
    @samevariable
    def __gt__(self, other):
        try: left = self.leftvalue > other.leftvalue
        except TypeError: left = self.leftvalue is not None and other.leftvalue is None
        try: right = self.rightvalue > other.rightvalue
        except TypeError: right = self.rightvalue is None and other.rightvalue is not None
        return left and right
  
    @samevariable
    def __contains__(self, other): return self.contains(other)
    @samevariable
    def __le__(self, other): return self == other or self < other
    @samevariable
    def __ge__(self, other): return self == other or self > other
    
    @keydispatcher('how')
    def consolidate(self, *args, how, **kwargs): raise KeyError(how) 

    # OPERATIONS
    def add(self, other, *args, **kwargs):
        if all([within_threshold(self.leftvalue, other.rightvalue, self.spec.threshold), self.leftvalue is not None, other.rightvalue is not None]): value = [other.leftvalue, self.rightvalue]
        elif all([within_threshold(self.rightvalue, other.leftvalue, self.spec.threshold), self.rightvalue is not None, other.leftvalue is not None]): value = [self.leftvalue, other.rightvalue]
        else: raise VariableOverlapError(self, other, 'add')
        return self.operation(other.__class__, *args, method='add', **kwargs)(value)

    def subtract(self, other, *args, **kwargs):
        if all([self.value.count(None) == 0, None not in other.value]):
            if all([within_threshold(self.leftvalue, other.leftvalue, self.spec.threshold), other.rightvalue < self.rightvalue]): value = [other.rightvalue, self.rightvalue]
            elif all([within_threshold(self.rightvalue, other.rightvalue, self.spec.threshold), other.leftvalue > self.leftvalue]): value = [self.leftvalue, other.leftvalue]
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

    def multiply(self, other, *args, **kwargs): 
        if isinstance(other, Number): return self.transformation(*args, method='factor', how='multiply', factor=other, **kwargs)([val*other for val in self.value])    
        elif isinstance(other, Num): return self.operation(other, *args, method='multiply', **kwargs)([val*other.value for val in self.value])   
        elif isinstance(other, Range): return self.operation(other.__class__, *args, method='multiply', **kwargs)([val*other.value for val in self.value])
        else: TypeError(type(other))
    
    def divide(self, other, *args, **kwargs): 
        if isinstance(other, Number): return self.transformation(*args, method='factor', how='divide', factor=other, **kwargs)([val/other for val in self.value])    
        elif isinstance(other, Num): return self.operation(other, *args, method='divide', **kwargs)([val/other.value for val in self.value])   
        elif isinstance(other, Range): return self.operation(other.__class__, *args, method='divide', **kwargs)([val/other.value for val in self.value])
        else: TypeError(type(other))
        
    def couple(self, other, *args, **kwargs):
        assert isinstance(other, self.__class__)
        try: leftvalue = min([self.leftvalue, other.leftvalue])
        except TypeError: leftvalue = None
        try: rightvalue = max([self.rightvalue, other.rightvalue])
        except TypeError: rightvalue = None
        return self.operation(other.__class__, *args, method='couple', **kwargs)([leftvalue, rightvalue])     

    # TRANSFORMATIONS   
    @consolidate.register('average')
    def average(self, *args, how='average', weight=0.5, bounds=[None, None], **kwargs):
        assert how == 'average'
        assert isinstance(weight, Number)
        assert all([weight <=1, weight >=0])
        getvalue = lambda value, bound: value if value is not None else bound
        value = [getvalue(self.leftvalue, bounds[0]), getvalue(self.rightvalue, bounds[-1])]
        assert None not in value
        value = weight * value[0] + (1-weight) * value[-1]
        return self.transformation(*args, method='consolidate', how=how, weight=weight, **kwargs)(value)
    
    @consolidate.register('cumulate')
    def cumulate(self, *args, how='cumulate', direction, **kwargs):
        assert how == 'cumulate'
        assert direction == self.spec.direction(self.value)
        assert direction == 'lower' or direction == 'upper'
        value = getattr(self, {'upper':'leftvalue', 'lower':'rightvalue'}[direction])
        return self.transformation(*args, method='consolidate', how=how, direction=direction, **kwargs)(value)
    
    @consolidate.register('differential')
    def differential(self, *args, how='differential', bounds=[None, None], **kwargs):
        assert how == 'differential'
        getvalue = lambda value, bound: value if value is not None else bound
        value = [getvalue(self.leftvalue, bounds[0]), getvalue(self.rightvalue, bounds[-1])]
        return self.transformation(*args, method='consolidate', how=how, **kwargs)(value[-1] - value[0])    
    

    
    
    
    
    
    

    
    
    
    
    
    
    
    
    
    
    
    