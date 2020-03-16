# -*- coding: utf-8 -*-
"""
Created on Sun Jun 9 2019
@name:   Custom Variable Objects
@author: Jack Kirby Cook
"""

import numpy as np
import scipy.stats as stats
from numbers import Number

from utilities.dispatchers import keyword_singledispatcher as keydispatcher

from variables.variable import CustomVariable, VariableOverlapError, samevariable

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Category', 'Histogram', 'Num', 'Range']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


def within_threshold(value, other, threshold):
    if value == other == None: return True
    elif None in (value, other): return False
    else: return abs(value - other) <= threshold


@CustomVariable.register('category')
class Category: 
    @samevariable
    def contains(self, other): return all([item in self.value for item in other.value])
    @samevariable
    def overlaps(self, other): return any([item in self.value for item in other.value])
    
    @samevariable
    def __contains__(self, other): return self.contains(other)
    def __hash__(self): return hash((self.__class__.__name__, self.value,))
    def __iter__(self): 
        for item in self.value: yield item

    # OPERATIONS & TRANSFORMATIONS
    def add(self, other, *args, **kwargs): 
        if any([item in self.value for item in other.value]): raise VariableOverlapError(self, other, 'add')
        value = {*self.value, *other.value}
        return self.operation(other.__class__, *args, method='add', **kwargs)(value) 
    def subtract(self, other, *args, **kwargs): 
        if any([item not in self.values for item in other.values]): raise VariableOverlapError(self, other, 'sub')
        value = {value for value in self.values if value not in other.values}
        return self.operation(other.__class__, *args, method='subtract', **kwargs)(value)

    def divide(self, other, *args, **kwargs): 
        if other.value != self.spec.categories: raise VariableOverlapError(self, other, 'divide')
        value = self.value
        return self.operation(other.__class__, *args, method='divide', **kwargs)(value)   

    def couple(self, other, *args, **kwargs):   
        value = {*self.value, *other.value}
        return self.operation(other.__class__, *args, method='couple', **kwargs)(value)   


@CustomVariable.register('histogram')
class Histogram:
    def __getitem__(self, category): return self.value[category]
    def __len__(self): return len(self.categories)  
    def __hash__(self): return hash((self.__class__.__name__, *self.value.values,))
    
    @property
    def categoryvector(self): return list(self.spec.category)
    @property
    def valuevector(self): return np.array(list(self.spec.index))
    @property
    def weightvector(self): return np.array([self.value[category] for category in self.spec.categories])   
    
    def array(self): return np.array([np.full(weight, value) for value, weight in zip(np.nditer(self.valuevector, np.nditer(self.weightvector)))]).flatten()
    def sample(self): return np.random.choice(self.valuevector, 1, p=self.weightvector)  
    def total(self): return np.sum(self.array)
    def mean(self): return np.mean(self.array)
    def median(self): return np.median(self.array)
    def stdev(self): return np.std(self.array)
    def rstdev(self): return self.std() / self.mean()
    def skew(self): return stats.skew(self.array)
    def kurtosis(self): return stats.kurtosis(self.array)
    
    def xmin(self): return np.minimum(self.valuevector)
    def xmax(self): return np.maximum(self.valuevector)
    def xdev(self, x): 
        if isinstance(x, Number): pass
        elif isinstance(x, str):
            if x in self.categories: x = self.categories.index(x) 
            else: raise ValueError(x)
        else: raise TypeError(type(x))        
        valuefunction = lambda value: pow(x - value, 2) / pow(self.xmax() - self.xmin(), 2)
        weightfunction = lambda weight: weight / self.total()
        return np.sum(np.array([valuefunction(value) * weightfunction(weight) for value, weight in zip(self.valuevector, self.weightvector)]))
    
    # OPERATIONS & TRANSFORMATIONS
    def add(self, other, *args, **kwargs): 
        value = {category:self.value[category] + other.value[category] for category in self.spec.categories} 
        return self.operation(other.__class__, *args, method='add', **kwargs)(value) 
    def subtract(self, other, *args, **kwargs): 
        value = {category:self.value[category] - other.value[category] for category in self.spec.categories} 
        return self.operation(other.__class__, *args, method='subtract', **kwargs)(value) 
    

@CustomVariable.register('num')
class Num:    
    def __hash__(self): return hash((self.__class__.__name__, self.value,))
    
    # OPERATIONS & TRANSFORMATIONS        
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

    @keydispatcher('how')
    def unconsolidate(self, *args, how, **kwargs): raise KeyError(how)    
    @unconsolidate.register('couple')
    def couple(self, other, *args, how='couple', **kwargs):
        assert how == 'couple'
        value = [min(self.value, other.value), max(self.value, other.value)]
        return self.operation(other.__class__, *args, method='unconsolidate', how=how, **kwargs)(value)
    @unconsolidate.register('uncumulate')
    def uncumulate(self, *args, how='uncumulate', direction, **kwargs):
        assert all([how == 'uncumulate', direction == 'lower' or direction == 'upper', direction == self.numdirection])
        value = [self.value if direction == 'upper' else None, self.value if direction == 'lower' else None]
        return self.transformation(*args, method='unconsolidate', how=how, direction=direction, **kwargs)(value)    


@CustomVariable.register('range')
class Range:  
    def __hash__(self): return hash((self.__class__.__name__, self.value[0], self.value[-1],))
    
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
    
    # OPERATIONS & TRANSFORMATIONS    
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

    @keydispatcher('how')
    def consolidate(self, *args, how, **kwargs): raise KeyError(how) 
    
    @consolidate.register('average')
    def average(self, *args, how='average', weight=0.5, bounds=[None, None], **kwargs):
        assert all([how == 'average', isinstance(weight, Number), weight<=1, weight>=0])
        getvalue = lambda value, bound: value if value is not None else bound
        value = [getvalue(self.leftvalue, bounds[0]), getvalue(self.rightvalue, bounds[-1])]
        assert None not in value
        value = weight * value[0] + (1-weight) * value[-1]
        return self.transformation(*args, method='consolidate', how=how, weight=weight, **kwargs)(value)
    
    @consolidate.register('cumulate')
    def cumulate(self, *args, how='cumulate', direction, **kwargs):
        assert all([how == 'cumulate', direction == self.spec.direction(self.value), direction == 'lower' or direction == 'upper'])
        value = getattr(self, {'upper':'leftvalue', 'lower':'rightvalue'}[direction])
        return self.transformation(*args, method='consolidate', how=how, direction=direction, **kwargs)(value)
    
    @consolidate.register('differential')
    def differential(self, *args, how='differential', bounds=[None, None], **kwargs):
        assert how == 'differential'
        getvalue = lambda value, bound: value if value is not None else bound
        value = [getvalue(self.leftvalue, bounds[0]), getvalue(self.rightvalue, bounds[-1])]
        return self.transformation(*args, method='consolidate', how=how, **kwargs)(value[-1] - value[0])    
    

    
    
    
    
    
    

    
    
    
    
    
    
    
    
    
    
    
    