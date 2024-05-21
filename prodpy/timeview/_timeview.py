import datetime

import pandas

class TimeView():

    _mindate = datetime.date(2020,1,1)
    _maxdate = datetime.date(2030,1,1)

    def __init__(self,frame:pandas.DataFrame):
        self._frame, self._datehead = frame, None

    @property
    def frame(self):
        return self._frame

    @property
    def empty(self):
        return self._frame.empty

    def __call__(self,datehead:str):
        self._datehead = datehead

        return self

    @property
    def datehead(self):
        return self._datehead

    @property
    def dates(self):
        """Returns the datetime column selected by datehead."""
        if self.datehead is None or self.empty:
            return pandas.Series()

        return self._frame[self.datehead]

    @property
    def mindate(self):
        """Returns the smallest datetime.date observed in the date column."""
        if self.dates.empty:
            return self._mindate

        return dates.min().date()-datetime.timedelta(days=1)

    @property
    def maxdate(self):
        """Returns the largest datetime.date observed in the date column."""
        if self.dates.empty:
            return self._maxdate

        return dates.max().date()+datetime.timedelta(days=1)

    @property
    def limit(self):
        """Returns the datetime.date limits observed in the date column."""
        return (self.mindate,self.maxdate)