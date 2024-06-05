import datetime

import pandas

class Template():

    _mindate = datetime.date(2020,1,1)
    _maxdate = datetime.date(2030,1,1)

    def __init__(self,*args,**kwargs):
        """The frame must contain leads on the first column, dates on the second
        column and numerical values on the remaining columns."""
        self._frame = self.__frame(*args,**kwargs)

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
        return self.frame if self.empty else self.__filter(*args)

    def sum(self,*args):
        """Returns a new frame after datewise summing the args on the lead column."""
        return self.frame if self.empty else self.__sum(*args)

    def __filter(self,*args):
        """Returns frame after filtering for args on the lead column of non-empty frames."""
        return self.frame[self.leads.isin(args)].reset_index(drop=True)

    def __sum(self,*args):
        """Returns a new frame after datewise summing the args on the lead column
        of non-empty frames."""
        frame = self.__filter(*args)
        leads = self.__concat_leads(frame)
        frame = self.__groupby_date(frame)

        frame.iloc[:,0] = leads

        return frame

    @staticmethod
    def __frame(unknown=None,**kwargs):
        """Returns an empty pandas.DataFrame if frame is None."""
        return unknown if isinstance(unknown,pandas.DataFrame) else pandas.DataFrame(unknown,**kwargs)

    @staticmethod
    def __series(*args,**kwargs):
        """Return pandas series."""
        return pandas.Series(*args,**kwargs)

    @staticmethod
    def __groupby_date(frame):
        """Returns a new frame after grouping based on date column."""
        return frame.groupby(frame.columns[1]).sum().reset_index()

    @staticmethod
    def __concat_leads(frame):
        """Returns a string after concatenating unique leads."""
        return " ".join(frame.iloc[:,0].unique())

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