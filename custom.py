# -*- coding: utf-8 -*-
"""
Created on Sun Jun 9 2019
@name:   Custom Variables
@author: Jack Kirby Cook

"""

from abc import ABC, abstractmethod

from utilities.strings import uppercase

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['create_customvariable', 'CustomVariable', 'VariableOverlapError', 'VariableOperationError', 'VariableOperationNotSupportedError']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


def sametype(function):
    def wrapper(self, other, *args, **kwargs):
        if self.variabletype != other.variabletype: raise TypeError(' != '.join([self.name, other.name]))
        return function(self, other, *args, **kwargs)
    return wrapper


class VariableOverlapError(Exception):
    def __init__(self, instance, other, operation): 
        super().__init__('{}.{}({})'.format(repr(instance), operation, repr(other)))

class VariableOperationError(Exception):
    def __init__(self, instance, operation):
        super().__init__('{}.{}()'.format(repr(instance), operation))    

class VariableOperationNotSupportedError(Exception): 
    def __init__(self, spec, operation): super().__init__('{}.{}()'.format(repr(spec), operation))

class VariableNotCreatedError(Exception): pass


# DEEPCOPY ? ##
#def create_customvariable(spec):
#    variable = CustomVariable.subclasses()[spec.datatype]
#    variable.spec = spec
#    return variable    


class CustomVariable(ABC):
    def __new__(cls, *args, **kwargs):
        if cls == CustomVariable: raise VariableNotCreatedError()
        cls.add, cls.subtract = sametype(cls.add), sametype(cls.subtract)
        cls.multiply, cls.divide = sametype(cls.multiply), sametype(cls.divide)
        return super().__new__(cls)
   
    @classmethod
    def subclasses(cls): return {subclass.variabletype:subclass for subclass in CustomVariable.__subclasses__()}
    
    @abstractmethod
    def variabletype(self): pass
    
    @property
    def name(self): return '_'.join([uppercase(self.spec.data, index=0, withops=True), self.__class__.__name__])
    
    def __init__(self, value):
        self.spec.checkval(value)
        self.__value = value
        
    @classmethod
    def fromstr(cls, varstr): return cls(cls.spec.asval(varstr))
    
    @property
    def value(self): return self.__value
    def __str__(self): return self.spec.asstr(self.__value)   
    def __repr__(self): return '{}({})'.format(self.__class__.__name__, self.value)

    # EQUALITY
    @sametype
    def __eq__(self, other): return self.value == other.value
    def __ne__(self, other): return not self.__eq__(other)

    # OPERATIONS       
    def __add__(self, other): return self.add(other)
    def __sub__(self, other): return self.subtract(other)
    def __mul__(self, other): return self.multiply(other)
    def __truediv__(self, other): return self.divide(other)
    
    def add(self, other, *args, **kwargs): raise VariableOperationNotSupportedError(self, 'add')  
    def subtract(self, other, *args, **kwargs): raise VariableOperationNotSupportedError(self, 'subtract') 
    def multiply(self, other, *args, **kwargs): raise VariableOperationNotSupportedError(self, 'multiply')
    def divide(self, other, *args, **kwargs): raise VariableOperationNotSupportedError(self, 'divide')
    
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    