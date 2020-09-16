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


class VariableNotCreatedError(Exception): pass     
class VariableOverlapError(Exception):
    def __init__(self, instance, other, operation): 
        super().__init__('{}.{}({})'.format(repr(instance), operation, repr(other))) 
        

class Variable(ABC):
    def __init_subclass__(cls, *args, datatype, **kwargs):
        setattr(cls, 'datatype', datatype.lower())
        VARIABLES[datatype.lower()] = cls
    
    def __init__(self, value): 
        try: self.checkvalue(value)
        except ValueError: value = self.fixvalue(value)
        self.checkvalue(value)
        self.__value = value   

    @abstractmethod
    def checkvalue(self, value): pass
    @abstractmethod
    def fixvalue(self, value): pass

    @classmethod
    def name(cls): return '_'.join([cls.__name__, 'Variable'])
    @property
    def value(self): return self.__value    
    @property
    def index(self): return self.__value    
    @classmethod
    def jsonstr(cls): return json.dumps(dict(data=cls.datatype), sort_keys=True, indent=3, separators=(',', ' : '), default=str)       
        
    @abstractmethod
    def __repr__(self): pass    
    @abstractmethod
    def __str__(self): pass    

    def __hash__(self): return hash((hash(self.__class__), self.index,))
    def __ne__(self, other): return not self.__eq__(other)
    def __eq__(self, other): 
        if type(self) != type(other): raise TypeError(type(other))        
        return self.index == other.index      
    def __lt__(self, other): 
        if type(self) != type(other): raise TypeError(type(other))   
        return self.index < other.index
    def __gt__(self, other): 
        if type(self) != type(other): raise TypeError(type(other))   
        return self.index > other.index        
    def __le__(self, other): 
        if type(self) != type(other): raise TypeError(type(other))   
        return self.index <= other.index
    def __ge__(self, other): 
        if type(self) != type(other): raise TypeError(type(other))   
        return self.index >= other.index

    @classmethod
    def fromindex(cls, index): return cls(index)
    @classmethod
    def fromvalue(cls, value): return cls(value)
    @abstractmethod
    def fromstr(self): pass        
    @classmethod
    def fromall(cls): raise NotImplementedError('{}.{}()'.format(cls.__name__, 'fromall'))

 
class CustomVariable(ABC):
    def __init_subclass__(cls, *args, datatype, **kwargs):
        setattr(cls, 'datatype', datatype.lower())
        CUSTOM_VARIABLES[datatype.lower()] = cls

    def __new__(cls, *args, **kwargs):
        if cls == CustomVariable: raise VariableNotCreatedError()
        if not hasattr(cls, 'spec'): raise VariableNotCreatedError()
        return super().__new__(cls)   

    def __init__(self, value): 
        try: self.checkvalue(value)
        except ValueError: value = self.fixvalue(value)
        self.checkvalue(value)
        self.__value = value   

    @abstractmethod
    def checkvalue(self, value): pass
    @abstractmethod
    def fixvalue(self, value): pass
    
    @classmethod
    def name(cls): return '_'.join([cls.__name__, 'Variable'])
    @property
    def value(self): return self.__value    
    @property
    def index(self): return self.__value    
    @classmethod
    def jsonstr(cls): return cls.spec.jsonstr()         
    
    def __repr__(self): return '{}({})'.format(self.__class__.__name__, self.value) 
    def __str__(self): return self.spec.asstr(self.value)  
 
    def __hash__(self): return hash((hash(self.spec), self.index,))
    def __ne__(self, other): return not self.__eq__(other)
    def __eq__(self, other): 
        if self.spec != other.spec: raise TypeError(type(other))        
        return self.index == other.index      
    def __lt__(self, other): 
        if self.spec != other.spec: raise TypeError(type(other))      
        return self.index < other.index
    def __gt__(self, other): 
        if self.spec != other.spec: raise TypeError(type(other))        
        return self.index > other.index        
    def __le__(self, other): 
        if self.spec != other.spec: raise TypeError(type(other))     
        return self.index <= other.index
    def __ge__(self, other): 
        if self.spec != other.spec: raise TypeError(type(other))     
        return self.index >= other.index
          
    @classmethod
    def fromindex(cls, index): return cls(index)
    @classmethod
    def fromvalue(cls, value): return cls(value)
    @classmethod
    def fromstr(cls, varstr): return cls(cls.spec.asval(varstr))          
    @classmethod
    def fromall(cls): raise NotImplementedError('{}.{}()'.format(cls.__name__, 'fromall'))
    
    @classmethod
    def operation(cls, other, *args, method, **kwargs): 
        try: return create_customvariable(getattr(cls.spec, method)(other.spec, *args, **kwargs))
        except AttributeError: return create_customvariable(cls.spec.operation(other.spec, *args, method=method, **kwargs))
    @classmethod
    def transformation(cls, *args, method, how, **kwargs): 
        try: return create_customvariable(getattr(cls.spec, method)(*args, how=how, **kwargs))
        except AttributeError: return create_customvariable(cls.spec.transformation(*args, method=method, how=how, **kwargs))    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
