# -*- coding: utf-8 -*-
"""
Created on Sun Jun 9 2019
@name:   Variable Objects
@author: Jack Kirby Cook

"""

from abc import ABC, abstractmethod

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Variable', 'CustomVariable', 'create_customvariable', 'samevariable']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


CUSTOM_VARIABLES = {}


def create_customvariable(spec):
    try: return CUSTOM_VARIABLES[spec.jsonstr]
    except:      
        base = CustomVariable.getsubclass(spec.datatype)
        name = '_'.join([spec.dataname, base.__name__])
        attrs = {'spec':spec}
        newvariable = type(name, (base,), attrs)
        print('Created: {}\n'.format(newvariable.name()))
        CUSTOM_VARIABLES[spec.jsonstr] = newvariable
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
    def __str__(self): pass
    @abstractmethod
    def __repr__(self): pass
    @abstractmethod
    def fromstr(self): pass

    @property
    def value(self): return self.__value
    def __init__(self, value): self.__value = value
    def __hash__(self): return hash(str(self))
    
    @classmethod
    def name(cls): return '_'.join([cls.__name__, 'Variable'])
   
    def __add__(self, other): return self.add(other)
    def __sub__(self, other): return self.subtract(other)
    def __mul__(self, other): return self.multiply(other)
    def __truediv__(self, other): return self.divide(other)    
    
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


    # REGISTER SUBCLASSES  
    __subclasses = {}    
    @classmethod
    def subclasses(cls): return cls.__subclasses
    @classmethod
    def getsubclass(cls, datatype): return cls.__subclasses[datatype.lower()]     
    
    @classmethod
    def register(cls, datatype):  
        def wrapper(subclass):
            name = subclass.__name__
            bases = (subclass, cls)
            newsubclass = type(name, bases, dict(datatype=datatype.lower()))
            Variable.__subclasses[datatype.lower()] = newsubclass
            return newsubclass
        return wrapper 

 
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
    def getsubclass(cls, datatype): return cls.__subclasses[datatype.lower()]
    @classmethod
    def custom_subclasses(cls): return list(CUSTOM_VARIABLES.values())
    
    @classmethod
    def register(cls, datatype):  
        def wrapper(subclass):
            name = subclass.__name__
            bases = (subclass, cls)
            newsubclass = type(name, bases, dict(datatype=datatype.lower()))
            CustomVariable.__subclasses[datatype.lower()] = newsubclass
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

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    