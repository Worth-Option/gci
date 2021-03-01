#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Libraries
import os
import re
import pandas as pd
from detect_delimiter import detect

def cls():
    """
    Clears the prompt
    """
    os.system('cls' if os.name=='nt' else 'clear')

# Input delimeter and file names
coarserFile = input("Name of coarser mesh file: ")
mediumFile = input("Name of medium mesh file: ")
finerFile = input("Name of finer mesh file: ")

coarserFile = "treatment/" + coarserFile
mediumFile = "treatment/" + mediumFile
finerFile = "treatment/" + finerFile

with open(coarserFile) as f:
    for line in f:
        if re.match(r"^\d+.*$",line):
            delim = detect(line)
            break
if delim is None:
    delim = input("""Type of delimiter\n[1] ('\\t')\n[2] (' ')\n[3] (';')
                  [4] (',')\n [5] Custom delimiter\nChosen option: """)
    delim = int(delim)
    if delim == 1:
        delim = '\\t'
    elif delim == 2:
        delim = ' '
    elif delim == 3:
        delim = ';'
    elif delim == 4:
        delim = ','
    elif delim == 5:
        delim = input("Enter custom delimiter: ")
        
cls()

print("Python columns start on zero, please pay attention to this detail.\n")
axis = int(input("Axis column number: "))
var = int(input("Variable column number: "))

headerlines = int(input("Number of header lines: "))

# Import generated data
coarser = pd.read_csv(coarserFile,delimiter=delim, skiprows=headerlines,
                      usecols=[axis,var], header=0,
                      names=["Axis","Variable_coarser"])
medium = pd.read_csv(mediumFile,delimiter=delim, skiprows=headerlines,
                      usecols=[axis,var], header=0,
                      names=["Axis","Variable_medium"])
finer = pd.read_csv(finerFile,delimiter=delim, skiprows=headerlines,
                      usecols=[axis,var], header=0,
                      names=["Axis","Variable_finer"])

# Reindexing using axis
coarser = coarser.set_index('Axis')
medium = medium.set_index('Axis')
finer = finer.set_index('Axis')

# Sorting imported data
coarser = coarser.sort_values('Axis')
medium = medium.sort_values('Axis')
finer = finer.sort_values('Axis')

cls()
