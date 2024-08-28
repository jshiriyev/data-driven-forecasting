from dataclasses import dataclass, fields

import datetime

import numpy

import pandas

@dataclass
class ProdData:
    """It is a Production  dictionary for a perf in a well."""

    date    : datetime.date = None

    well    : str = None

    horizon : str = None

    days    : int = None

    optype  : str = "production"

    roil    : float = None
    rwater  : float = None
    rgas    : float = None

    toil    : float = None
    twater  : float = None
    tgas    : float = None

    @staticmethod
    def fields() -> list:
        return [field.name for field in fields(ProdData)]

class Production():
    
    def __init__(self,frame:pandas.DataFrame=None,mapping:dict=None):
        """
        Initialize the class with a DataFrame and a column mapping.

        Parameters:

        frame (pd.DataFrame)    : The input DataFrame.

        mapping (dict)          : A dictionary mapping class properties
                                to DataFrame columns.
        """
        self.frame,self.mapping = frame,mapping

        self.validate_mapping()

    @property
    def frame(self):
        return self._frame

    @frame.setter
    def frame(self,value:pandas.DataFrame):
        self._frame = pandas.DataFrame(columns=ProdData.fields()) if value is None else value

    @property
    def mapping(self):
        return self._mapping

    @mapping.setter
    def mapping(self,value:dict):
        self._mapping = {key:key for key in ProdData.fields()} if value is None else value

    def validate_mapping(self):

        wrong_keys = [key for key in self.mapping.keys() if key not in ProdData.fields()]

        if wrong_keys:
            raise ValueError(f"Mapping keys are: {', '.join(ProdData.fields())}")

    def __getattr__(self,key):

        if key in ProdData.fields():

            if key.startswith("t") and key not in self.mapping.keys():
                return numpy.nancumsum(self.frame[self.mapping["r"+key[1:]]])

            return self.frame[self.mapping[key]]

        return getattr(self.frame,key)

    def __getitem__(self,key):

        if isinstance(key,int):

            row = self.frame.iloc[key].to_dict()

            return ProdData(**{key:row.get(value) for key,value in self.mapping.items()})

        return getitem(self.frame,key)

if __name__ == "__main__":

    frame = pandas.DataFrame(dict(
        A=[datetime.date(2020,1,1),datetime.date(2021,1,1),datetime.date(2022,1,1),datetime.date(2023,1,1)],
        B=[31,30,28,15],
        C=['production','injection','production','production'],
        D=[256,569,32,15.]))

    prods = Production(frame,dict(date='A',days='B',optype='C',roil='D'))

    print(prods.toil)