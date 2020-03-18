# -*- coding: utf-8 -*-
"""
Created on Thurs Jun 6 2019
@name:   Variable Functions
@author: Jack Kirby Cook

"""

from functools import reduce, update_wrapper
import numpy as np

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['varray_fromvalues', 'summation', 'minimum', 'maximum', 'mean', 'average', 'upper_cumulate', 'lower_cumulate', 'upper_uncumulate', 'lower_uncumulate', 
           'moving_average', 'moving_summation', 'moving_difference', 'moving_minimum', 'moving_maximum', 'moving_couple', 'groupby_bins', 'groupby_contains', 'groupby_overlaps']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


_flatten = lambda nesteditems: [item for items in nesteditems for item in items]


class VariableMethodNotSupported(Exception): 
    def __init__(self, function, datatype): 
        super().__init__('{}([<{}>,])'.format(function.__name__, datatype)) 


# FACTORY
def varray_fromvalues(data, *args, variable, **kwargs): 
    return [variable(value) for value in data]


# SUPPORT
def varray_datatype(varray): 
    varray_datatypes = list(set([item.datatype.lower() for item in varray]))
    assert len(varray_datatypes) == 1
    return varray_datatypes[0]

def varray_type(varray):
    varray_types = list(set([item.__class__ for item in varray]))
    assert len(varray_types) == 1
    return varray_types[0]    

def varray_dispatcher(mainfunc):
    _registry = {}    
    def update(regfunc, *keys): _registry.update({key:regfunc for key in keys})
    def registry(): return _registry
    
    def register(*keys): 
        def register_decorator(regfunc): 
            update(regfunc, *keys) 
            def register_wrapper(*args, **kwargs): 
                return regfunc(*args, **kwargs) 
            return register_wrapper 
        return register_decorator 

    def wrapper(varray, *args, **kwargs): 
        datatype = varray_datatype(varray)
        if datatype not in registry().keys(): raise VariableMethodNotSupported(mainfunc, datatype)
        else: return registry()[datatype](varray, *args, **kwargs)  

    wrapper.register = register 
    wrapper.registry = registry
    update_wrapper(wrapper, mainfunc)
    return wrapper
    

# REDUCTIONS
@varray_dispatcher
def couple(varray, *args, **kwargs): pass
@couple.register('num', 'range', 'category')
def _couple(varray, *args, **kwargs): return reduce(lambda x, y: x.couple(y, *args, **kwargs), varray)    

@varray_dispatcher
def summation(varray, *args, **kwargs): pass
@summation.register('num', 'range', 'category', 'geography')
def _summation(varray, *args, **kwargs): return reduce(lambda x, y: x.add(y, *args, **kwargs), varray)

@varray_dispatcher
def minimum(varray, *args, **kwargs): pass
@minimum.register('num', 'range', 'date', 'datetime')
def _minimum(varray, *args, **kwargs): return reduce(lambda x, y: min(x, y), varray)
      
@varray_dispatcher
def maximum(varray, *args, **kwargs): pass
@maximum.register('num', 'range', 'date', 'datetime')
def _maximum(varray, *args, **kwargs): return reduce(lambda x, y: max(x, y), varray)

@varray_dispatcher
def mean(varray, *args, **kwargs): pass
@mean.register('num')
def _mean(varray, *args, **kwargs): return reduce(lambda x, y: x.add(y, *args, **kwargs), varray) / len(varray)

@varray_dispatcher
def average(varray, *args, **kwargs): pass
@average.register('num')
def _average(varray, *args, weights=None, **kwargs):
    if not weights: weights = [1/len(varray)] * len(varray)
    assert len(weights) == len(varray)
    return summation([item.multiply(weight, *args, **kwargs) for item, weight in zip(varray, weights)], *args, **kwargs)   
    

#GROUPING    
@varray_dispatcher
def groupby_bins(varray, *args, groups, **kwargs): pass

@groupby_bins.register('num')
def _groupby_bins_nums(varray, *args, groups, right=True, **kwargs):
    NumVariable = varray_type(varray)
    RangeVariable = NumVariable.unconsolidate(*args, how='group', **kwargs)
    grpkeys = [[None, groups[0]], *[[groups[index], groups[index+1]] for index in range(len(groups)-1)], [groups[-1], None]] 
    grpkeys = [RangeVariable(grpkey) for grpkey in grpkeys]
    grpvalues = [[] for i in range(len(grpkeys))]
    indexes = np.digitize([item.value for item in varray], groups, right=True)
    for index, item in zip(indexes, varray): grpvalues[index].append(item)
    groupings = {grpkey:grpvalue for grpkey, grpvalue in zip(grpkeys, grpvalues)}
    return groupings

@groupby_bins.register('range')
def _groupby_bins_range(varray, *args, groups, **kwargs):
    RangeVariable = varray_type(varray)
    grpkeys = [[None, groups[0]], *[[groups[index], groups[index+1]] for index in range(len(groups)-1)], [groups[-1], None]]   
    grpkeys = [RangeVariable(grpkey) for grpkey in grpkeys]
    grpvalues = [[] for i in range(len(grpkeys))]
    grpvalues = [[item for item in varray if grpkey.overlaps(item)] for grpkey in grpkeys]
    assert len(_flatten(grpvalues)) == len(varray)
    groupings = {grpkey:grpvalue for grpkey, grpvalue in zip(grpkeys, grpvalues)}
    return groupings 

