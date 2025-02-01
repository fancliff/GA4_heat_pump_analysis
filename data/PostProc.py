import CoolProp.CoolProp as CP
import matplotlib.pyplot as plt
import numpy as np

# Patm = float(input("Enter Patm for this run.")) * 10e5
Patm = 10e5
zero_c_in_k = 273.15
const_power = 176 # power draw of fan etc
#const_power = 0

tim = []   # Initialise lists for input variables
T1w = []
T2w = []
T1a = []
T2a = []
T1r = []
T2r = []
T3r = []
T4r = []
P1 = []
P2 = []
P4 = []
Pow = []
Qc = []
#initialise lists for calculation variables
COPext = []
COPext_noaux = []
COPint = []
deltahw = []
h1r = []
h2r = []
h3r = []
P3 = [] #condenser exit pressure assuming dryness fraction is zero
evap_pdrop = []
evap_superheat = []

file_name = input("Enter data file name: ") # Prompt for file name and open file
data_file = open(file_name,"r")
title = data_file.readline() # Read first header line
props = data_file.readline() # Read second header line

# Now read in data line by line
for line in data_file:
    vals = line.split() # Split each line into "words"
    if vals[0] == "#":  #error handling - logging file contains repeated title lines starting with #
        continue
    tim.append(eval(vals[0]))               # Convert words (strings) to floating point
    T1w.append(eval(vals[1])+zero_c_in_k)   # and append to arrays
    T2w.append(eval(vals[2])+zero_c_in_k)   # eval() func converts from scientific to float
    T1a.append(eval(vals[3])+zero_c_in_k)
    T2a.append(eval(vals[4])+zero_c_in_k)
    T1r.append(eval(vals[5])+zero_c_in_k)
    T2r.append(eval(vals[6])+zero_c_in_k)
    T3r.append(eval(vals[7])+zero_c_in_k)
    T4r.append(eval(vals[8])+zero_c_in_k)
    P1.append(eval(vals[9]))
    P2.append(eval(vals[10]))
    P4.append(CP.PropsSI('P', 'T', T4r[-1], 'Q', 0.5, "R134a")/1e5) # P4 lies in saturation region
    Qc.append(eval(vals[12])/(1000*60))     # Convert to m3/s (recorded in L/min)
    Pow.append(eval(vals[11])*100)          # Convert back to Watts (stored in W/100)
    deltahw.append(CP.PropsSI("H","T",T2w[-1],"P",Patm,"water") - CP.PropsSI("H","T",T1w[-1],"P",Patm,"water")) # water enthalpy change
    h1r = CP.PropsSI("H","T",T1r[-1],"P",P1[-1]*1e5,"R134a")
    h2r = CP.PropsSI("H","T",T2r[-1],"P",P2[-1]*1e5,"R134a")
    h3r = CP.PropsSI("H","T",T3r[-1],"Q",0,"R134a")
    #two options to find h3
    #   assume dryness fraction is 0
    #   assume no pressure loss in condenser (worse assumption)
    P3.append(CP.PropsSI("P","T",T3r[-1],"Q",0,"R134a")/1e5) 
    #assume quality (dryness fraction) is 0 at condenser exit
    if Pow[-1] > const_power + 200:    # check compressor running also avoiding divide by zero
        COPext.append(deltahw[-1] * Qc[-1] * CP.PropsSI("D","T",(T2w[-1]+T1w[-1])/2,"P",Patm,"water") / (Pow[-1]-const_power))
        COPext_noaux.append(deltahw[-1] * Qc[-1] * CP.PropsSI("D","T",(T2w[-1]+T1w[-1])/2,"P",Patm,"water") / (Pow[-1]))
        COPint.append((h2r-h3r)/(h2r-h1r))
    else:
        COPext.append(0.0)
        COPext_noaux.append(0.0)
        COPint.append(0.0)

    evap_pdrop.append(P4[-1]-P1[-1])
    evap_superheat.append(T1r[-1] - CP.PropsSI('T', 'P', P4[-1]*1e5, 'Q', 1, "R134a"))

"""

figure1 = plt.figure()
plt.plot(tim[125:225],Pow[125:225],label = "Electrical Power In")
plt.xlabel("Time (s)")
plt.ylabel("Power (W)")
plt.legend()
plt.show()
figure1.savefig('POW_21_02.eps', format='eps')

"""

figure1 = plt.figure()
plt.plot(tim,COPint,label="internal")
plt.plot(tim,COPext,label="external w auxillaries")
plt.plot(tim,COPext_noaux,label="external w/out auxillaries")
plt.xlabel("Time (s)")
plt.ylabel("COP")
plt.ylim(top = 5.5)
plt.legend()
plt.show()
figure1.savefig('3COPs_21_27.eps', format='eps')

figure2 = plt.figure()
plt.plot(tim,T1w,label="T1w")
plt.plot(tim,T2w,label="T2w")
plt.plot(tim,T3r,label="T3r")
plt.xlabel("Time (s)")
plt.ylabel("Temperature (K)")
plt.legend(loc="upper left")
plt.show()
figure2.savefig('CondenserTemps_21_27.eps', format='eps')

figure3 = plt.figure()
plt.plot(tim,COPext,label="COP external")
plt.plot(tim,np.subtract(T3r,T1w),label="Condenser entry deltaT")
plt.xlabel("Time (s)")
plt.ylabel("Temperature (K), COP")
plt.legend(loc="lower right")
plt.show()
figure3.savefig('CondenserTemps&COP_21_27.eps', format='eps')

