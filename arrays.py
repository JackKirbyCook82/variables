# -*- coding: utf-8 -*-
"""
Created on Thurs Jun 6 2019
@name:   Variable Functions
@author: Jack Kirby Cook

"""

from functools import reduce

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['apply_tovarray', 'cumulate', 'consolidate', 'summation']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


# FACTORY
def apply_tovarray(varray, function, *args, **kwargs):
    return function(varray, *args, **kwargs)


# BROADCASTING
def cumulate(varray, *args, direction='upper', **kwargs): 
    function = lambda x: [summation(x[slice(0, i+1)], *args, **kwargs) for i in range(len(varray))]
    if direction == 'upper': return function(varray)
    elif direction == 'lower': return function(varray[::-1])[::-1]
    else: raise TypeError(direction)

def consolidate(varray, *args, method, **kwargs): 
    return [getattr(item, method)(*args, **kwargs) for item in varray]


# REDUCTIONS
def average(varray, *args, weights=None, **kwargs): 
    if not weights: weights = [1] * len(varray)
    assert len(weights) == len(varray)
    return summation([item.multiply(weight, *args, **kwargs) for item, weight in zip(varray, weights)], *args, **kwargs)
    
def summation(varray, *args, **kwargs): return reduce(lambda x, y: x.add(y, *args, **kwargs), varray)
def minimum(varray, *args, **kwargs): return reduce(lambda x, y: min(x,y), varray)
def maximum(varray, *args, **kwargs): return reduce(lambda x, y: max(x,y), varray)





