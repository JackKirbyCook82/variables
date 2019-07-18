# -*- coding: utf-8 -*-
"""
Created on Thurs Jun 6 2019
@name:   Variable Functions
@author: Jack Kirby Cook

"""

from functools import reduce

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['varray_fromvalues', 'summation', 'mean', 'minimum', 'maximum', 'average', 'boundary', 'consolidate', 'cumulate']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


# FACTORY
def varray_fromvalues(data, *args, variable, **kwargs): 
    return [variable(value) for value in data]


# SUPPORT
def varray_datatype(varray): 
    datatypes = list(set([item.datatype for item in varray]))
    assert len(datatypes) == 1
    return datatypes[0]


# REDUCTIONS
def summation(varray, *args, **kwargs): return reduce(lambda x, y: x.add(y, *args, **kwargs), varray)
def mean(varray, *args, **kwargs): return reduce(lambda x, y: x.add(y, *args, **kwargs), varray) / len(varray)
def minimum(varray, *args, **kwargs): return reduce(lambda x, y: min(x, y), varray)
def maximum(varray, *args, **kwargs): return reduce(lambda x, y: max(x, y), varray)
def average(varray, *args, weights=None, **kwargs): 
    if not weights: weights = [1/len(varray)] * len(varray)
    assert len(weights) == len(varray)
    return summation([item.multiply(weight, *args, **kwargs) for item, weight in zip(varray, weights)], *args, **kwargs)
   

# BROADCASTING
def boundary(varray, *args, boundarys, **kwargs): return [item.boundary(*args, boundarys=boundarys, **kwargs) for item in varray]
def consolidate(varray, *args, method, **kwargs): return [getattr(item, method)(*args, **kwargs) for item in varray]    

def cumulate(varray, *args, direction, **kwargs): 
    datatype = varray_datatype(varray)    
    if datatype == 'range': function = lambda x: [summation(x[slice(0, i+1)], *args, **kwargs) for i in range(len(varray))]
    elif datatype == 'num': function = lambda x: [x.cumulate(*args, direction=direction, **kwargs) for item in x]
    else: raise TypeError(datatype)
    
    if direction == 'lower': return function(varray)
    elif direction == 'upper': return function(varray[::-1])[::-1]
    else: raise TypeError(direction)





