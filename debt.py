# -*- coding: utf-8 -*-
"""
Created on Thurs Feb 27 2020
@name:   Debt Object
@author: Jack Kirby Cook

"""

from collections import namedtuple as ntuple
from parse import parse

from utilities.strings import uppercase

from variables.variable import Variable

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Debt']
__copyright__ = "Copyright 2020, Jack Kirby Cook"
__license__ = ""


_aslist = lambda items: [items] if not isinstance(items, (list, tuple)) else list(items)
_filterempty = lambda items: [item for item in _aslist(items) if item is not None]

DEBT = ('name', 'startyear', 'startbalance', 'yearlyterm', 'yearlyrate')
FORMAT = '{name} | ${startbalance} for {yearlyterm} YRS @ {yearlyrate} %/YR in {startyear}'
DebtSgmts = ntuple('DebtSgmts', ' '.join(DEBT))


def monthly_rate(yearlyrate):
    return pow(1 + yearlyrate, 12) - 1

def current_balance(startbalance, monthlyrate, monthlyterm, monthlyperiod):
    return startbalance * (pow(1 + monthlyrate, monthlyterm) - pow(1 + monthlyrate, monthlyperiod) / (pow(1 + monthlyrate, monthlyterm) - 1))


@Variable.register('debt')    
class Debt: 
    fields = DEBT
    
    def __init__(self, *args, name='debt', startyear, startbalance, yearlyterm, yearlyrate, **kwargs): 
        super().__init__(DebtSgmts(str(name), int(startyear), int(startbalance), int(yearlyterm), float(yearlyrate)))

    def __call__(self, currentyear):
        period = (currentyear - self.startyear) * 12
        periodrate = monthly_rate(self.yearlyrate)
        periodterm = self.yearlyterm * 12
        periodbalance = current_balance(self.startbalance, periodrate, periodterm, period)
        newyearlyterm = periodterm - period
        return self.__class__(name=self.name, startyear=currentyear, startbalance=periodbalance, yearlyterm=newyearlyterm, yearlyrate=self.yearlyrate)
       
    def __str__(self): 
        items = self.value._asdict()
        name = uppercase(items.pop('name'))
        return FORMAT.format(name=name, **items)
    
    def __repr__(self): 
        fmt = '{}(name={}, startyear={}, startamount={}, yearlyterm={}, yearlyrate={})'
        return fmt.format(self.__class__.__name__, self.name, self.startyear, self.startbalance, self.yearlyterm, self.yearlyrate)

    def __getitem__(self, key): return self.value.todict()[key]
    def __getattr__(self, attr): return getattr(self.value, attr)  

    def keys(self): return list(self.value.todict().keys())
    def values(self): return list(self.value.todict().values())
    def todict(self): return self.value._asdict()

    @classmethod
    def fromstr(cls, debtstr, **kwargs):
        unformated = parse(FORMAT, debtstr)
        return cls(**unformated.named)


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    