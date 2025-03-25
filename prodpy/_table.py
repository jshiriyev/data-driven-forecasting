import pandas as pd

from ._utils import utils

class Table():
    """A class to handle a pd.DataFrame of well data with column mapping."""

    fields = []

    def __init__(self,frame:pd.DataFrame=None,tiein:dict=None):
        """
        Initialize the class with a pd.DataFrame and a column mapping.

        Parameters:
        ----------
        frame (pd.DataFrame)  : The input pd.DataFrame containing perforation data.
        tiein (dict)          : A dictionary tying in data attributes to pd.DataFrame columns.

        """
        self.frame = frame # Calls the property setter
        self.tiein = tiein # Calls the property setter

    @property
    def frame(self) -> pd.DataFrame:
        """Returns the pd.DataFrame containing perforation data."""
        return self._frame

    @frame.setter
    def frame(self,value:pd.DataFrame) -> None:
        """Sets the pd.DataFrame, assigning empty dataframe if the input is None."""
        self._frame = pd.DataFrame(columns=self.fields) if value is None else value

    @property
    def tiein(self) -> dict:
        """Returns the column tie-in for the pd.DataFrame."""
        return self._tiein

    @tiein.setter
    def tiein(self,value:dict):
        """Sets the column tie-in, ensuring default tie-in if None is provided."""
        if value is None:
            self._tiein = {key:key for key in self.fields}
            return

        invalid_keys = [key for key in value.keys() if key not in self.fields]

        if invalid_keys:
            raise ValueError(f"tie-in keys are: {', '.join(self.fields)}")

        self._tiein = value

    def __repr__(self):
        """Returns a string representation of the object."""
        return f"{self.__class__.__name__}\n{repr(self.frame)}\n"

    def __getattr__(self,key):
        """Returns unique values for a given data field from the pd.DataFrame
        if key is in data fields, otherwise returns corresponding pd.DataFrame attribute.
        """
        if key in self.fields:
            return self.frame[self.tiein[key]]

        return getattr(self.frame,key)

    def __getitem__(self,key):
        """Retrieves a row as a data object if an integer index is given,
        otherwise returns the corresponding pd.DataFrame subset.
        """
        rows = self.frame.iloc[key]

        if rows.ndim == 1:
            rows = rows.to_frame().T

        return Table(rows,self.tiein)

    @property
    def datetimes(self):
        """Returns the list of column names with datetime format."""
        return utils.heads(self.frame,include=('datetime64',))

    @property
    def numbers(self):
        """Returns the list of column names with number format."""
        return utils.heads(self.frame,include=('number',))

    @property
    def nominals(self):
        """Returns the list of column names that are categorical by nature."""
        return utils.heads(self.frame,exclude=('number','datetime64'))

def prods(frame:pd.DataFrame=None,tiein:dict=None):

    from .wellbore import Operation

    Table.fields = Operation.fields()

    return Table(frame,tiein)

def perfs(frame:pd.DataFrame=None,tiein:dict=None):

    from .wellbore import Perf

    Table.fields = Perf.fields()

    return Table(frame,tiein)

if __name__ == "__main__":

    import datetime

    Table.fields.extend(["a","b","c","d"])

    df = pd.DataFrame(dict(
        A=[datetime.date(2020,1,1),datetime.date(2021,1,1),datetime.date(2022,1,1),datetime.date(2023,1,1)],
        B=['A','B','C','D'],
        C=['5-6','7-8','9-10','11'],
        D=['XY','XZ','YZ','ZZ']))

    base = Table(df,dict(a='A',b='B',c='C',d='D'))

    print(base[2].c)
    print(base[2:])

    # print(type(df.A))

    # print(base.a)
    # print(type(base.a))
    # print(base.c)

    # print(base.tiein)
    # print(base['A'])
    # print(base[2])

    # print(perfs.tiein)
    # print(perfs[2])

    # print(perfs.layer)

    # perfs2 = PerfFrame()

    # print(perfs2.tiein)

    # # # for d in dir(frame):
    # # #     print(d)
