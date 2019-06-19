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
__all__ = ['Variable', 'CustomVariable', 'create_customvariable', 'VariableOperationNotSupportedError', 'VariableTransformationNotSupportedError']
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

class VariableOperationNotSupportedError(Exception): 
    def __init__(self, variable, other, operation): super().__init__('{}.{}({})'.format(repr(variable), operation, repr(other)))
class VariableTransformationNotSupportedError(Exception):
    def __init__(self, variable, transformation, method): super().__init__('{}.{}(method={})'.format(repr(variable), transformation, method))   
       

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
   
    def __add__(self, other): return self.add(other)
    def __sub__(self, other): return self.subtract(other)
    def __mul__(self, other): return self.multiply(other)
    def __truediv__(self, other): return self.divide(other)    
    
    # EQUALITY
    def __eq__(self, other): 
        if self.datatype != other.datatype: raise TypeError('{} != {}'.format(type(self), type(other)))
        return self.value == other.value
    def __ne__(self, other): return not self.__eq__(other)

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

    # OPERATIONS
    def add(self, other, *args, **kwargs): raise VariableOperationNotSupportedError(self, other, 'add')
    def subtract(self, other, *args, **kwargs): raise VariableOperationNotSupportedError(self, other, 'subtract')
    def multiply(self, other, *args, **kwargs): raise VariableOperationNotSupportedError(self, other, 'multiply')
    def divide(self, other, *args, **kwargs): raise VariableOperationNotSupportedError(self, other, 'divide')

 
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
    def operation(cls, method, other, *args, **kwargs):        
        try: return create_customvariable(getattr(cls.spec, method)(other.spec, *args, **kwargs))
        except AttributeError: raise VariableOperationNotSupportedError 
    
    # TRANSFORMATIONS
    @classmethod
    def transformation(cls, method, *args, **kwargs): 
        try: return create_customvariable(getattr(cls.spec, method)(*args, **kwargs))
        except AttributeError: raise VariableTransformationNotSupportedError
    
    
    
    
    
    
    
    
    
    