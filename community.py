# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 2020
@name:   Community Object
@author: Jack Kirby Cook

"""

from collections import namedtuple as ntuple

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

COMMUNITY = {'race':Race_Histogram, 'education':Education_Histogram, 'lifestage':LifeStage_Histogram}
DELIMITER = '|'
SEPARATOR = '&'
CommunitySgmts = ntuple('CommunitySgmts', ' '.join(list(COMMUNITY.keys())))


@Variable.register('community')    
class Community: 
    fields = tuple(COMMUNITY.keys())
        

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        