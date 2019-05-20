# -*- coding: utf-8 -*-
"""
Created on Sat Apr 7 2018
@name:   Date Objects
@author: Jack Kirby Cook

"""

from abc import ABC
from datetime import datetime, date
import time

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Datetime', 'Date']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


_DATEATTRS = {'date':('year', 'month', 'day'), 'datetime':('year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond')}
_DATEFORMATS = {'date':'%Y-%m-%d', 'datetime':'%Y-%m-%d %H:%M:%S'}
    

class DateBase(ABC):
    @classmethod
    def dateattrs(cls): return _DATEATTRS[cls.datetype()]
    @classmethod
    def datetype(cls): return cls.__name__.lower()
    
    @property
    def dateformat(self): return self.__dateformat
    
    def __init__(self, *args, **kwargs): self.setformat(kwargs.get('dateformat', _DATEFORMATS[self.datetype()]))
    def setformat(self, dateformat): self.__dateformat = dateformat
    def __str__(self): return self.strftime(self.dateformat)  
    def __repr__(self): return '{}({})'.format(self.__class__.__name__,  ', '.join(['='.join([attr, str(getattr(self, attr))]) for attr in self.dateattrs()])) 
       
    @classmethod
    def frominstance(cls, instance): return cls(**{attr:getattr(instance, attr) for attr in cls.dateattrs()})    
    @classmethod
    def fromstr(cls, datestr, **kwargs): return cls.frominstance(datetime.strptime(datestr, kwargs.get('dateformat', _DATEFORMATS[cls.datetype()])))  


class Datetime(DateBase, datetime):
    def __new__(cls, *args, year, month=1, day=1, hour=0, minute=0, second=0, microsecond=0, **kwargs):
        return super().__new__(cls, int(year), int(month), int(day), hour=int(hour), minute=int(minute), second=int(second), microsecond=int(microsecond))

    @property
    def timestamp(self): return int(time.mktime(self.timetuple()))     
    @classmethod
    def fromtimestamp(cls, timestamp): return cls.frominstance(datetime.fromtimestamp(int(timestamp)))      
    

class Date(DateBase, date):
    def __new__(cls, *args, year, month=1, day=1, **kwargs): 
        return super().__new__(cls, int(year), int(month), int(day))
    

    