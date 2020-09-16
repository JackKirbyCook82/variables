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


class Datetime(Variable, datatype='datetime'):  
    fields = DATE   

    def __init__(self, value): 
        try: super().__init__(date(value.year, value.month, value.day, value.hour, value.minute, value.second))
        except AttributeError: 
            try: 
                datesegments = [int(x) for x in str(value).split('T')[0].split('-')]
                timesegments = [int(x) for x in str(value).split('T')[1].split('+')[0].split(':')]
                super().__init__(date(*datesegments, **{key:value for key, value in zip(('hour', 'minute', 'second'), timesegments)}))
            except: super().__init__(value)
        self.setformat(DATETIMEFORMAT)
    
    def checkvalue(self, value):
        if not isinstance(value, datetime): raise ValueError(value)
    def fixvalue(self, value):
        if isinstance(value, date): return datetime(value.year, value.month, value.day)    
        elif isinstance(value, dict): return datetime(int(value['year']), int(value.get('month', 1)), int(value.get('day', 1)), hour=int(value.get('hour', 0)), minute=int(value.get('minute', 0)), second=int(value.get('second', 0)))
        else: return value
       
    def __str__(self): return self.strftime(self.dateformat)  
    def __repr__(self): return '{}({})'.format(self.__class__.__name__,  ', '.join(['='.join([attr, str(getattr(self, attr))]) for attr in self.fields])) 
    def __getattr__(self, attr): return getattr(self.value, attr)  
    
    @property
    def timestamp(self): return int(time.mktime(self.timetuple()))     
    @classmethod
    def fromtimestamp(cls, timestamp): return cls(datetime.fromtimestamp(int(timestamp)))   
    
    @property
    def index(self): return self.timestamp
    @classmethod
    def fromindex(cls, index): return cls.fromtimestamp(index)
    
    @property
    def dateformat(self): return self.__dateformat    
    def setformat(self, dateformat): self.__dateformat = dateformat
 
    def __add__(self, other):  
        assert isinstance(other, Timedelta)
        return self.__class__(self.value + other.value)
    def __sub__(self, other):
        assert isinstance(other, Timedelta)
        return self.__class__(self.value - other.value)
    
    @classmethod
    def fromnow(cls): return cls(datetime.now())    
    @classmethod
    def fromstr(cls, datetimestr, **kwargs): 
        datefmt = kwargs.get('dateformat', DATETIMEFORMAT)
        if '.' in datefmt:
            try: return cls(datetime.strptime(datetimestr, datefmt))  
            except ValueError: datefmt = datefmt.rpartition('.')[0]   
        while '-' in datefmt:
            try: return cls(datetime.strptime(datetimestr, datefmt))   
            except ValueError: datefmt = datefmt.rpartition('-')[0]  
        try: return cls(datetime.strptime(datetimestr, datefmt))    
        except: raise ValueError(datetimestr)   
    

class Date(Variable, datatype='date'):
    fields = DATE    
    
    def __init__(self, value): 
        try: super().__init__(date(value.year, value.month, value.day))
        except AttributeError: 
            try: super().__init__(date(*[int(x) for x in str(value).split('T')[0].split('-')]))
            except: super().__init__(value)
        self.setformat(DATEFORMAT)

    def checkvalue(self, value):
        if not isinstance(value, date): raise ValueError(value)
    def fixvalue(self, value):
        if isinstance(value, datetime): return date(value.year, value.month, value.day)        
        elif isinstance(value, dict): return date(int(value['year']), int(value.get('month', 1)), int(value.get('day', 1)))
        else: return value
    
    def __str__(self): return self.strftime(self.dateformat)  
    def __repr__(self): return '{}({})'.format(self.__class__.__name__,  ', '.join(['='.join([attr, str(getattr(self, attr))]) for attr in self.fields])) 
    def __getattr__(self, attr): return getattr(self.value, attr)  

    @property
    def timestamp(self): return int(time.mktime(self.timetuple()))     
    @classmethod
    def fromtimestamp(cls, timestamp): return cls(datetime.fromtimestamp(int(timestamp)))   
    
    @property
    def index(self): return self.timestamp
    @classmethod
    def fromindex(cls, index): return cls.fromtimestamp(index)
    
    @property
    def dateformat(self): return self.__dateformat
    def setformat(self, dateformat): self.__dateformat = dateformat
    
    def add(self, *args, years=0, months=0, days=0, **kwargs): return self.__class__(self.value + timedelta(days + (months/12) * 365 + years * 365))
    def sub(self, *args, years, months, days, **kwargs): return self.__class__(self.value - timedelta(days + (months/12) * 365 + years * 365))
    
    @classmethod
    def fromnow(cls): return cls(datetime.now())    
    @classmethod
    def fromstr(cls, datestr, **kwargs): 
        datefmt = kwargs.get('dateformat', DATEFORMAT)
        while '-' in datefmt:
            try: return cls(datetime.strptime(datestr, datefmt))   
            except ValueError: datefmt = datefmt.rpartition('-')[0]       
        try: return cls(datetime.strptime(datestr, datefmt))    
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

    
class Timedelta(Variable, datatype='timedelta'):  
    fields = TIMEDELTA

    def __init__(self, value): 
        try: super().__init__(timedelta(seconds=value.total_seconds()))
        except AttributeError: 
            try: super().__init__(timedelta(seconds=value.item().total_seconds()))
            except AttributeError: super().__init__(value)

    def checkvalue(self, value):
        if not isinstance(value, date): raise ValueError(value)
    def fixvalue(self, value):
        if isinstance(value, dict): return timedelta(days=int(value.get('days', 0)), hours=int(value.get('hours', 0)), minutes=int(value.get('minutes', 0)), seconds=int(value.get('seconds', 0)))
        else: return value
    
    def __str__(self): return TIMEDELTAFORMAT.format(**split_seconds(self.total_seconds())).lstrip()
    def __repr__(self): return '{}({})'.format(self.__class__.__name__,  ', '.join(['='.join([attr, str(getattr(self, attr))]) for attr in self.fields])) 
    def __getattr__(self, attr): return getattr(self.value, attr)  
    
    def __add__(self, other):
        assert isinstance(other, type(self))
        return self.__class__(self.value + other.value)
    def __sub__(self, other):
        assert isinstance(other, type(self))
        return self.__class__(self.value - other.value)
    
    def __mul__(self, factor):
        assert isinstance(factor, (int, float))
        return self.__class__(self.value * factor)
    def __truediv__(self, factor): 
        assert isinstance(factor, (int, float))
        return self.__class__(self.value / factor)
    
    def total(self, key): return compile_seconds(self.total_seconds(), key)
    
    @classmethod    
    def fromseconds(cls, seconds): return cls({split_seconds(seconds)})
    @classmethod
    def fromstr(cls, timedeltastr, **kwargs): return cls({**parse(TIMEDELTAFORMAT, timedeltastr).named})  