@varray_dispatcher
def groupby_contains(varray, *args, **kwargs): pass
@groupby_contains.register('category', 'range')
def _groupby_contains(varray, *args, **kwargs): 
    groupings = {grpkey:[grpvalue for grpvalue in varray if grpkey.contains(grpvalue)] for grpkey in varray} 
    groupings = {key:values for key, values in groupings.items() if not any([key in othervalues for otherkey, othervalues in groupings.items() if key != otherkey])} 
    return groupings

@varray_dispatcher
def groupby_overlaps(varray, *args, **kwargs): pass
@groupby_overlaps.register('category', 'range')
def _groupby_overlaps(varray, *args, **kwargs):
    groupings = {grpkey:[grpvalue for grpvalue in varray if grpkey.overlaps(grpvalue)] for grpkey in varray}
    groupings = {couple(values):values for values in set(*groupings.values())}
    return groupings

# BROADCASTING
@varray_dispatcher
def consolidate(varray, *args, how, **kwargs): pass
@consolidate.register('range')
def _consolidate(varray, *args, how, **kwargs): return [item.consolidate(*args, how=how, **kwargs) for item in varray]   

@varray_dispatcher
def unconsolidate(varray, *args, how, **kwargs): pass
@unconsolidate.register('num')
def _unconsolidate(varray, *args, how, **kwargs): return [item.unconsolidate(*args, how=how, **kwargs) for item in varray]   

@varray_dispatcher
def boundary(varray, *args, **kwargs): pass
@boundary.register('range')
def _boundary(varray, *args, **kwargs): return [item.boundary(*args, **kwargs) for item in varray]   

# ROLLING
@varray_dispatcher
def upper_cumulate(varray, *args, **kwargs): pass
@upper_cumulate.register('num', 'range')
def _upper_cumulate(varray, *args, **kwargs): 
    function = lambda x: [summation(x[slice(0, i+1)], *args, **kwargs) for i in range(len(varray))]
    return function(varray[::-1])[::-1]

@varray_dispatcher
def lower_cumulate(varray, *args, **kwargs): pass
@lower_cumulate.register('num', 'range')
def _lower_cumulate(varray, *args, **kwargs): 
    function = lambda x: [summation(x[slice(0, i+1)], *args, **kwargs) for i in range(len(varray))]
    return function(varray)
  
@varray_dispatcher
def upper_uncumulate(varray, *args, **kwargs): pass
@upper_uncumulate.register('num', 'range')
def _upper_uncumulate(varray, *args, **kwargs): 
    function = lambda x: [x[0]] + [x.subtract(y, *args, **kwargs) for x, y in zip(x[1:], x[:-1])]
    return function(varray[::-1])[::-1]
    
@varray_dispatcher
def lower_uncumulate(varray, *args, **kwargs): pass
@lower_uncumulate.register('num', 'range')
def _lower_uncumulate(varray, *args, **kwargs): 
    function = lambda x: [x[0]] + [x.subtract(y, *args, **kwargs) for x, y in zip(x[1:], x[:-1])]
    return function(varray)

@varray_dispatcher
def moving_minimum(varray, *args, period, **kwargs): pass
@moving_minimum.register('num', 'date', 'datetime')
def _moving_minimum(varray, *args, period, **kwargs):
    assert isinstance(period, int)
    assert len(varray) >= period
    return [minimum(varray[i:i+1+period], *args, period=period, **kwargs) for i in range(0, len(varray)-period)]

@varray_dispatcher
def moving_maximum(varray, *args, period, **kwargs): pass
@moving_maximum.register('num', 'date', 'datetime')
def _moving_maximum(varray, *args, period, **kwargs):
    assert isinstance(period, int)
    assert len(varray) >= period
    return [maximum(varray[i:i+1+period], *args, period=period, **kwargs) for i in range(0, len(varray)-period)]

@varray_dispatcher
def moving_average(varray, *args, period, **kwargs): pass
@moving_average.register('num')
def _moving_average(varray, *args, period, **kwargs):
    assert isinstance(period, int)
    assert len(varray) >= period 
    return [mean(varray[i:i+1+period], *args, period=period, **kwargs) for i in range(0, len(varray)-period)]  

@varray_dispatcher
def moving_summation(varray, *args, period, **kwargs): pass
@moving_summation.register('num', 'range')
def moving_summation(varray, *args, period, **kwargs):
    assert isinstance(period, int)
    assert len(varray) >= period
    return [summation(varray[i:i+1+period], *args, period=period, **kwargs) for i in range(0, len(varray)-period)]  

@varray_dispatcher
def moving_difference(varray, *args, period, **kwargs): pass
@moving_difference.register('num')
def _moving_difference_num(varray, *args, period, **kwargs):
    assert isinstance(period, int)
    assert len(varray) >= period
    return [varray[i].subtract(varray[i+period], *args, period=period, **kwargs) for i in range(0, len(varray)-period)]  
@moving_difference.register('range')
def _moving_difference_range(varray, *args, period, **kwargs):
    assert isinstance(period, int)
    assert len(varray) >= period
    return [item.differental(*args, **kwargs) for item in moving_summation(varray, *args, period=period, **kwargs)]

@varray_dispatcher
def moving_couple(varray, *args, period, **kwargs): pass
@moving_couple.register('num', 'range', 'category')
def _moving_couple(varray, *args, period, **kwargs):
    assert isinstance(period, int)
    assert len(varray) >= period
    return [couple(varray[i:i+1+period], *args, period=period, **kwargs) for i in range(0, len(varray)-period)]   


    
    

    
    
