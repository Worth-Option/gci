#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(9,6), dpi=300)
ax.plot(desiredVar.index, desiredVar.Variable_coarser,
            label= 'Coarser', aa=True)
ax.plot(desiredVar.index, desiredVar.Variable_medium,
            label= 'Medium', aa=True)
ax.plot(desiredVar.index, desiredVar.Variable_finer,
            label= 'Finer', aa=True)

ax.legend(loc='best',fontsize='x-large')

plt.grid()
plt.autoscale(enable=True, tight=True)
plt.savefig('treatment/results/allMeshes.png')

fig, ax = plt.subplots(figsize=(9,6), dpi=300)
ax.errorbar(desiredVar.index, desiredVar.Variable_medium,
            gci*desiredVar.Variable_medium,
            errorevery = 5, elinewidth = 1,
            uplims = True, lolims = True, 
            lw=1.5, aa = True)

plt.grid()
plt.autoscale(enable=True, tight=True)
plt.savefig('treatment/results/mediumWithErrorbars.png')

fig, ax = plt.subplots(figsize=(9,6), dpi=300)
ax.errorbar(desiredVar.index, desiredVar.Variable_finer,
            gci*desiredVar.Variable_finer,
            errorevery = 5, elinewidth = 1,
            uplims = True, lolims = True, 
            lw=1.5, aa = True)

plt.grid()
plt.autoscale(enable=True, tight=True)
plt.savefig('treatment/results/finerWithErrorbars.png')