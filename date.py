# -*- coding: utf-8 -*-
"""
Created on Sat Apr 7 2018
@name:   Date Objects
@author: Jack Kirby Cook

"""

from datetime import datetime, date
import time

from variables.variable import Variable

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Datetime', 'Date']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


DATE = ('year', 'month', 'day')
DATEFORMAT = '%Y-%m-%d'
DATETIME = ('year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond')
DATETIMEFORMAT = '%Y-%m-%d %H:%M:%S.%f'


@Variable.register('datetime')
class Datetime:  
    fields = DATE
    
    def __init__(self, *args, year, month=1, day=1, hour=0, minute=0, second=0, microsecond=0, **kwargs):
        instance = datetime(int(year), int(month), int(day), hour=int(hour), minute=int(minute), second=int(second), microsecond=int(microsecond))
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
    
    @classmethod
    def fromnow(cls): return cls.frominstance(datetime.now())    
    @classmethod
    def frominstance(cls, instance, *args, **kwargs): return cls(*args, **{attr:getattr(instance, attr) for attr in cls.fields}, **kwargs)    
    @classmethod
    def fromstr(cls, datestr, **kwargs): 
        datefmt = kwargs.get('dateformat', DATEFORMAT)
        if '.' in datefmt:
            try: return cls.frominstance(datetime.strptime(datestr, datefmt), dateformat=datefmt)  
            except ValueError: datefmt = datefmt.rpartition('.')[0]   
        while '-' in datefmt:
            try: return cls.frominstance(datetime.strptime(datestr, datefmt), dateformat=datefmt)   
            except ValueError: datefmt = datefmt.rpartition('-')[0]  
        try: return cls.frominstance(datetime.strptime(datestr, datefmt), dateformat=datefmt)    
        except: raise ValueError(datestr)      
    

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
    
    
    










