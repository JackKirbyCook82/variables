# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 2020
@name:   Community Object
@author: Jack Kirby Cook

"""

from specs import HistogramSpec

from variables.variable import Variable, create_customvariable

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Community']
__copyright__ = "Copyright 2020, Jack Kirby Cook"
__license__ = ""


_aslist = lambda items: [items] if not isinstance(items, (list, tuple)) else list(items)
_filterempty = lambda items: [item for item in _aslist(items) if item is not None]

Race_Histogram = create_customvariable(HistogramSpec(data='race', categories=['White', 'Black', 'Native', 'Asian', 'Islander', 'Other', 'Mix']))
Education_Histogram = create_customvariable(HistogramSpec(data='education', categories=['Uneducated', 'GradeSchool', 'Associates', 'Bachelors', 'Graduate']))
LifeStage_Histogram = create_customvariable(HistogramSpec(data='lifestage', categories=['Baby', 'Toddler', 'Child', 'Teenager', 'YoungAdult', 'MidLife', 'Mature', 'Elder']))

_COMMUNITY = {'race':Race_Histogram, 'education':Education_Histogram, 'lifestage':LifeStage_Histogram}


@Variable.register('community')
class Community:
    fields = tuple(_COMMUNITY.keys())
    delimiter = '&'    
    
    def __init__(self, **kwargs): super().__init__([kwargs[attr] if attr in kwargs.keys() else None for attr in self.fields.keys()])
    def __getattr__(self, attr): return self.value[list(self.fields.keys()).index(attr)]
    def __getitem__(self, attr): return self.value[list(self.fields.keys()).index(attr)]
    
    def __len__(self): return len(_filterempty(self.value))
    def __repr__(self): return '{}({})'.format(self.__class__.__name__,  ', '.join(['{}={}'.format(attr, repr(item)) for attr, item in self.items()]))
    def __str__(self): return self.delimiter.join([str(item) if item is not None else '' for item in self.value])
    
    def items(self): return zip(self.fields.keys(), self.value)
    def asdict(self): return {key:value for key, value in self.items()}
    
    @classmethod
    def fromstr(cls, communitystr, **kwargs): 
        communitystrs = communitystr.split(cls.delimiter)
        return cls({attr:variable.fromstr(communitystrs[i]) for i, (attr, variable) in enumerate(cls.fields.items()) if communitystrs[i]})

        
        
     
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        