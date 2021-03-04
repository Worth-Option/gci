#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import openpyxl
import pandas as pd
import matplotlib.pyplot as plt
from detect_delimiter import detect
from scipy.optimize import fsolve

if __name__ == "__main__":
    sys.exit('This file must run as a module, please run main.py')

def cls():
    """
    Clears the prompt
    """
    os.system('cls' if os.name=='nt' else 'clear')

def caseInfo():
    """
    Reads the case information for an n number of simulations
    """
    d = {'Elements' : [], 'Volume' : []}
    for ii in range(3):
        elmt = int(input("Number of elements of the mesh {0}: ".format(ii)))
        d['Elements'].append(elmt)
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
            file = [int(input()), input()] 
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

def run(nVar, var, axis):
    infoFile = 'treatment/caseInformation.csv'
    if os.path.exists(infoFile):
        infoDf = pd.read_csv(infoFile)
    else: 
        print ("Please state the meshes from the finer to the coarser")  
        infoDf = caseInfo()

    # Import simulation data
    ##nVar = int(input("""[1] Single data point
    ##[2] Multiple data point (line)
    ##Choice: """))
    cls()
    ##var = input("Write the name of the desired variable: ")
    ##axis = input("Write the name of the desired plot axis: ")
    if nVar == 1:
        cls()
        print("Please insert the point value for the meshes")
        simDf = dict()
        for ii in range(3):
            jj = str(ii)
            lst = [float(input("Mesh "+jj+" value: "))]
            simDf['Mesh '+jj] = pd.DataFrame(data=lst,columns=[var])
        del ii,jj,lst
    elif nVar == 2:
        simDf = caseImport(3)
    del nVar

    def refinementRate(volume, elements):
        exponent = input("Type of Analysis\n[1] 2D\n[2] 3D\nChosen Option: ")
        if exponent == "1":
            exponent = 1/2
        elif exponent == "2":
            exponent = 1/3
        else:
            sys.exit("Invalid option")  
        h = list()
        for ii in range(2, -1, -1):
            h[ii] = (volume/elements[ii])**exponent   
        r = list()
        r[0] = h[1]/h[0]
        r[1] = h[2]/h[1]    
        return r

    r = refinementRate(infoDf.Volume[0], infoDf.Elements)
    # Variable absolute error
    desiredVar = pd.concat([finer, medium, coarser], axis=1)
    desiredVar = desiredVar.interpolate('index').reindex(medium.index)
    e21 = desiredVar.Variable_medium - desiredVar.Variable_finer
    e32 = desiredVar.Variable_coarser - desiredVar.Variable_medium
    desiredVar['e21'] = e21
    desiredVar['e32'] = e32

    # Sign
    sign = np.sign(desiredVar['e32']/desiredVar['e21'])
    desiredVar['Sign'] = sign

    # p 
    p = np.abs(np.log(np.abs(desiredVar['e32']/desiredVar['e21'])+order)/np.log(r21))
