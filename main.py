#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  main.py
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

This script analyses numerical and modeling errors in LES simulations and
Grid convergence analysis on RANS simulations.
The analysis steps are performed by the modules in the bin folder
"""

import sys
import os
import shutil
import time
start_time = time.time()

def cls():
    """
    Clears the prompt
    """
    os.system('cls' if os.name=='nt' else 'clear')

# Check for necessary directories
if not os.path.exists('treatment'):
    os.makedirs('treatment')
    print("The directory treatment/ was created, please populate with the "
          "desired csv files to be analysed.")
    sys.exit('The directory treatment/ did not exist.')
elif not os.listdir('treatment'):
    sys.exit('The directory treatment/ is empty.')
    
# Clear the previous results directories
if os.path.exists('treatment/results'):
    shutil.rmtree('treatment/results')
os.makedirs('treatment/results')

# Import CSV
exec(open("bin/import.py").read());

analysisType = input("Type of Analysis\n[1] RANS\n[2] LES\nChosen Option: ")

if analysisType == 1:
    # Grid Convergence Analysis (RANS)
    exec(open("bin/gci.py").read());
else:
    # Grid Convergence Analysis (LES)
    exec(open("bin/gciLES.py").read());
