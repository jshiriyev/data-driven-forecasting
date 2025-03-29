from dataclasses import dataclass, fields

import datetime

@dataclass
class Interval:

    above   : float
    below   : float

    def tostr(self,template:str=None):
        """Converts the interval into a string."""
        if template is None:
            template = "{}-{}"

        return template.format(self.below,self.above)
    
    @staticmethod
    def tolist(interval:str,delimiter:str="-",decsep:str=".") -> list:
        """Converts a string interval into a list of floats.

        Parameters:
        ----------
        interval  : The interval string (e.g., "1005-1092").
        delimiter : The delimiter separating depths in the interval. Defaults to "-".
        decsep    : The decimal separator in the depth of the interval. Defaults to ".".
        
        Returns:
        -------
        List: A list containing one or two float values. If only one value
            is provided, the second element will be None.
        """
        try:
            depths = [float(depth.replace(decsep,'.')) for depth in interval.split(delimiter)]
            if len(depths)==1:
                depths.append(None)
            elif len(depths) > 2:
                raise ValueError(f"Unexpected format: '{interval}'. Expected format 'depth_1{delimiter}depth_2'.")
            return depths
        except ValueError as e:
            raise ValueError(f"Invalid interval format: {interval}. Error: {e}")

@dataclass
class Perf:
    """It is a dictionary for a perforation in a well."""
    interval    : tuple

    layer       : str = None
    guntype     : str = None
    start       : datetime.date = None
    stop        : datetime.date = None

    def __post_init__(self):

        self.interval = Interval(*self.interval)

    @staticmethod
    def fields() -> list:
        """Returns the list of field names in the Perf dataclass."""
        return [f.name for f in fields(Perf)]

class Perfs():
    """A collection of 'Perf' objects with list-like access."""

    def __init__(self,*args:Perf):

        self._list = list(args)

    def __getitem__(self,key):
        """Retrieves a 'Perf' object by index."""
        return self._list[key]

    def __iter__(self):
        """Allows iteration over the 'Perf' objects."""
        return iter(self._list)

    def __len__(self) -> int:
        """Returns the number of 'Perf' objects."""
        return len(self._list)

    def add(self,**kwargs):
        """Adds one perforation item."""
        self._list.append(Perf(**kwargs))

    def append(self,perf:Perf) -> None:
        """Adds a new 'Perf' object to the collection."""
        if not isinstance(perf, Perf):
            raise TypeError("Only Perf objects can be added.")
        self._list.append(perf)

    def extend(self,perfs:Perf) -> None:
        """Adds a new 'Perf' object to the collection."""
        for perf in perfs:
            self.append(perf)

    def __getattr__(self,key):
        """Forwards attribute access to the internal list object."""
        return getattr(self._list,key)
    