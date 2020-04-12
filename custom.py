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


_aslist = lambda items: [items] if not isinstance(items, (list, tuple)) else list(items)


@CustomVariable.register('category')
class Category: 
    def checkvalue(self, value): 
        if not isinstance(value, tuple): raise ValueError(value)
        if not all([isinstance(item, str) for item in value]): raise ValueError(value)
        if not all([item in self.spec.categories for item in value]): raise ValueError(value)          
    def fixvalue(self, value): return value
    
    @samevariable
    def contains(self, other): return all([item in self.value for item in other.value])
    @samevariable
    def overlaps(self, other): return any([item in self.value for item in other.value])
    
    @samevariable
    def __contains__(self, other): return self.contains(other)
    def __hash__(self): return hash((self.__class__.__name__, *self.value,))
    def __iter__(self): 
        for item in self.value: yield item

    # OPERATIONS & TRANSFORMATIONS
    def expand(self, *args, how=None, **kwargs):
        cls = self.transformation(*args, method='expand', how=how, **kwargs)
        return [cls((item,)) for item in self.value] 

    def add(self, other, *args, **kwargs): 
        if any([item in self.value for item in other.value]): raise VariableOverlapError(self, other, 'add')
        value = (*self.value, *other.value)
        return self.operation(other.__class__, *args, method='add', **kwargs)(value) 
    def subtract(self, other, *args, **kwargs): 
        if any([item not in self.values for item in other.values]): raise VariableOverlapError(self, other, 'sub')
        value = tuple([value for value in self.values if value not in other.values])
        return self.operation(other.__class__, *args, method='subtract', **kwargs)(value)

    def divide(self, other, *args, **kwargs): 
        if other.value != self.spec.categories: raise VariableOverlapError(self, other, 'divide')
        value = self.value
        return self.operation(other.__class__, *args, method='divide', **kwargs)(value)   

    def couple(self, other, *args, **kwargs):   
        value = (*self.value, *other.value)
        return self.operation(other.__class__, *args, method='couple', **kwargs)(value)   


@CustomVariable.register('histogram')
class Histogram:
    def checkvalue(self, value): 
        if not isinstance(value, dict): raise ValueError(value)
        if not all([isinstance(key, str) for key in value.keys()]): raise ValueError(value)
        if not all([key in self.spec.categories and isinstance(weight, int) for key, weight in value]): raise ValueError(value)    
    def fixvalue(self, value): return value
    
    def __getitem__(self, category): return self.value[category]
    def __len__(self): return len(self.categories)  
    def __hash__(self): return hash((self.__class__.__name__, *self.value.values,))
    
    @property
    def categoryvector(self): return list(self.spec.category)
    @property
    def indexvector(self): return np.array(list(self.spec.index))
    @property
    def weightvector(self): return np.array([self.value[category] for category in self.spec.categories])   
    
    def array(self): return np.array([np.full(weight, value) for value, weight in zip(np.nditer(self.indexvector, np.nditer(self.weightvector)))]).flatten()
    def sample(self): return np.random.choice(self.indexvector, 1, p=self.weightvector)  
    def total(self): return np.sum(self.array)
    def mean(self): return np.mean(self.array)
    def median(self): return np.median(self.array)
    def stdev(self): return np.std(self.array)
    def rstdev(self): return self.std() / self.mean()
    def skew(self): return stats.skew(self.array)
    def kurtosis(self): return stats.kurtosis(self.array)
    
    def xmin(self): return np.minimum(self.indexvector)
    def xmax(self): return np.maximum(self.indexvector)
    def xdev(self, x): 
        if isinstance(x, Number): pass
        elif isinstance(x, str):
            if x in self.categories: x = self.categories.index(x) 
            else: raise ValueError(x)
        else: raise TypeError(type(x))        
        indexfunction = lambda i: pow(x - i, 2) / pow(self.xmax() - self.xmin(), 2)
        weightfunction = lambda weight: weight / self.total()
        return np.sum(np.array([indexfunction(index) * weightfunction(weight) for index, weight in zip(self.indexvector, self.weightvector)]))
    
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

    def checkvalue(self, value): 
        if not isinstance(value, Number): raise ValueError(value)
    def fixvalue(self, value):
         if isinstance(value, str): return (float(value) if '.' in value else int(value)) * (-1 if '-' in value else 1)
         else: return value
        
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

    def couple(self, other, *args, how=None, **kwargs):
        value = [min(self.value, *_aslist(other.value)), max(self.value, *_aslist(other.value))]
        return self.operation(other.__class__, *args, method='couple', how=how, **kwargs)(value)

    @keydispatcher('how')
    def unconsolidate(self, *args, how, **kwargs): raise KeyError(how)   
    @unconsolidate.register('cumulate')
    def cumulate(self, *args, how='cumulate', direction, **kwargs):
        assert all([how == 'cumulate', direction == 'lower' or direction == 'upper'])
        value = (self.value if direction == 'upper' else None, self.value if direction == 'lower' else None)
        return self.transformation(*args, method='unconsolidate', how=how, direction=direction, **kwargs)(value)    


