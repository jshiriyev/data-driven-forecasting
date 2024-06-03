import datetime

import pandas

class TimeView():

    _mindate = datetime.date(2020,1,1)
    _maxdate = datetime.date(2030,1,1)

    _datehead = None
    _leadhead = None

    def __init__(self,frame:pandas.DataFrame,**kwargs):

        self._frame = frame

        self(**kwargs)

    @property
    def frame(self):
        return self._frame

    @property
    def empty(self):
        return self._frame.empty

    def __call__(self,leadhead:str=None,datehead:str=None):
            
        self._leadhead = leadhead
        self._datehead = datehead

        return self

    def __iter__(self):

        for item in self.items:
            yield item,self.filter(item)

    @property
    def leadhead(self):
        return self._leadhead

    @property
    def datehead(self):
        return self._datehead

    @property
    def leads(self):
        """Returns Series of leads in the given frame."""
        return pandas.Series() if self._leadhead is None else self._frame[self._leadhead]

    @property
    def items(self):
        """Returns list of unique leads in the given frame."""
        return self.leads.unique().tolist()

    @property
    def nunique(self):
        return len(self.items)

    @property
    def dates(self):
        """Returns the datetime column selected by datehead."""
        return pandas.Series() if self._datehead is None else self._frame[self._datehead]
    
    @property
    def mindate(self):
        """Returns the smallest datetime.date observed in the date column."""
        if self.dates.empty:
            return self._mindate

        return self.dates.min().date()-datetime.timedelta(days=45)

    @property
    def maxdate(self):
        """Returns the largest datetime.date observed in the date column."""
        if self.dates.empty:
            return self._maxdate

        return self.dates.max().date()+datetime.timedelta(days=45)

    @property
    def limit(self):
        """Returns the datetime.date limits observed in the date column."""
        return (self.mindate,self.maxdate)

    def filter(self,*args):
        """Filters and returns frame based on the item in the lead column."""
        return self._frame if self.leads.empty else self._frame[self.leads.isin(args)].reset_index(drop=True)

if __name__ == "__main__":

    tv = TimeView()

    print(tv.frame)
    print(tv.datehead)
    print(tv.leadhead)

    print(tv('Date').datehead)

    print(tv.empty)
    print(tv.dates)
    print(tv.mindate)
    print(tv.maxdate)
    print(tv.limit)