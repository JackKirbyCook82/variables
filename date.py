# -*- coding: utf-8 -*-
"""
Created on Sat Apr 7 2018
@name:   Date Objects
@author: Jack Kirby Cook

"""

from datetime import datetime, date, timedelta
from parse import parse
import math
import time

from variables.variable import Variable

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Datetime', 'Date', 'Timedelta']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


DATE = ('year', 'month', 'day')
DATEFORMAT = '%Y-%m-%d'
DATETIME = ('year', 'month', 'day', 'hour', 'minute', 'second')
DATETIMEFORMAT = '%Y-%m-%d %H:%M:%S.%f'
TIMEDELTA = ('days', 'hours', 'minutes', 'seconds')
TIMEDELTAFORMAT = '{days} {hours}:{minutes}:{seconds}'


@Variable.register('datetime')
class Datetime:  
    fields = DATE   
    def __init__(self, *args, year, month=1, day=1, hour=0, minute=0, second=0, **kwargs):
        instance = datetime(int(year), int(month), int(day), hour=int(hour), minute=int(minute), second=int(second))
        self.setformat(kwargs.get('dateformat', DATEFORMAT))
        super().__init__(instance)
        
    def __str__(self): return self.strftime(self.dateformat)  
    def __repr__(self): return '{}({})'.format(self.__class__.__name__,  ', '.join(['='.join([attr, str(getattr(self, attr))]) for attr in self.fields])) 
    def __getattr__(self, attr): return getattr(self.value, attr)  
    
    @property
    def timestamp(self): return int(time.mktime(self.timetuple()))     
    @classmethod
    def fromtimestamp(cls, timestamp): return cls.frominstance(datetime.fromtimestamp(int(timestamp)))   
    
    @property
    def dateformat(self): return self.__dateformat    
    def setformat(self, dateformat): self.__dateformat = dateformat
 
    def __add__(self, other):
        assert isinstance(other, Timedelta)
        return self.frominstance(self.value + other.value)
    def __sub__(self, other):
        assert isinstance(other, Timedelta)
        return self.frominstance(self.value - other.value)
    
    @classmethod
    def fromnow(cls): return cls.frominstance(datetime.now())    
    @classmethod
    def frominstance(cls, instance, *args, **kwargs): return cls(*args, **{attr:getattr(instance, attr) for attr in cls.fields}, **kwargs)    
    @classmethod
    def fromstr(cls, datetimestr, **kwargs): 
        datefmt = kwargs.get('dateformat', DATEFORMAT)
        if '.' in datefmt:
            try: return cls.frominstance(datetime.strptime(datetimestr, datefmt), dateformat=datefmt)  
            except ValueError: datefmt = datefmt.rpartition('.')[0]   
        while '-' in datefmt:
            try: return cls.frominstance(datetime.strptime(datetimestr, datefmt), dateformat=datefmt)   
            except ValueError: datefmt = datefmt.rpartition('-')[0]  
        try: return cls.frominstance(datetime.strptime(datetimestr, datefmt), dateformat=datefmt)    
        except: raise ValueError(datetimestr)      
    

@Variable.register('date')
class Date:
    fields = DATETIME    
    def __init__(self, *args, year, month=1, day=1, **kwargs): 
        instance = date(int(year), int(month), int(day))
        self.setformat(kwargs.get('dateformat', DATETIME))
        super().__init__(instance)
    
    def __str__(self): return self.strftime(self.dateformat)  
    def __repr__(self): return '{}({})'.format(self.__class__.__name__,  ', '.join(['='.join([attr, str(getattr(self, attr))]) for attr in self.fields])) 
    def __getattr__(self, attr): return getattr(self.value, attr)  
    
    @property
    def dateformat(self): return self.__dateformat
    def setformat(self, dateformat): self.__dateformat = dateformat
    
    def __add__(self, other):
        assert isinstance(other, Timedelta)
        return self.frominstance(self.value + other.value)
    def __sub__(self, other):
        assert isinstance(other, Timedelta)
        return self.frominstance(self.value - other.value)
    
    @classmethod
    def fromnow(cls): return cls.frominstance(datetime.now())    
    @classmethod
    def frominstance(cls, instance, *args, **kwargs): return cls(*args, **{attr:getattr(instance, attr) for attr in cls.fields}, **kwargs)    
    @classmethod
    def fromstr(cls, datestr, **kwargs): 
        datefmt = kwargs.get('dateformat', DATETIME)
        while '-' in datefmt:
            try: return cls.frominstance(datetime.strptime(datestr, datefmt), dateformat=datefmt)   
            except ValueError: datefmt = datefmt.rpartition('-')[0]       
        try: return cls.frominstance(datetime.strptime(datestr, datefmt), dateformat=datefmt)    
        except: raise ValueError(datestr)    
  
    
def split_seconds(seconds):
    function = lambda x, divisor: (math.modf(x/divisor)[0], math.modf(x/divisor)[1]*divisor)       
    minutes, seconds = function(seconds, 60)
    hours, minutes = function(minutes, 60)
    days, hours = function(hours, 24)   
    return dict(days=days, hours=hours, minutes=minutes, seconds=seconds)     

def compile_seconds(seconds, key):
    conversions = {'days':lambda x: x/(60*60*24), 'hours':lambda x: x/(60*60), 'minutes':lambda x: x/60, 'seconds':lambda x: x}
    return conversions[key](seconds)

    
@Variable.register('timedelta')
class Timedelta:  
    fields = DATE
    def __init__(self, *args, days=0, hours=0, minutes=0, seconds=0, **kwargs):
        instance = timedelta(days=int(days), hours=int(hours), minutes=int(minutes), seconds=int(seconds))
        self.setformat(kwargs.get('dateformat', DATEFORMAT))
        super().__init__(instance)     
        
    def __str__(self): return TIMEDELTAFORMAT.format(**split_seconds(self.total_seconds())).lstrip()
    def __repr__(self): return '{}({})'.format(self.__class__.__name__,  ', '.join(['='.join([attr, str(getattr(self, attr))]) for attr in self.fields])) 
    def __getattr__(self, attr): return getattr(self.value, attr)  
   
    def __add__(self, other):
        assert isinstance(other, type(self))
        return self.frominstance(self.value + other.value)
    def __sub__(self, other):
        assert isinstance(other, type(self))
        return self.frominstance(self.value - other.value)
    
    def __mul__(self, factor):
        assert isinstance(factor, (int, float))
        return self.frominstance(self.value * factor)
    def __truediv__(self, factor): 
        assert isinstance(factor, (int, float))
        return self.frominstance(self.value / factor)
    
    def total(self, key): return compile_seconds(self.total_seconds(), key)
    
    @classmethod    
    def fromseconds(cls, seconds, *args, **kwargs): return cls(*args, **split_seconds(seconds), **kwargs)
    @classmethod
    def frominstance(cls, instance, *args, **kwargs): return cls(*args, **split_seconds(instance.total_seconds()), **kwargs)    
    @classmethod
    def fromstr(cls, timedeltastr, **kwargs): return cls(**parse(TIMEDELTAFORMAT, timedeltastr)   .named)  






