@CustomVariable.register('range')
class Range:  
    def __hash__(self): return hash((self.__class__.__name__, self.value[0], self.value[-1],))
    
    def checkvalue(self, value): 
        if not isinstance(value, tuple): raise ValueError(value)
        if not len(value) == 2: raise ValueError(value)
        if not all([isinstance(item, (Number, type(None))) for item in value]): raise ValueError(value)
    def fixvalue(self, value):
         if isinstance(value, Number): return (value, value)
         else: return value
       
    @property
    def leftvalue(self): return self.value[0]
    @property
    def rightvalue(self): return self.value[-1]
    
    @property
    def lower(self): return self.value[0]
    @property
    def upper(self): return self.value[-1]
    
    def contains(self, other): 
        if isinstance(other, Num):
            try: left = other.value >= self.leftvalue
            except: left = self.leftvalue is None
            try: right = other.value <= self.rightvalue
            except: right = self.rightvalue is None
        elif isinstance(other, Range):            
            try: left = self.leftvalue <= other.leftvalue
            except: left = self.leftvalue is None
            try: right = self.rightvalue >= other.rightvalue
            except: right = self.rightvalue is None      
        else: raise TypeError(type(other))
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
        if self < other: 
            if self.upper is None or other.lower is None: raise VariableOverlapError(self, other, 'add')
            if abs(self.upper - other.lower) > self.spec.threshold: raise VariableOverlapError(self, other, 'add')
            value = (self.leftvalue, other.rightvalue)
        elif self > other: 
            if self.lower is None or other.upper is None: raise VariableOverlapError(self, other, 'add')
            if abs(self.lower - other.upper) > self.spec.threshold: raise VariableOverlapError(self, other, 'add')                        
            value = (other.leftvalue, self.rightvalue)
        else: raise VariableOverlapError(self, other, 'add')
        return self.operation(other.__class__, *args, method='add', **kwargs)(value)
    
    def subtract(self, other, *args, **kwargs):
        if not self.contains(other): raise VariableOverlapError(self, other, 'subtract')        
        if (abs(self.lower - other.lower) <= self.spec.threshold if (self.lower is not None and other.lower is not None) else False) or self.lower == other.lower == None: 
            value = (other.upper + self.spec.threshold, self.upper)
        elif (abs(self.upper - other.upper) <= self.spec.threshold if (self.upper is not None and other.upper is not None) else False) or self.upper == other.upper == None: 
            value = (self.lower, other.lower - self.spec.threshold)
        return self.operation(other.__class__, *args, method='subtract', **kwargs)(value)

    def multiply(self, other, *args, **kwargs): 
        if isinstance(other, Number): return self.transformation(*args, method='factor', how='multiply', factor=other, **kwargs)(tuple([val*other for val in self.value])) 
        elif isinstance(other, Num): return self.operation(other, *args, method='multiply', **kwargs)(tuple([val*other.value for val in self.value]))   
        elif isinstance(other, Range): return self.operation(other.__class__, *args, method='multiply', **kwargs)(tuple([val*other.value for val in self.value]))
        else: TypeError(type(other))
    
    def divide(self, other, *args, **kwargs): 
        if isinstance(other, Number): return self.transformation(*args, method='factor', how='divide', factor=other, **kwargs)(tuple([val/other for val in self.value])) 
        elif isinstance(other, Num): return self.operation(other, *args, method='divide', **kwargs)(tuple([val/other.value for val in self.value]))   
        elif isinstance(other, Range): return self.operation(other.__class__, *args, method='divide', **kwargs)(tuple([val/other.value for val in self.value]))
        else: TypeError(type(other))
        
    def couple(self, other, *args, how=None, **kwargs):
        value = (min(*_aslist(self.value), *_aslist(other.value)), max(*_aslist(self.value), *_aslist(other.value)))
        return self.operation(other.__class__, *args, method='couple', how=how, **kwargs)(value)     

    def split(self, value, *args, how=None, **kwargs):
        value = round(value, self.spec.threshold)
        if value >= self.upper or value <= self.lower: return self       
        lowervalues, uppervalues = (self.lower, value), (value + self.spec.threshold, self.upper)
        return self.transformation(*args, method='split', how=how, **kwargs)(lowervalues), self.transformation(*args, method='split', how=how, **kwargs)(uppervalues)

    def boundary(self, *args, how=None, bounds=(None, None), **kwargs):
        assert isinstance(bounds, (tuple, list))
        assert len(bounds) == 2
        getvalue = lambda value, bound: value if value is not None else bound
        value = (getvalue(self.leftvalue, bounds[0]), getvalue(self.rightvalue, bounds[-1]))
        return self.transformation(*args, method='boundary', how=how, **kwargs)(value)  

    def expand(self, *args, how=None, bounds=(None, None), **kwargs):
        assert isinstance(bounds, (tuple, list))
        assert len(bounds) == 2
        getvalue = lambda value, bound: value if value is not None else bound
        cls = self.transformation(*args, method='expand', how=how, **kwargs)
        return [cls(value) for value in np.arange(getvalue(self.lower, bounds[0]), getvalue(self.upper, bounds[-1]) + self.spec.threshold, self.spec.threshold)]

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
        assert all([how == 'cumulate', direction == 'lower' or direction == 'upper'])
        value = getattr(self, {'upper':'leftvalue', 'lower':'rightvalue'}[direction])
        return self.transformation(*args, method='consolidate', how=how, direction=direction, **kwargs)(value)
    
    @consolidate.register('differential')
    def differential(self, *args, how='differential', bounds=(None, None), **kwargs):
        assert how == 'differential'
        getvalue = lambda value, bound: value if value is not None else bound
        value = [getvalue(self.leftvalue, bounds[0]), getvalue(self.rightvalue, bounds[-1])]
        return self.transformation(*args, method='consolidate', how=how, **kwargs)(value[-1] - value[0])    
    

    
    
    
    
    
    

    
    
    
    
    
    
    
    
    
    
    
    