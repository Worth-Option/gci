#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from scipy import optimize

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
desiredVar = desiredVar.dropna()

# Sign
sign = np.sign(desiredVar['e32']/desiredVar['e21'])
desiredVar['Sign'] = sign.astype(float)

# Order Error
initial = np.repeat(2.0, len(desiredVar.index))

def aparentOrder(order, df):
    order = np.abs(order)
    q = np.log(((r21**order)-desiredVar.Sign)/((r32**order)-desiredVar.Sign))
    ap = np.abs(np.log(np.abs(desiredVar['e32']/desiredVar['e21'])+q))/np.log(r21)
    error = np.abs(order - ap)
    error = np.array(error.values.tolist()) #converts to array
    return np.mean(error)

res = optimize.minimize(aparentOrder, args=(desiredVar),
                        x0=initial, method = 'Nelder-Mead', tol=0.01,
                        options={'maxiter':1000})

order = res.x
q = np.log((r21**order-desiredVar.Sign)/(r32**order-desiredVar.Sign))
ap = np.abs(np.log(np.abs(desiredVar['e32']/desiredVar['e21'])+q))/np.log(r21)
orderError = order - ap

desiredVar['Aparent Order'] = ap
desiredVar['Optimized Order'] = order
desiredVar['Order Error'] = orderError

# Extrapolated values
ext21 = ((r21**ap)*desiredVar.Variable_finer-desiredVar.Variable_medium)/((r21**ap)-1)
ext32 = ((r32**ap)*desiredVar.Variable_medium-desiredVar.Variable_coarser)/((r32**ap)-1)

desiredVar['Extrapolated Value (Finer, Medium)'] = ext21
desiredVar['Extrapolated Value (Medium, Coarser)'] = ext32

# Calculate and report the error estimatives
apxRelErr = np.abs((desiredVar.Variable_finer-desiredVar.Variable_medium)/desiredVar.Variable_finer)
extRelErr = np.abs((ext21-desiredVar.Variable_finer)/ext21)
gci = (1.25*apxRelErr)/((r21**ap)-1)

desiredVar['Aproximated Relative Error'] = apxRelErr
desiredVar['Extrapolated Relative Error'] = extRelErr
desiredVar['Grid Convergence Index'] = gci

# Export generated table
desiredVar.to_excel("treatment/results/gci.xlsx")  