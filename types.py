# -*- coding: utf-8 -*-
"""
Created on Thurs Jun 6 2019
@name:   Category Objects
@author: Jack Kirby Cook

"""

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Category']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


_DELIMITER = ' & '

def sametype(function):
    def wrapper(self, other):
        if type(self) != type(other): raise TypeError(' != '.join([str(type(self)), str(type(other))]))
        return function(self, other)
    return wrapper


class CategoryOverlapError(Exception):
    def __init__(self, instance, other, operation): 
        super().__init__('{}.{}({})'.format(repr(instance), operation, repr(other)))


class Category(object):
    delimiter = _DELIMITER
    
    @property
    def values(self): return self.__values
    
    def __init__(self, *args):
        assert len(set(args)) == len(args)
        self.__values = list(args)
        
    def __str__(self): return self.delimiter.join(list(self.values))
    def __add__(self, other): return self.add(other)
    def __sub__(self, other): return self.subtract(other)
    
    @sametype
    def add(self, other, *args, **kwargs): 
        if any([item in self.values for item in other.values]): raise CategoryOverlapError(self, other, 'add')
        return self.__class__([*self.value, *other.value])  
    @sametype
    def subtract(self, other, *args, **kwargs): 
        if any([item not in self.values for item in other.values]): raise CategoryOverlapError(self, other, 'sub')
        return self.__class__([value for value in self.values if value not in other.values]) 
    
    @classmethod
    def fromstr(cls, catstr, **kwargs):
        return cls(*catstr.split(cls.delimiter))

















