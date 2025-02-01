#!/usr/bin/env python3

# Script to plot the saturation line of a fluid on a T-S diagram
#
###############################################################
# Import the CoolProp property evaluation and plotting modules

import CoolProp.CoolProp as cp
import numpy as np
import matplotlib.pyplot as plt

# Read in fluid name and calculate critical and triple point pressures
fluid = input ('Enter fluid name (see CoolProp docs for list): ')
ofile = open ('%s.sat'%fluid,'w')
ofile.write('# Saturation line for %s\n'%fluid)
ofile.write('#  p (bar)      Tsat (C)     sf (kJ/kgK)   sg (kJ/kgK)\n')

# Find critcal-point and triple-point pressures
pc = cp.PropsSI (fluid,'pcrit')
pt = cp.PropsSI (fluid,'ptriple')

# Create array of pressures with geometric distribution 
p  = np.geomspace(pt,pc,500)
# Use the CoolProp routines to get T and s (note Q is same as dryness)
ts = cp.PropsSI ('T','P',p,'Q',0.0,fluid) - 273.15
sf = cp.PropsSI ('S','P',p,'Q',0.0,fluid) / 1000
sg = cp.PropsSI ('S','P',p,'Q',1.0,fluid) / 1000
hf = cp.PropsSI ('H','P',p,'Q',0.0,fluid) / 1000
hg = cp.PropsSI ('H','P',p,'Q',1.0,fluid) / 1000

# Output to a file for future use (e.g., with `gnuplot')
fmt = 4*'%11.4E   ' + '\n'
for i in range (len(p)):
    ofile.write(fmt%(p[i]/1E5,ts[i],sf[i],sg[i]))
ofile.close()

# Plot both wet and dry sat together (may be a bit flat)
T = np.concatenate((ts,np.flip(ts)[1:]))
s = np.concatenate((sf,np.flip(sg)[1:]))
P = np.concatenate((p,np.flip(p)[1:]))
h = np.concatenate((hf,np.flip(hg)[1:]))

plt.plot (s,T)
plt.xlabel('Specific entropy (kJ/K.kg)')
plt.ylabel('Temperature (deg. C)')
plt.title ('Saturation Line for %s'%fluid)
plt.show()

plt.plot (h,P)
plt.yscale("log")
plt.xlabel('Specific enthalpy (kJ/kg)')
plt.ylabel('Pressure (bar)')
plt.title ('Saturation Line for %s'%fluid)
#plt.grid(which="both")
plt.show()