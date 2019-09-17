# -*- coding: utf-8 -*-
"""
Created on Thurs Jun 6 2019
@name:   Variable Functions
@author: Jack Kirby Cook

"""

from functools import reduce

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['varray_fromvalues', 'summation', 'minimum', 'maximum', 'mean', 'average', 'combine_contained', 'combine_overlap',
           'bound', 'consolidate', 'unconsolidate', 'cumulate', 'uncumulate', 'moving_average', 'moving_total', 'moving_bracket', 'moving_differential']
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

def sort(varray, ascending=True):
    return sorted(varray, reverse=not ascending)

    
# REDUCTIONS
def summation(varray, *args, **kwargs): return reduce(lambda x, y: x.add(y, *args, **kwargs), varray)
def minimum(varray, *args, **kwargs): return reduce(lambda x, y: min(x, y), varray)
def maximum(varray, *args, **kwargs): return reduce(lambda x, y: max(x, y), varray)

def mean(varray, *args, **kwargs): return reduce(lambda x, y: x.add(y, *args, **kwargs), varray) / len(varray)
def average(varray, *args, weights=None, **kwargs): 
    if not weights: weights = [1/len(varray)] * len(varray)
    assert len(weights) == len(varray)
    return summation([item.multiply(weight, *args, **kwargs) for item, weight in zip(varray, weights)], *args, **kwargs)
 
def combine_contained(varray, *args, ascending=True, **kwargs):
    varray = sort(varray, ascending=ascending)
    newvarray = [varray[0]]
    for item in varray[1:]:   
        if item in newvarray[-1]: newvarray[-1] = item
        elif newvarray[-1] in item: pass
        else: newvarray.append(item)   
    return newvarray

def combine_overlap(varray, *args, ascending=True, **kwargs):
    varray = sort(varray, ascending=ascending)
    newvarray = [varray[0]]
    for item in varray[1:]:
        if varray[-1].overlaps(item): newvarray[-1] = newvarray[-1].merge(item)
        else: newvarray.append(item)
    return newvarray


# BROADCASTING
def bound(varray, *args, bounds, **kwargs): return [item.bound(*args, bounds=bounds, **kwargs) for item in varray]

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

def moving_average(varray, *args, period, **kwargs):
    assert isinstance(period, int)
    assert len(varray) >= period 
    return [mean(varray[i:i+period]) for i in range(0, len(varray)-period+1)]  

def moving_total(varray, *args, period, **kwargs):
    assert isinstance(period, int)
    assert len(varray) >= period
    return [summation(varray[i:i+period]) for i in range(0, len(varray)-period+1)]  

def moving_bracket(varray, *args, period, **kwargs):
    assert isinstance(period, int)
    assert len(varray) >= period
    if varraytype(varray) == 'num': return [varray[i].bracket(varray[i+period], *args, period=period, **kwargs) for i in range(0, len(varray)-period)]
    elif varraytype(varray) == 'range': return moving_total(varray, *args, period=period, **kwargs)
    else: raise ValueError(varraytype(varray))    
    
def moving_differential(varray, *args, period, **kwargs):
    assert isinstance(period, int)
    assert len(varray) >= period
    return [varray[i].subtract(varray[i+period], *args, **kwargs) for i in range(0, len(varray)-period)]  
    

    
    
