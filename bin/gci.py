#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import openpyxl
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from detect_delimiter import detect
from scipy.optimize import fsolve, minimize

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

    def refinementRate(df):
        exponent = input("Type of Analysis\n[1] 2D\n[2] 3D\nChosen Option: ")
        if exponent == "1":
            df.eval('h = (Volume[0]/Elements)**(1/2)', inplace=True)
        elif exponent == "2":
            df.eval('h = (Volume[0]/Elements)**(1/3)', inplace=True)
        else:
            sys.exit("Invalid option")

        r = [i for i in range(2)]
        r[0] = df.h[1]/df.h[0]
        r[1] = df.h[2]/df.h[1]
        r = pd.Series(r, name="r")
        df = pd.concat([df, r], ignore_index=True, axis=1)
        df.columns = ["Cells", "Volume", "h", "r"]
        return df

    # Refinement rate
    infoDf = refinementRate(infoDf)
    
    # Data Processing
    simData = dict()
    for ii in range(3):
        variable = simDf['Mesh '+str(ii)][var]
        variable.index = simDf['Mesh '+str(ii)][axis]
        variable.name = "Mesh "+str(ii)
        simData['Mesh '+str(ii)] = variable
        
    del simDf, variable
    
    # Variable absolute error
    desiredVar = pd.concat([simData["Mesh 0"],\
                            simData["Mesh 1"],\
                            simData["Mesh 2"]], axis=1)
    desiredVar = desiredVar.interpolate('index').reindex(simData["Mesh 1"].index)
    desiredVar.dropna(inplace=True)
    desiredVar['e21'] = desiredVar["Mesh 1"] - desiredVar["Mesh 2"]
    desiredVar['e32'] = desiredVar["Mesh 0"] - desiredVar["Mesh 1"]

    # Sign
    sign = np.sign(desiredVar['e32']/desiredVar['e21'])
    desiredVar['Sign'] = sign

    # p 
#    p = np.abs(np.log(np.abs(desiredVar['e32']/desiredVar['e21'])+order)/np.log(infoDf.r[0]))

    # Error Order
    initial = np.repeat(2.0, len(desiredVar.index))
    
    def aparentOrder(order, df):
        order = np.abs(order)
        q = np.log(((infoDf.r[0]**order)-desiredVar.Sign)/((desiredVar.r[1]**order)-desiredVar.Sign))
        ap = np.abs(np.log(np.abs(desiredVar['e32']/desiredVar['e21'])+q))/np.log(infoDf.r[0])
        error = np.abs(order - ap)
        error = np.array(error.values.tolist()) #converts to array
        return np.mean(error)
    
    res = minimize(aparentOrder, args=(desiredVar),
                            x0=initial, method = 'Nelder-Mead', tol=0.01,
                            options={'maxiter':1000})
    
    order = res.x
    q = np.log((infoDf.r[0]**order-desiredVar.Sign)/(desiredVar.r[1]**order-desiredVar.Sign))
    ap = np.abs(np.log(np.abs(desiredVar['e32']/desiredVar['e21'])+q))/np.log(infoDf.r[0])
    orderError = order - ap
    
    desiredVar['Aparent Order'] = ap
    desiredVar['Optimized Order'] = order
    desiredVar['Order Error'] = orderError
    
    # Extrapolated values
    ext21 = ((infoDf.r[0]**ap)*desiredVar.Variable_finer-desiredVar.Variable_medium)/((infoDf.r[0]**ap)-1)
    ext32 = ((desiredVar.r[1]**ap)*desiredVar.Variable_medium-desiredVar.Variable_coarser)/((desiredVar.r[1]**ap)-1)
    
    desiredVar['Extrapolated Value (Finer, Medium)'] = ext21
    desiredVar['Extrapolated Value (Medium, Coarser)'] = ext32
    
    # Calculate and report the error estimatives
    apxRelErr = np.abs((desiredVar.Variable_finer-desiredVar.Variable_medium)/desiredVar.Variable_finer)
    extRelErr = np.abs((ext21-desiredVar.Variable_finer)/ext21)
    gci = (1.25*apxRelErr)/((infoDf.r[0]**ap)-1)
    
    desiredVar['Aproximated Relative Error'] = apxRelErr
    desiredVar['Extrapolated Relative Error'] = extRelErr
    desiredVar['Grid Convergence Index'] = gci
    
    # Export generated table
    desiredVar.to_excel("treatment/results/gci.xlsx")   


