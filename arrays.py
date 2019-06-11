# -*- coding: utf-8 -*-
"""
Created on Thurs Jun 6 2019
@name:   Variable Functions
@author: Jack Kirby Cook

"""

from functools import update_wrapper, reduce

from variables import Num, Range, Category

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['apply_tovarray', 'cumulate', 'consolidate', 'summation']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


class VariableMethodNotSupportedError(Exception):
    def __init__(self, variabletype, functionname): super().__init__('{}([<{}>])'.format(functionname, variabletype))


def variable_dispatcher(mainfunc):
    _registry = {}
    
    def update(regfunc, *vtypes): _registry.update({vtype:regfunc for vtype in vtypes})
    def registry(): return _registry
    
    def register(*vtypes): 
        def register_decorator(regfunc): 
            update(regfunc, *vtypes) 
            def register_wrapper(*args, **kwargs): 
                return regfunc(*args, **kwargs) 
            return register_wrapper 
        return register_decorator 

    def wrapper(varray, *args, **kwargs): 
        vtypes = list(set([type(item) for item in varray]))
        assert len(vtypes) == 1
        try: return _registry[vtypes[0]](varray, *args, **kwargs)   
        except KeyError: raise VariableMethodNotSupportedError(vtypes[0], mainfunc.__name__)

    wrapper.register = register 
    wrapper.registry = registry
    update_wrapper(wrapper, mainfunc)
    return wrapper


# FACTORY
def apply_tovarray(varray, function, *args, **kwargs):
    pass


# BROADCASTING
@variable_dispatcher
def cumulate(varray, *args, direction='upper', **kwargs): pass

@cumulate.register(Num, Range, Category)
def _cumulate(varray, *args, direction='upper', **kwargs): 
    function = lambda x: [summation(x[slice(0, i+1)], *args, **kwargs) for i in range(len(varray))]
    if direction == 'upper': return function(varray)
    elif direction == 'lower': return function(varray[::-1])[::-1]
    else: raise TypeError(direction)


@variable_dispatcher
def consolidate(varray, *args, method, **kwargs): pass

@consolidate.register(Range)
def _consolidate(varray, *args, method, **kwargs): 
    return [getattr(item, method)(*args, **kwargs) for item in varray]


# REDUCTIONS
@variable_dispatcher
def summation(varray, *args, **kwargs): pass

@summation.register(Num, Range, Category)
def _summation(varray, *args, **kwargs): 
    return reduce(lambda x, y: x + y, varray)










