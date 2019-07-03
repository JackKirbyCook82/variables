# -*- coding: utf-8 -*-
"""
Created on Sun Jun 9 2019
@name:   Variable Objects
@author: Jack Kirby Cook

"""

from abc import ABC, abstractmethod

from utilities.strings import uppercase

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Variable', 'CustomVariable', 'create_customvariable']
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
    @classmethod
    def name(cls): return cls.__name__ + '_Variable'
   
    def __add__(self, other): return self.add(other)
    def __sub__(self, other): return self.subtract(other)
    def __mul__(self, other): return self.multiply(other)
    def __truediv__(self, other): return self.divide(other)    
    
    # EQUALITY
    def __eq__(self, other): 
        if self.spec != other.spec: raise TypeError('{} != {}'.format(type(self), type(other)))
        return self.value == other.value
    def __ne__(self, other): return not self.__eq__(other)
    
    def __lt__(self, other): return self.value < other.value
    def __le__(self, other): return self.value <= other.value
    def __ge__(self, other): return self.value >= other.value
    def __gt__(self, other): return self.value > other.value

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
    
    # OPERATIONS
    @classmethod
    def added(cls, other, *args, **kwargs): return create_customvariable(cls.spec.add(other.spec, *args, **kwargs))
    @classmethod
    def subtracted(cls, other, *args, **kwargs): return create_customvariable(cls.spec.subtract(other.spec, *args, **kwargs))
    @classmethod
    def multiplied(cls, other, *args, **kwargs): return create_customvariable(cls.spec.multiply(other.spec, *args, **kwargs))
    @classmethod
    def divided(cls, other, *args, **kwargs): return create_customvariable(cls.spec.divide(other.spec, *args, **kwargs))

    # TRANSFORMATIONS
    @classmethod
    def modify(cls, *args, mod, **kwargs): return create_customvariable(cls.spec.modify(*args, mod=mod, **kwargs))    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    