import contextlib
import copy
import datetime

from dateutil import parser

from difflib import SequenceMatcher

import logging

import os
import re

import numpy

from .directory._browser import Browser

class TxtRead():

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

        dtypes = [numpy.dtype(type_) for type_ in types]

        floatFlags = [True if type_ is float else False for type_ in types]

        self.seekrow(self.skiprows)

        if all(floatFlags):
            cols = numpy.loadtxt(self.txtmaster,comments=self.comments,delimiter=self.delimiter,unpack=True)
        else:
            cols = numpy.loadtxt(self.txtmaster,comments=self.comments,delimiter=self.delimiter,unpack=True,dtype=str)

        heads = self.heads()

        for col,head in zip(cols,heads):
            self.txtfile.frame[head] = col

    @contextlib.contextmanager
    def txtopen(filepath):

        txtmaster = open(filepath,"r")
        try:
            yield txtmaster
        finally:
            txtmaster.close()

def strtypes(_list:list):

    return [strtype(string) for string in _list]

def strtype(string:str):

    for attempt in (float,parser.parse):

        try:
            typedstring = attempt(string)
        except:
            continue

        return type(typedstring)

    return str