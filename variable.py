# -*- coding: utf-8 -*-
"""
Created on Sun Jun 9 2019
@name:   Variable Objects
@author: Jack Kirby Cook

"""

from abc import ABC, abstractmethod
import json

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['create_customvariable', 'Variable', 'CustomVariable']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


VARIABLES = {}
CUSTOM_VARIABLES = {}
CUSTOM_VARIABLE_SUBCLASSES = {}


def create_customvariable(spec):
    try: return CUSTOM_VARIABLE_SUBCLASSES[hash(spec)]
    except:      
        base = CUSTOM_VARIABLES[spec.datatype]
        name = '_'.join([spec.dataname, base.__name__])
        attrs = {'spec':spec}
        newvariable = type(name, (base,), attrs)
        print('Created: {}\n'.format(newvariable.name()))
        CUSTOM_VARIABLE_SUBCLASSES[hash(spec)] = newvariable
        return newvariable  

def samevariable(function):
    def wrapper(self, other, *args, **kwargs):
        try: 
            if self.spec != other.spec: raise TypeError('{} != {}'.format(type(self), type(other)))    
        except AttributeError: 
            if type(self) != type(other): raise TypeError('{} != {}'.format(type(self), type(other)))    
        return function(self, other, *args, **kwargs)
    return wrapper


class VariableNotCreatedError(Exception): pass     
class VariableOverlapError(Exception):
    def __init__(self, instance, other, operation): 
        super().__init__('{}.{}({})'.format(repr(instance), operation, repr(other))) 
        

class Variable(ABC):
    @abstractmethod
    def __repr__(self): pass    
    @abstractmethod
    def __str__(self): pass
    @abstractmethod
    def __hash__(self): pass
    @abstractmethod
    def fromstr(self): pass
    @abstractmethod
    def checkvalue(self, value): pass
    @abstractmethod
    def fixvalue(self, value): pass

    @classmethod
    def jsonstr(cls): return json.dumps(dict(data=cls.datatype), sort_keys=True, indent=3, separators=(',', ' : '), default=str)   
    @classmethod
    def name(cls): return '_'.join([cls.__name__, 'Variable'])
    @property
    def value(self): return self.__value    
    def __init__(self, value): 
        try: self.checkvalue(value)
        except ValueError: value = self.fixvalue(value)
        self.checkvalue(value)
        self.__value = value   
    
    # EQUALITY
    @samevariable
    def __eq__(self, other): return self.value == other.value
    def __ne__(self, other): return not self.__eq__(other)
    
    @samevariable
    def __lt__(self, other): return self.value < other.value
    @samevariable
    def __gt__(self, other): return self.value > other.value        
    @samevariable
    def __le__(self, other): return self.value <= other.value
    @samevariable
    def __ge__(self, other): return self.value >= other.value

    @classmethod
    def register(cls, datatype):  
        def wrapper(subclass):
            newsubclass = type(subclass.__name__, (subclass, cls), dict(datatype=datatype.lower()))
            VARIABLES[datatype.lower()] = newsubclass
            return newsubclass
        return wrapper 

 
class CustomVariable(Variable):
    def __repr__(self): return '{}({})'.format(self.__class__.__name__, self.value) 
    def __str__(self): return self.spec.asstr(self.value)  
    def __new__(cls, *args, **kwargs):
        if cls == CustomVariable: raise VariableNotCreatedError()
        if not hasattr(cls, 'spec'): raise VariableNotCreatedError()
        return super().__new__(cls)
       
    @classmethod
    def fromstr(cls, varstr): return cls(cls.spec.asval(varstr))
    @classmethod
    def jsonstr(cls): return cls.spec.jsonstr()    
    
    @classmethod
    def register(cls, datatype):  
        def wrapper(subclass):
            newsubclass = type(subclass.__name__, (subclass, cls), dict(datatype=datatype.lower()))
            CUSTOM_VARIABLES[datatype.lower()] = newsubclass
            return newsubclass
        return wrapper  
    
    # OPERATIONS
    @classmethod
    def operation(cls, other, *args, method, **kwargs): 
        try: return create_customvariable(getattr(cls.spec, method)(other.spec, *args, **kwargs))
        except AttributeError: return create_customvariable(cls.spec.operation(other.spec, *args, method=method, **kwargs))

    # TRANSFORMATIONS
    @classmethod
    def transformation(cls, *args, method, how, **kwargs): 
        try: return create_customvariable(getattr(cls.spec, method)(*args, how=how, **kwargs))
        except AttributeError: return create_customvariable(cls.spec.transformation(*args, method=method, how=how, **kwargs))    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
