from dataclasses import dataclass

import re

import numpy

from ._drilling import Drilling

from ._layout import Layout
from ._survey import Survey

from ._zones import Zones
from ._perfs import Perfs

@dataclass
class Name:

    name : str

    @staticmethod
    def apply(index:int,template:str=None) -> str:
        """Generates a well name by formatting a given index into a string template.

        Parameters:
        ----------
        index    : The well index (number)
        template : A string template containing a placeholder (e.g., "Well-{}").
        
        Returns:
        -------
        str: The formatted well name.

        Raises:
        ------
        ValueError: If the template does not contain a valid placeholder.

        """
        template = "Well-{}" if template is None else template

        try:
            return template.format(index)
        except Error as e:
            raise ValueError(f"Invalid template '{template}' for index '{index}'. Error: {e}")

    @staticmethod
    def parse(name:str,regex:str=None) -> str:
        """Returns a searched part of the name. If no match is found, returns the original name.

        Parameters:
        ----------
        name (str): The name to parse.
        regex (raw str): A custom regular expression for extraction. Defaults to extracting digits.

        Returns:
        -------
        str: The extracted content, or the original string if no match is found.

        """
        regex = r'\d+' if regex is None else regex
        # previous version of the code : r"'(.*?)'"
        # previous chatgpt suggestion : r"'([^']*)'"

        match = re.search(regex,name)
        
        return match.group() if match else name

@dataclass
class Slot:
    """It is a slot dictionary for a well."""
    index   : int = None

    plt     : str = None

    xhead   : float = 0.0
    yhead   : float = 0.0
    datum   : float = 0.0

class Well():
    """It is a well dictionary with all sub classes."""

    STATUS_OF_WELL = []

    def __init__(self,
        name        : str,
        status      : str = "active",
        slot        : dict = None,
        drill       : dict = None,
        survey      : dict = None,
        zones       : dict = None,
        ):

        self.name   = name
        self.status = status
        self.slot   = slot
        
        self.drill  = drill
        self.layout = None
        self.survey = survey
        self.zones  = zones
        self.perfs  = None

        self.las    = []

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self,value:str):
        self._name = Name(value)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self,value:str):
        self._status = value

    @property
    def slot(self):
        return self._slot

    @slot.setter
    def slot(self,value:dict):
        self._slot = Slot(**(value or {}))

    @property
    def drill(self):
        return self._drill

    @drill.setter
    def drill(self,value:dict):
        self._drill = Drilling(**(value or {}))

    @property
    def layout(self):
        return self._layout

    @layout.setter
    def layout(self,value):
        self._layout = Layout()

    @property
    def survey(self):
        return self._survey

    @survey.setter
    def survey(self,value:dict):
        self._survey = Survey(**(value or {}))

    @property
    def zones(self):
        return self._zones

    @zones.setter
    def zones(self,value:dict):
        self._zones = Zones(**(value or {}))

    @property
    def perfs(self):
        return self._perfs

    @perfs.setter
    def perfs(self,value):
        self._perfs = Perfs()