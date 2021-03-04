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

def refinementRate(df, testVersion):
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

def run(testVersion, nVar, var, axis):
    # Import the case structure data (mesh and timestep)
    ##testVersion = int(input("Which test should be performed?\n"
    ##                        "[1] Short Version (3 cases)\n"
    ##                        "[2] Long Version (5 cases)\n"
    ##                        "Choice: "))
    ##if testVersion == 1:
    ##    testVersion = 3
    ##else:
    ##    testVersion = 5

    infoFile = 'treatment/caseInformation.csv'
    if os.path.exists(infoFile):
        infoDf = pd.read_csv(infoFile)
    else: 
        print ("Please state the meshes from the finer to the coarser")  
        infoDf = caseInfo(testVersion)

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
        for ii in range(testVersion):
            jj = str(ii)
            lst = [float(input("Mesh "+jj+" value: "))]
            simDf['Mesh '+jj] = pd.DataFrame(data=lst,columns=[var])
        del ii,jj,lst
    elif nVar == 2:
        simDf = caseImport(testVersion)
    del nVar

    # Starts evaluating the GCI
    infoDf.eval('h = (@infoDf.Volume[0]/Elements)**(1/3)', inplace=True)
    infoDf.eval('hstar = (h*DeltaT)**(1/2)', inplace=True)
    infoDf = refinementRate(infoDf, testVersion)
    delta = max(infoDf.h)
    r = infoDf.r.mean()
    hstar = infoDf.hstar.mean()

    ## Simulated data
    s1 = simDf['Mesh 0'][var]
    s2 = simDf['Mesh 1'][var]
    s3 = simDf['Mesh 2'][var]
    if testVersion == 5:
        s4 = simDf['Mesh 3'][var]
        s5 = simDf['Mesh 4'][var]
    if testVersion == 3:
        # Simplified method
        """
        This section of the code implements the 3 equation proceedure from
        Dutta, R. and Xing, T. (2018)
        ‘Five-equation and robust three-equation methods for solution verification of large eddy simulation’
        Journal of Hydrodynamics, 30(1), pp. 23–33. doi: 10.1007/s42241-018-0002-0.
        """
        pn = 1.7
        pm = 1.5
        cm = (r**(1.7)*(s1-s2)-(s2-s3))/((r**(1.7)-r**(1.5)-r**(3.2)+r**(3))\
              *delta**(1.5))
        sc = ((r**(1.7)*s1-s2)*(r**(3.2)-r**(3))-(r**(1.7)*s2-s3)*(r**(1.7)\
              -r**(1.5)))/((r**(1.7)-1)*((r**(3.2)-r**(3))-(r**(1.7)-r**(1.5))))
        cn = (s1-sc-cm*delta**(1.5))/(hstar**(1.7))
        Enum = dict()
        Enum[0] = cn*(hstar**1.7)
        Enum[1] = cn*(r**1.7)*(hstar**1.7)
        Enum[2] = cn*(r**3.4)*(hstar**1.7)
        Emod = dict()
        Emod[0] = cm*(delta**1.5)
        Emod[1] = cm*(r**1.5)*(delta**1.5)
        Emod[2] = cm*(r**3)*(delta**1.5)
        jj=0
        for ii in simDf:
            simDf[ii]['Sc'] = sc
            simDf[ii]['Numerical Error'] = Enum[jj]
            simDf[ii]['Modelling Error'] = Emod[jj]
            simDf[ii]['Total Error'] = Enum[jj] + Emod[jj]
            jj+=1
        del ii,jj
    elif testVersion == 5:
        # Full method
        """
        This section of the code implements the 5 equation proceedure from
        Dutta, R. and Xing, T. (2018)
        ‘Five-equation and robust three-equation methods for solution verification of large eddy simulation’
        Journal of Hydrodynamics, 30(1), pp. 23–33. doi: 10.1007/s42241-018-0002-0.
        """
        def fullMethod(vars):
        # =========================================================================
        #     Sets the nonlinear system of 5 equations
        # =========================================================================
            sc, cn, cm, pn, pm = vars
            eq1 = cn*hstar**pn + cm*delta**pm
            eq2 = cn*(r*hstar)**pn + cm*(r*delta)**pm
            eq3 = cn*((r**2)*hstar)**pn + cm*((r**2)*delta)**pm
            eq4 = cn*((r**3)*hstar)**pn + cm*((r**3)*delta)**pm
            eq5 = cn*((r**4)*hstar)**pn + cm*((r**4)*delta)**pm
            return [eq1, eq2, eq3, eq4, eq5]
        sc, cn, cm, pn, pm =  fsolve(fullMethod, (0.007, 1, 1, 1.7, 1.5))
        Enum = dict()
        for ii in range(testVersion):
            if ii == 0:
                val = cn*hstar**pn
            else:
                val = cn*((r**ii)*hstar)**pn
            Enum[ii]=val
        Emod = dict()
        for ii in range(testVersion):
            if ii == 0:
                val = cm*delta**pm
            else:
                val = cm*((r**ii)*delta)**pm
            Emod[ii]=val
        jj=0
        for ii in simDf:
            simDf[ii]['Sc'] = sc
            simDf[ii]['Numerical Error'] = Enum[jj]
            simDf[ii]['Modelling Error'] = Emod[jj]
            simDf[ii]['Total Error'] = Enum[jj] + Emod[jj]
            jj+=1
        del ii, jj, val, var
    # Export Results to Excel
    d = {'Order of Accuracy for the Numerical Error (Pn)': pn,
         'Order of Accuracy for the Modelled Error (Pm)': pm,
         'Mean Constant for Numerical Errors (Cn)': cn.mean(),
         'Mean Constant for Modelled Errors (Cm)': cm.mean(),
         'Delta': delta,
         'Hstar': hstar,
         'Mean Refinement Rate': r
        }
    idx = [0]
    summary = pd.DataFrame(data=d, index=idx)
    xlsxFile = 'treatment/results/dataSummary.xlsx'
    if not os.path.isfile(xlsxFile):
        wb = openpyxl.Workbook()
        wb.save(xlsxFile)
    with pd.ExcelWriter(xlsxFile, engine="openpyxl", mode='a') as writer:
        summary.to_excel(writer, sheet_name='Summary', index=False)
        for df_name, df in simDf.items():
            df.to_excel(writer, sheet_name=df_name, index=False)

    del d, idx, xlsxFile

    # All meshes
    fig, ax = plt.subplots(figsize=(9,6), dpi=300)
    ax.plot(simDf['Mesh 0'][axis], simDf['Mesh 0'][var],
                label= 'Mesh 0', aa=True)
    ax.plot(simDf['Mesh 1'][axis], simDf['Mesh 1'][var],
                label= 'Mesh 1', aa=True)
    ax.plot(simDf['Mesh 2'][axis], simDf['Mesh 2'][var],
                label= 'Mesh 2', aa=True)
    if testVersion == 5:
        ax.plot(simDf['Mesh 3'][axis], simDf['Mesh 3'][var],
                label= 'Mesh 3 - Coarser', aa=True)
        ax.plot(simDf['Mesh 4'][axis], simDf['Mesh 4'][var],
                label= 'Mesh 4 - Coarser', aa=True)

    ax.legend(loc='best',fontsize='x-large')

    plt.grid()
    plt.autoscale(enable=True, tight=True)
    plt.xlabel(axis,fontsize='x-large')
    plt.ylabel(var,fontsize='x-large')
    plt.savefig('treatment/results/allMeshes.png', bbox_inches='tight')
    # Plot with error bars
    fig, ax = plt.subplots(figsize=(9,6), dpi=300)
    l, caps, c = plt.errorbar(simDf['Mesh 1'][axis], simDf['Mesh 1'][var],
                simDf['Mesh 1']['Total Error'],
                elinewidth = 1, capsize = 5, capthick = 1, marker = 'o',
    #            errorevery = 5,
                uplims = True, lolims = True, 
                lw=1.5, aa = True)

    for cap in caps:
        cap.set_marker("_")

    plt.grid()
    plt.autoscale(enable=True, tight=True)
    plt.xlabel(axis,fontsize='x-large')
    plt.ylabel(var,fontsize='x-large')
    plt.savefig('treatment/results/Mesh1.png', bbox_inches='tight')
