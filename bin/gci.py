#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
import numpy as np

def cls():
    """
    Clears the prompt
    """
    os.system('cls' if os.name=='nt' else 'clear')

cElements = int(input("Number of elements of the coarser mesh: "))
mElements = int(input("Number of elements of the medium mesh: "))
fElements = int(input("Number of elements of the finer mesh: "))

analysisType = input("Type of Analysis\n[1] 2D\n[2] 3D\nChosen Option: ")
volume = float(input("Total cell volume [m3]: "))

if analysisType == '1':
	h1 = (volume/fElements)**(0.5)
	h2 = (volume/mElements)**(0.5)
	h3 = (volume/cElements)**(0.5)
	
elif analysisType == '2':
	h1 = (volume/fElements)**(1/3)
	h2 = (volume/mElements)**(1/3)
	h3 = (volume/cElements)**(1/3)
	
else:
	cls()
	print("Deleting all data...")
	print("Computer shutting down...")

# Refinement rate

r21 = h2/h1
r32 = h3/h2

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
