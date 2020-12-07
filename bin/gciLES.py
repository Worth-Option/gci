#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  gciLES.py
#  
#  Copyright 2020 Luiz Oliveira
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

"""
Main module

This script analyses numerical and modeling errors in LES simulations
"""

import os
import re
import pandas as pd
from detect_delimiter import detect

def cls():
    """
    Clears the prompt
    """
    os.system('cls' if os.name=='nt' else 'clear')

def caseInfo(ncases):
    """
    Reads the case information for an n number of simulations
    """
    d = {'Elements' : [], 'DeltaT' : [], 'Volume' : []}
    for ii in range(ncases):
        elmt = int(input("Number of elements of the mesh {0}: ".format(ii)))
        dt = float(input("Timestep size of the mesh {0}: ".format(ii)))
        d['Elements'].append(elmt)
        d['DeltaT'].append(dt)
    d['Volume'].append(float(input("Total cell volume [m3]: ")))
    df = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in d.items() ]))
    df.index.names = ['Mesh']
    df.to_csv('treatment/caseInformation.csv', index = False)
    return df

def checkDelimiter(filename, directory):
    """
    Checks the delimiter of a file or takes the input from the user
    """
    with open(os.path.join(directory,filename)) as f:
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
    return delim

def caseImport(ncases):
    """
    Imports the data from an n number of simulations
    """
    directory = 'treatment'
    # Get all files.
    list = os.listdir(directory)
    filetpl = []
    for file in list:
        # Use join to get full file path.
        location = os.path.join(directory, file)
        # Get size and add to list of tuples.
        size = os.path.getsize(location)
        filetpl.append((size, file))
    # Sort list of tuples by the first element, size.
    filetpl.sort(key=lambda s: s[0])
    filetpl.reverse()
    df = pd.DataFrame(data=filetpl, columns=["Size","Filename"])
    df.drop(df.tail(len(list)-ncases).index, inplace = True)
    df.index.names = ['Mesh']
    print("Assuming this file order:")
    print(df.to_string())
    order = int(input("Is this corrrect?\n[1] Yes\n[2] No\nChoice: "))
    if order == 2:      
        lst = []
        print("Write the mesh number succeeded by the file name:\n")
        for ii in range(ncases): 
            file = [input(), int(input())] 
            lst.append(file) 
        df = pd.DataFrame(data=lst, columns=["Size","Filename"])
        df.index.names = ['Mesh']
        cls()
        print("Files to be imported:\n")
        print(df.to_string())
    importedFiles = dict()
    delim = checkDelimiter(df.Filename[0],directory)
    for ii in range(ncases):
        temp = pd.read_csv(os.path.join(directory,df.Filename[ii]),
                           delimiter=delim)
        importedFiles['Mesh '+str(ii)] = temp
    return importedFiles

def refinementRate(df):
    """
    Defines the refinement rate between the meshes
    """
    r = list()
    for n in range(testVersion):
        if n == testVersion - 1:
            refRate = 1
        else:
            refRate = df.Elements[n+1]/df.Elements[n]
        r.append(refRate)
    df['r'] = r
    return df

# Import the case structure data (mesh and timestep)
testVersion = int(input("""Which test should be performed?
[1] Short Version (3 cases)
[2] Long Version (5 cases)
Choice: """))
if testVersion == 1:
    testVersion = 3
else:
    testVersion = 5

infoFile = 'treatment/caseInformation.csv'
if os.path.exists(infoFile):
    infoDf = pd.read_csv(infoFile)
else: 
    print ("Please state the meshes from the finer to the coarser")  
    infoDf = caseInfo(testVersion)

# Import simulation data
simDf = caseImport(testVersion)

# Starts evaluating the GCI
infoDf.eval('h = (@infoDf.Volume[0]/Elements)**(1/3)', inplace=True)
infoDf.eval('hstar = (h*DeltaT)**(1/2)', inplace=True)
infoDf = refinementRate(infoDf)
delta = max(infoDf.h)
r = infoDf.r.mean()
hstar = infoDf.hstar.mean()

## Simulated data
var = input("Write the name of the desired variable: ")
s1 = simDf['Mesh 0'][var]
s2 = simDf['Mesh 1'][var]
s3 = simDf['Mesh 2'][var]
if testVersion == 5:
    s4 = simDf['Mesh 3'][var]
    s5 = simDf['Mesh 4'][var]

# Simplified method
cm = (r**(1.7)*(s1-s2)-(s2-s3))/((r**(1.7)-r**(1.5)-r**(3.2)+r**(3))\
      *delta**(1.5))
sc = ((r**(1.7)*s1-s2)*(r**(3.2)-r**(3))-(r**(1.7)*s2-s3)*(r**(1.7)\
      -r**(1.5)))/((r**(1.7)-1)*((r**(3.2)-r**(3))-(r**(1.7)-r**(1.5))))
cn = (s1-sc-cm*delta**(1.5))/(hstar**(1.7))

    

