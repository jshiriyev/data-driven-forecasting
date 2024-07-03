import datetime

import pandas

from ._frameutils import FrameUtils

class Template():

    _mindate = datetime.date(2020,1,1)
    _maxdate = datetime.date(2030,1,1)

    def __init__(self,frame:pandas.DataFrame):
        """The frame must contain leads on the first column, dates on the second
        column and numerical values on the remaining columns."""
        self.__utils = FrameUtils()

        self._frame = frame

    @property
    def frame(self):
        return self._frame

    @property
    def empty(self):
        return self._frame.empty

    @property
    def shape(self):
        return self._frame.shape

    @property
    def columns(self):
        return self._frame.columns.tolist()
    
    def __iter__(self):

        for item in self.unique:
            yield item,self.filter(item)

    @property
    def keys(self):
        """Returns the head of leads and dates."""
        return (self.leadhead,self.datehead)

    @property
    def leadhead(self):
        """Returns the head of leads."""
        return None if self.empty else self._frame.columns[0]

    @property
    def datehead(self):
        """Returns the head of dates."""
        return None if self.empty else self._frame.columns[1]

    @property
    def leads(self):
        """Returns Series of leads in the given frame."""
        return pandas.Series() if self.empty else self._frame[self.leadhead]

    @property
    def unique(self):
        """Returns list of unique leads in the given frame."""
        return self.leads.unique().tolist()

    @property
    def nunique(self):
        return len(self.unique)

    @property
    def dates(self):
        """Returns the datetime column selected by datehead."""
        return pandas.Series() if self.empty else self._frame[self.datehead]
    
    @property
    def mindate(self):
        """Returns the smallest datetime.date observed in the date column."""
        return self._mindate if self.empty else self.dates.min().date()-datetime.timedelta(days=45)

    @property
    def maxdate(self):
        """Returns the largest datetime.date observed in the date column."""
        return self._maxdate if self.empty else self.dates.max().date()+datetime.timedelta(days=45)

    @property
    def limit(self):
        """Returns the datetime.date limits observed in the date column."""
        return (self.mindate,self.maxdate)

    def filter(self,*args):
        """Returns frame after filtering for args on the lead column."""
        return self.frame if self.empty else self.__utils(frame).filter(frame.columns[1])

    def groupsum(self,*args):
        """Returns a new frame after datewise summing the args on the lead column."""
        return self.frame if self.empty else self.__utils(frame).groupsum(frame.columns[1])

if __name__ == "__main__":

    tv = Template()

    print(tv.frame)
    print(tv.datehead)
    print(tv.leadhead)

    # print(tv('Date').datehead)

    print(tv.empty)
    print(tv.dates)
    print(tv.mindate)
    print(tv.maxdate)
    print(tv.limit)

    tv2 = Template(pandas.DataFrame({'d':[1,1]}))

    print(tv2.frame)

    print(tv2.datehead)