|pypi| |pyversions|

------------

# Grid Convergence Index
A python script to analyse numerical errors in Computational Fluid Dynamics Simulations (CFD).

This script works both for Reynolds Averaged Navier-Stokes (RANS) simulations using the proceedure "Procedure for Estimation and Reporting of Uncertainty Due to Discretizationin CFD Applications" https://www.doi.org/10.1115/1.2960953
and on Large Eddy Simulations (LES) based on Dutta, R. and Xing, T. (2018) ‘Five-equation and robust three-equation methods for solution verification of large eddy simulation’ https://www.doi.org/10.1007/s42241-018-0002-0.

------------

Installation
============

lorem_ipsum()

------------

Usage
============
Run the `main.py` script on a python3 console.

```
python3 main.py
```

The script will automatically create a directory named *treatment* where the desired *csv* files must be placed.
The processed output stays in the file `treatment/results/dataSummary.xlsx`.
