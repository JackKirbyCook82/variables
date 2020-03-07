# -*- coding: utf-8 -*-
"""
Created on Wed Mar 4 2020
@name:   Field Objects
@author: Jack Kirby Cook

"""

from collections import namedtuple as ntuple

from specs import HistogramSpec, RangeSpec
from parsers import FormatValueParser
from parsers.valuegenerators import RangeGenerator
from parsers.valueformatters import RangeFormatter

from variables.variable import Variable, create_customvariable

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Crime', 'School', 'Space', 'Proximity', 'Community']
__copyright__ = "Copyright 2020, Jack Kirby Cook"
__license__ = ""


SEPARATOR = ' & '
DELIMITER = '|'

rangegenerators = {'range':RangeGenerator(*'&-/')}
rangeformatters = {'range':RangeFormatter(DELIMITER)}
rangeparser = FormatValueParser(rangegenerators, rangeformatters, pattern=';|&=')

AgeRange = create_customvariable(RangeSpec(precision=0, unit='YRS'))
CommuteRange = create_customvariable(RangeSpec(precision=0, unit='MINS'))

RaceHistogram = create_customvariable(HistogramSpec(data='race', categories=['White', 'Black', 'Native', 'Asian', 'Islander', 'Other', 'Mix']))
OriginHistogram = create_customvariable(HistogramSpec(data='origin', categories=['NonHispanic', 'Hispanic']))
EducationHistogram = create_customvariable(HistogramSpec(data='education', categories=['Uneducated', 'GradeSchool', 'Associates', 'Bachelors', 'Graduate']))
LanguageHistogram = create_customvariable(HistogramSpec(data='language', categories=['English', 'Spanish', 'IndoEuro', 'Asian', 'Pacific', 'African', 'Native', 'Arabic', 'Other']))
EnglishHistogram = create_customvariable(HistogramSpec(data='english', categories=['Fluent', 'Well', 'Poor', 'Inable']))
ChildrenHistogram = create_customvariable(HistogramSpec(data='children', categories=['W/OChildren', 'WChildren']))
AgeHistogram = create_customvariable(HistogramSpec(data='age', categories=rangeparser('{} YRS|range|15-55/10&60&65-85/10|cut=lower&shift=upper'), 
                                                   function=lambda x, *args, bounds=[0, None], **kwargs: AgeRange.average(bounds=bounds).fromstr(x).value))
CommuteHistogram = create_customvariable(HistogramSpec(data='commute', categories=rangeparser('{} MINS|range|5-45/5&60&90|shift=upper'), 
                                                       function=lambda x, *args, bounds=[0, None], **kwargs: CommuteRange.average(bounds=bounds).fromstr(x).value))

CRIME = ('shooting', 'arson', 'burglary', 'assault', 'vandalism', 'robbery', 'arrest', 'other', 'theft')
SCHOOL = ('graduation_rate', 'reading_rate', 'math_rate', 'ap_enrollment', 'avgsat_score', 'avgact_score', 'student_density', 'inexperience_ratio')
SPACE = ('sqft', 'bedrooms', 'rooms')
PROXIMITY = {'commute':CommuteHistogram}
COMMUNITY = {'race':RaceHistogram, 'origin':OriginHistogram, 'education':EducationHistogram, 'language':LanguageHistogram, 'english':EnglishHistogram, 'age':AgeHistogram, 'children':ChildrenHistogram}

CrimeSgmts = ntuple('CrimeSgmts', ' '.join(CRIME))
SchoolSgmts = ntuple('SchoolSgmts', ' '.join(SCHOOL))
SpaceSgmts = ntuple('SpaceSgmts', ' '.join(SPACE))
ProximitySgmts = ntuple('ProximitySgmts', ' '.join(list(PROXIMITY.keys())))
CommunitySgmts = ntuple('CommunitySgmts', ' '.join(list(COMMUNITY.keys())))

_aslist = lambda items: [items] if not isinstance(items, (list, tuple)) else list(items)
_filterempty = lambda items: [item for item in _aslist(items) if item is not None]


@Variable.register('field')
class Field:
    def __init__(self, value): 
        assert all([hasattr(value, '_fields'), hasattr(value, 'todict'), isinstance(value, tuple)])
        super().__init__(value)
    
    def keys(self): return list(self.value.todict().keys())
    def values(self): return list(self.value.todict().values())
    def todict(self): return self.value._asdict()
    
    def __str__(self): return DELIMITER.join(['{}={}'.format(key, str(value)) for key, value in self.items() if value is not None])
    def __repr__(self): return '{}({})'.format(self.__class__.__name__, ', '.join(['{}={}'.format(key, value) for key, value in self.todict().items() if value is not None]))    
    def __len__(self): return len(_filterempty(self.value))
    def __getitem__(self, key): return self.value.todict()[key]
    def __getattr__(self, attr): return getattr(self.value, attr)     
    
    @classmethod
    def fromstr(cls, string, **kwargs):
        return cls({item.split('=')[0]:item.split('=')[1] for item in string.split(DELIMITER)})    


@Variable.register('histfield')
class HistField:
    def __init__(self, value): 
        assert all([hasattr(value, '_fields'), hasattr(value, 'todict'), isinstance(value, tuple)])
        super().__init__(value)
 
    def keys(self): return list(self.value.todict().keys())
    def values(self): return list(self.value.todict().values())
    def todict(self): return self.value._asdict()
    
    def __str__(self): return SEPARATOR.join(['{}={}'.format(key, str(value)) for key, value in self.todict().items()])
    def __repr__(self): return '{}({})'.format(self.__class__.__name__, ', '.join(['{}={}'.format(key, repr(value)) for key, value in self.todict().items()]))
    def __len__(self): return len(_filterempty(self.value))
    def __getitem__(self, key): return self.value.todict()[key]
    def __getattr__(self, attr): return getattr(self.value, attr)     
 
    @classmethod
    def fromstr(cls, string, **kwargs): 
        histograms = {item.split('=')[0]:item.split('=')[1] for item in string.split(SEPARATOR)}
        return cls({field:variable.fromstr(histograms[field]) for field, variable in cls.fields.items()})
                    

@Field.register('crime')    
class Crime: 
    fields = CRIME
    def __init__(self, **kwargs): 
        super().__init__(CrimeSgmts({field:int(kwargs.get(field, 0)) for field in self.fields}))

    
@Field.register('school')    
class School: 
    fields = SCHOOL        
    def __init__(self, **kwargs): 
        super().__init__(SchoolSgmts({field:int(kwargs[field]) if field in kwargs.keys() else None for field in self.fields}))


@Field.register('space')    
class Space: 
    fields = SPACE        
    def __init__(self, **kwargs): 
        super().__init__(SpaceSgmts({field:int(kwargs[field]) for field in self.fields}))
    

@HistField.register('proximity')    
class Proximity: 
    fields = PROXIMITY    
    def __init__(self, **kwargs): 
        assert all([isinstance(kwargs[field], variable) for field, variable in self.fields.items()])
        super().__init__(ProximitySgmts({field:kwargs[field] for field in self.fields}))
    

@HistField.register('community')    
class Community: 
    fields = COMMUNITY       
    def __init__(self, **kwargs): 
        assert all([isinstance(kwargs[field], variable) for field, variable in self.fields.items()])
        super().__init__(CommunitySgmts({field:kwargs[field] for field in self.fields}))
    































