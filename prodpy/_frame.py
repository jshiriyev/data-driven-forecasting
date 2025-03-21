from pandas import DataFrame

class BaseFrame():
    """A class to handle a DataFrame of perforation data with column mapping."""

    fields = [] # needs modification here

    def __init__(self,frame:DataFrame=None,tiein:dict=None):
        """
        Initialize the class with a DataFrame and a column mapping.

        Parameters:
        ----------
        frame (pd.DataFrame)  : The input DataFrame containing perforation data.
        tiein (dict)          : A dictionary tying in data attributes to DataFrame columns.
        """
        self.frame = frame # Calls the property setter
        self.tiein = tiein # Calls the property setter

    @property
    def frame(self) -> DataFrame:
        """Returns the DataFrame containing perforation data."""
        return self._frame

    @frame.setter
    def frame(self,value:DataFrame) -> None:
        """Sets the DataFrame, assigning empty dataframe if the input is None."""
        self._frame = DataFrame(columns=self.fields) if value is None else value

    @property
    def tiein(self) -> dict:
        """Returns the column tie-in for the DataFrame."""
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

    def __getattr__(self,key):
        """Returns unique values for a given data field from the DataFrame
        if key is in data fields, otherwise returns corresponding DataFrame attribute.
        """
        if key in self.fields:
            return self.frame[self.tiein[key]].unique()

        return getattr(self.frame,key)

    def __getitem__(self,key):
        """Retrieves a row as a data object if an integer index is given,
        otherwise returns the corresponding DataFrame subset.
        """
        if isinstance(key,int):
            row = self.frame.iloc[key].to_dict()

            return {key:row.get(col) for key,col in self.tiein.items()}

        return self.frame[key] # Directly return the DataFrame subset
    
if __name__ == "__main__":

    frame = DataFrame(dict(
        A=[date(2020,1,1),date(2021,1,1),date(2022,1,1),date(2023,1,1)],
        B=['A','B','C','D'],
        C=['5-6','7-8','9-10','11'],
        D=['XY','XZ','YZ','ZZ']))

    perfs = PerfFrame(frame,dict(date='A',layer='B',interval='C',guntype='D'))

    # help(frame.__getitem__)

    print(perfs.tiein)
    print(perfs[2])

    print(perfs.layer)

    perfs2 = PerfFrame()

    print(perfs2.tiein)

    # # for d in dir(frame):
    # #     print(d)
