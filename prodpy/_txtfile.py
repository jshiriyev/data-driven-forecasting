import contextlib
from dateutil import parser
import re

import numpy as np

class TxtFile():
    
    def __init__(self,txtfile,headline=None,comments="#",delimiter=None,skiprows=0):

        self.txtfile = txtfile

        self.headline = headline
        self.comments = comments
        self.delimiter = delimiter
        self.skiprows = skiprows
        
        with TxtWorm.txtopen(self.txtfile.filepath) as self.txtmaster:
            self.text()

    def seekrow(self,rownumber):

        self.txtmaster.seek(0)

        countrows = 0

        while True:

            if countrows >= rownumber:
                break

            next(self.txtmaster)

            countrows += 1

    def heads(self):

        if self.headline is None:
            return key2column(size=self.numcols,dtype='str').vals

        self.seekrow(self.headline)

        line = next(self.txtmaster).strip()

        if self.delimiter is None:
            heads_ = re.sub(r"\s+"," ",line).split(" ")
        else:
            heads_ = line.split(self.delimiter)

        return heads_

    def types(self):

        self.seekrow(self.skiprows)

        while True:

            line = next(self.txtmaster).strip()

            if len(line)<1:
                continue
            
            if line.startswith(self.comments):
                continue

            break

        if self.delimiter is None:
            row = re.sub(r"\s+"," ",line).split(" ")
        else:
            row = line.split(self.delimiter)

        return strtypes(row)

    def text(self):

        types = self.types()

        if self.headline is None:
            self.numcols = len(types)

        dtypes = [np.dtype(type_) for type_ in types]

        floatFlags = [True if type_ is float else False for type_ in types]

        self.seekrow(self.skiprows)

        if all(floatFlags):
            cols = np.loadtxt(self.txtmaster,comments=self.comments,delimiter=self.delimiter,unpack=True)
        else:
            cols = np.loadtxt(self.txtmaster,comments=self.comments,delimiter=self.delimiter,unpack=True,dtype=str)

        heads = self.heads()

        for col,head in zip(cols,heads):
            self.txtfile.frame[head] = col

    def write(self,filepath,comment=None,**kwargs):
        """It writes text form of frame."""

        if comment is None:
            comment = "# "

        with open(filepath,"w",encoding='utf-8') as txtmaster:

            txtmaster.write(self.header.__str__(comment=comment))
            txtmaster.write(f"{comment}\n")
            txtmaster.write(self.frame.__str__(limit=self.frame.shape[0],comment=comment,**kwargs))

        # np.savetxt("data.txt",Z,fmt="%s",header=header,footer=footer,comments="")

    def writeb(self,filepath):
        """It writes binary form of frame."""

        for header,datacolumn in zip(self._headers,self._running):
            kwargs[header] = datacolumn

        np.savez_compressed(filepath,**kwargs)

        # np.savez_compressed('data.npz', a=A, b=B, c=C)

    @contextlib.contextmanager
    def txtopen(filepath):

        txtmaster = open(filepath,"r")
        try:
            yield txtmaster
        finally:
            txtmaster.close()

    @staticmethod
    def strtypes(_list:list):

        return [strtype(string) for string in _list]

    @staticmethod
    def strtype(string:str):

        for attempt in (float,parser.parse):

            try:
                typedstring = attempt(string)
            except:
                continue

            return type(typedstring)

        return str