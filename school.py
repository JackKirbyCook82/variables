# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 2020
@name:   School Object
@author: Jack Kirby Cook

"""

from collections import namedtuple as ntuple

from variables.variable import Variable

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['School']
__copyright__ = "Copyright 2020, Jack Kirby Cook"
__license__ = ""


_aslist = lambda items: [items] if not isinstance(items, (list, tuple)) else list(items)
_filterempty = lambda items: [item for item in _aslist(items) if item is not None]

SCHOOL = ('graduation_rate', 'reading_rate', 'math_rate', 'ap_enrollment', 'avgsat_score', 'avgact_score', 'student_density', 'inexperience_ratio')
DELIMITER = '|'
SchoolSgmts = ntuple('SchoolSgmts', ' '.join(SCHOOL))


@Variable.register('school')    
class School: 
    fields = SCHOOL
        
    def __init__(self, **kwargs): super().__init__(SchoolSgmts({field:int(kwargs[field]) if field in kwargs.keys() else None for field in self.fields}))
    def __hash__(self): return hash(str(self))
    def __len__(self): return len(_filterempty(self.value))
    def __str__(self): return DELIMITER.join(['{}={}'.format(key, str(value)) for key, value in self.items() if value is not None])
    def __repr__(self): return '{}({})'.format(self.__class__.__name__, ', '.join(['{key}={value}'.format(key=key, value=value) for key, value in self.todict().items() if value is not None]))
    
    def keys(self): return list(self.value.todict().keys())
    def values(self): return list(self.value.todict().values())
    def todict(self): return self.value._asdict()
    
    def __getitem__(self, key): return self.value.todict()[key]
    def __getattr__(self, attr): return getattr(self.value, attr)  

    @classmethod
    def fromstr(cls, schoolstr, **kwargs):
        return cls({item.split('=')[0]:item.split('=')[1] for item in schoolstr.split(DELIMITER)})




