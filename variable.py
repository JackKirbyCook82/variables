# -*- coding: utf-8 -*-
"""
Created on Sun Jun 9 2019
@name:   Variable Objects
@author: Jack Kirby Cook

"""

from abc import ABC, abstractmethod
from functools import update_wrapper

from utilities.strings import uppercase

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Variable', 'CustomVariable', 'custom_operation', 'custom_transformation', 'create_customvariable']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


CUSTOM_VARIABLES = {}

def create_customvariable(spec):
    try: return CUSTOM_VARIABLES[spec.jsonstr]
    except: 
        datatype = spec.datatype        
        base = CustomVariable.subclasses()[datatype]
        name = '_'.join([uppercase(spec.data, index=0, withops=True), base.__name__])
        attrs = {'spec':spec}
        newvariable = type(name, (base,), attrs)
        CUSTOM_VARIABLES[spec.jsonstr] = newvariable
        return newvariable  


class VariableNotCreatedError(Exception): pass  
       

class Variable(ABC):
    @abstractmethod
    def datatype(self): pass
    @abstractmethod
    def __str__(self): pass
    @abstractmethod
    def __repr__(self): pass
    @abstractmethod
    def fromstr(self): pass

    @property
    def value(self): return self.__value
    def __init__(self, value): self.__value = value
    @property
    def name(self): return self.__class__.__name__
   
    def __eq__(self, other): 
        if self.datatype != other.datatype: raise TypeError('{} != {}'.format(type(self), type(other)))
        return self.value == other.value
    def __ne__(self, other): return not self.__eq__(other)

    def __add__(self, other): return self.add(other)
    def __sub__(self, other): return self.subtract(other)
    def __mul__(self, other): return self.multiply(other)
    def __truediv__(self, other): return self.divide(other)
    
    def transformation(self, method, *args, **kwargs): return getattr(self, method)(*args, **kwargs)
    def operation(self, method, other, *args, **kwargs): return getattr(self, method)(other, *args, **kwargs)  

    # REGISTER SUBCLASSES  
    __subclasses = {}      
    @classmethod
    def subclasses(cls): return cls.__subclasses     
    
    @classmethod
    def register(cls, datatype):  
        def wrapper(subclass):
            name = subclass.__name__
            bases = (subclass, cls)
            newsubclass = type(name, bases, dict(datatype=datatype))
            Variable.__subclasses[datatype] = newsubclass
            return newsubclass
        return wrapper  


def custom_operation(*func_args, **func_kwargs):
    def decorator(function):
        def wrapper(self, other, *args, **kwargs):
            cls = create_customvariable(getattr(self.spec, function.__name__)(other.spec, *func_args, **func_kwargs))
            return cls(function(self, other, *args, **kwargs))
        update_wrapper(wrapper, function)
        return wrapper
    return decorator

def custom_transformation(*func_args, **func_kwargs):
    def decorator(function):
        def wrapper(self, *args, **kwargs):
            cls = create_customvariable(getattr(self.spec, function.__name__)(*func_args, **func_kwargs))
            return cls(function(self, *args, **kwargs))
        update_wrapper(wrapper, function)
        return wrapper
    return decorator


class CustomVariable(Variable):
    def __new__(cls, *args, **kwargs):
        if cls == CustomVariable: raise VariableNotCreatedError()
        if not hasattr(cls, 'spec'): raise VariableNotCreatedError()
        return super().__new__(cls)
    
    def __init__(self, value):
        self.spec.checkval(value)
        super().__init__(value)
        
    @classmethod
    def fromstr(cls, varstr): return cls(cls.spec.asval(varstr))    
    
    def __str__(self): return self.spec.asstr(self.value)  
    def __repr__(self): return '{}({})'.format(self.__class__.__name__, self.value)     
    
    # REGISTER SUBCLASSES  
    __subclasses = {}      
    @classmethod
    def subclasses(cls): return cls.__subclasses  
    @classmethod
    def custom_subclasses(cls): return list(CUSTOM_VARIABLES.values())
    
    @classmethod
    def register(cls, datatype):  
        def wrapper(subclass):
            name = subclass.__name__
            bases = (subclass, cls)
            newsubclass = type(name, bases, dict(datatype=datatype))
            CustomVariable.__subclasses[datatype] = newsubclass
            return newsubclass
        return wrapper  
    
    
    
    
    
    
    
    
    
    
    
    