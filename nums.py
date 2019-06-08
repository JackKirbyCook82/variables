# -*- coding: utf-8 -*-
"""
Created on Thurs Jun 6 2019
@name:   NumRange Objects
@author: Jack Kirby Cook

"""

import re

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Num', 'Range']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


_DELIMITER = ' - '

_fixnumtype = lambda num: None if num is None else int(float(num)) if not bool(float(num) % 1) else float(num)

def _numfromstr(numstr): 
    nums = re.findall(r"[-+]?\d*\.\d+|\d+", numstr)
    if len(nums) == 0: yield None
    elif len(nums) == 1: yield _fixnumtype(nums[0])
    else: 
        for num in nums: yield _fixnumtype(num)


def sametype(function):
    def wrapper(self, other):
        if type(self) != type(other): raise TypeError(' != '.join([str(type(self)), str(type(other))]))
        return function(self, other)
    return wrapper


class RangeOverlapError(Exception):
    def __init__(self, instance, other, operation): 
        super().__init__('{}.{}({})'.format(repr(instance), operation, repr(other)))


class RangeOperationError(Exception):
    def __init__(self, instance, operation):
        super().__init__('{}.{}()'.format(repr(instance), operation))        


class Num(object):
    def __init__(self, value): 
        assert isinstance(value, (int, float))
        self.__value = value
        
    @property
    def value(self): return self.value

    def __str__(self): return str(self.value)
    def __add__(self, other): return self.add(other)
    def __sub__(self, other): return self.subtract(other)
    
    @sametype
    def add(self, other, *args, **kwargs): return self.__class__(self.value + other.value)   
    @sametype    
    def subtract(self, other, *args, **kwargs): return self.__class__(self.value - other.value)
    
    @classmethod
    def fromstr(cls, numstr, **kwargs):
        nums = [num for num in _numfromstr(numstr)]
        assert len(nums) == 1
        assert isinstance(nums[0], (int, float))
        return cls(nums[0])
        

class Range(object):
    delimiter = _DELIMITER
    headings = {'upper':'>', 'lower':'<', 'center':'', 'state':'', 'unbounded':'...'} 
 
    @property
    def lower(self): return self.__lower
    @property
    def upper(self): return self.__upper
    @property
    def values(self): return [self.lower, self.upper]
    
    @property
    def heading(self):
        return self.headings[self.direction]
    
    @property
    def direction(self):  
        if all([x is None for x in (self.lower, self.upper)]): return 'unbounded'
        elif self.lower is None: return 'lower'
        elif self.upper is None: return 'upper'
        elif self.lower == self.upper: return 'state'
        else: return 'center'         
    
    def __init__(self, lower, upper): 
        assert all([isinstance(value, (int, float, type(None))) for value in (lower, upper)])
        self.__lower, self.__upper = lower, upper

    def __str__(self): return self.headings[self.direction] + self.delimiter.join([str(value) for value in self.values if value is not None])
    def __add__(self, other): return self.add(other)
    def __sub__(self, other): return self.subtract(other)

    @sametype
    def add(self, other, *args, **kwargs):
        if all([self.lower == other.upper, self.lower is not None, other.upper is not None]): values = [other.lower, self.upper]
        elif all([self.upper == other.lower, self.upper is not None, other.lower is not None]): values = [self.lower, other.upper]
        else: raise RangeOverlapError(self, other, 'add')
        return self.__class__(*values)

    @sametype    
    def subtract(self, other, *args, **kwargs):
        if other.lower == other.upper: raise RangeOverlapError(self, other, 'sub')
        if self.lower == other.lower: 
            if other.upper is None: raise RangeOverlapError(self, other, 'sub')
            else: 
                if other.upper > self.upper: raise RangeOverlapError(self, other, 'sub')
                else: values = [other.upper, self.upper]
        elif self.upper == other.upper: 
            if other.lower is None: raise RangeOverlapError(self, other, 'sub')
            else: 
                if other.lower < self.lower: raise RangeOverlapError(self, other, 'sub')
                else: values = [self.lower, other.lower]
        else: raise RangeOverlapError(self, other, 'sub')
        return self.__class__(*values)
    
    def average(self, *args, wieght=0.5, **kwargs): 
        assert all([wieght >= 0, wieght <= 1]) 
        if self.direction != 'center' or self.direction != 'state': raise RangeOperationError(self, 'average')
        return wieght * self.lower + (1-wieght) * self.upper

    def cumulate(self, *args, **kwargs):
        if self.direction == 'lower': return self.upper
        elif self.direction == 'upper': return self.lower
        else: raise RangeOperationError(self, 'cumulative')

    @classmethod
    def fromstr(cls, rangestr, **kwargs):
        nums = [num for num in _numfromstr(rangestr)]
        if cls.headings['upper'] in rangestr: nums = [*nums, None]
        elif cls.headings['lower'] in rangestr: nums = [None, *nums]
        elif cls.headings['unbounded'] in rangestr: nums = [None, None]
        if len(nums) == 1: nums = [*nums, *nums]
        assert len(nums) == 2
        return cls(*nums)











