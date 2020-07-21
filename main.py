#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

# Create Results Folder
if not os.path.exists('treatment/results'):
    os.makedirs('treatment/results')

# Import CSV
exec(open("bin/import.py").read());
cls()
print('Variables imported...')

# Grid Convergence Analysis
exec(open("bin/gci.py").read());
cls()
print('Grid convergence analysis performed...')

# Plot data with error bars
exec(open("bin/plot.py").read());
cls()
print('All done.')