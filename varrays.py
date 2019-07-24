# -*- coding: utf-8 -*-
"""
Created on Thurs Jun 6 2019
@name:   Variable Functions
@author: Jack Kirby Cook

"""

from functools import reduce

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = []
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


# FACTORY
def varray_fromvalues(data, *args, variable, **kwargs): 
    return [variable(value) for value in data]


# SUPPORT
def varraytype(varray): 
    varraytypes = list(set([item.datatype.lower() for item in varray]))
    assert len(varraytypes) == 1
    return varraytypes[0]


# REDUCTIONS
def summation(varray, *args, **kwargs): return reduce(lambda x, y: x.add(y, *args, **kwargs), varray)
def minimum(varray, *args, **kwargs): return reduce(lambda x, y: min(x, y), varray)
def maximum(varray, *args, **kwargs): return reduce(lambda x, y: max(x, y), varray)

def mean(varray, *args, **kwargs): return reduce(lambda x, y: x.add(y, *args, **kwargs), varray) / len(varray)
def average(varray, *args, weights=None, **kwargs): 
    if not weights: weights = [1/len(varray)] * len(varray)
    assert len(weights) == len(varray)
    return summation([item.multiply(weight, *args, **kwargs) for item, weight in zip(varray, weights)], *args, **kwargs)
   

# BROADCASTING
def boundary(varray, *args, boundarys, **kwargs): return [item.boundary(*args, boundarys=boundarys, **kwargs) for item in varray]

def consolidate(varray, *args, how, **kwargs): return [getattr(item, how)(*args, **kwargs) for item in varray]   
def unconsolidate(varray, *args, how, **kwargs): return [getattr(item, how)(*args, **kwargs) for item in varray] 


# ROLLING
def cumulate(varray, *args, direction, **kwargs): 
    function = lambda x: [summation(x[slice(0, i+1)], *args, **kwargs) for i in range(len(varray))]
    if direction == 'lower': return function(varray)
    elif direction == 'upper': return function(varray[::-1])[::-1]
    else: raise TypeError(direction)
    
def uncumulate(varray, *args, direction, **kwargs): 
    function = lambda x: [x[0]] + [x - y for x, y in zip(x[1:], x[:-1])]
    if direction == 'lower': return function(varray)
    elif direction == 'upper': return function(varray[::-1])[::-1]
    else: raise TypeError(direction)

def movingaverage(varray, *args, period, **kwargs):
    assert isinstance(period, int)
    assert len(varray) >= period 
    return [mean(varray[i:i+period]) for i in range(0, len(varray)-period+1)]  

def movingtotal(varray, *args, period, **kwargs):
    assert isinstance(period, int)
    assert len(varray) >= period
    return [summation(varray[i:i+period]) for i in range(0, len(varray)-period+1)]  

def movingbracket(varray, *args, period, **kwargs):
    assert isinstance(period, int)
    assert len(varray) >= period
    if varraytype(varray) == 'num': return [varray[i].bracket(varray[i+period], *args, period=period, **kwargs) for i in range(0, len(varray)-period)]
    elif varraytype(varray) == 'range': return movingtotal(varray, *args, period=period, **kwargs)
    else: raise ValueError(varraytype(varray))    
    
    
    
    
    
    
    
    
