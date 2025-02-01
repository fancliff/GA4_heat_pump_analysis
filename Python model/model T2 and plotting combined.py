#model with T2 and T4 as primary inputs

import CoolProp.CoolProp as cp
import numpy as np
import matplotlib.pyplot as plt

#work in scientific units until plotting as CoolProp accepts scientific units

# Read in fluid name and key cycle properties
print('')
while True:
    try:
        fluid = input ('Enter fluid name (see CoolProp docs for list): ')
        test = cp.PropsSI('S','T',298,'P',1e5,fluid)
        break
    except ValueError:
        print('Please enter a valid fluid from the CoolProp library.')
print('')


#change the below to variables when investigating COP against properties
while True:
    try:
        condenser_p_drop = float(input('Enter Condenser Pressure Drop in bar: ')) #convert to Pa
        if condenser_p_drop < 0:
            print("Condenser pressure drop must be >= 0.")
        else:
            break
    except ValueError:
        print("Please enter a number only.")
print('')
condenser_p_drop *= 1e5 #Convert to Pa

while True:
    try:
        evaporator_p_drop = float(input('Enter Evaporator Pressure Drop in bar: '))
        if evaporator_p_drop < 0:
            print("Evaporator pressure drop must be >= 0.")
        else:
            break
    except ValueError:
        print("Please enter a number only.")
print('')
evaporator_p_drop *= 1e5 #Convert to Pa

while True:
    try:
        compressor_isen_eff = float(input('Enter Compressor Isentropic Efficiency: '))
        if compressor_isen_eff <= 0 or compressor_isen_eff > 1:
            print("Compressor isentropic efficiency must be <= 1, and > 0")
        else:
            break
    except ValueError:
        print("Please enter a number only.")
print('')

#T4 from experiments can be approximated by a small offset below the outside air temperature
#Allowing adequate heat transfer in the evaporator
while True:
    try:
        T4 = float(input('Enter throttle exit temperature in Celsisus: '))
        if T4 < -50 or  T4 > 50:
            print("Throttle exit temperature must be between -50 and 50 degrees Celsius")
        else:
            break
    except ValueError:
        print("Please enter a number only.")
print('')
T4 += 273.15 #Convert to K

while True:
    try:
        T2 = float(input('Enter Compressor exit temperature in Celsius: '))
        if T2 < -50 or  T2 > 100:
            print("Compressor exit temperature must be between -50 and 100 degrees Celsius")
        else:
            break
    except ValueError:
        print("Please enter a number only.")
print('')
T2 += 273.15 #Convert to K

while True:
    try:
        h_hsat_1 = float(input('Enter enthalpy difference from dry saturated at point 1 (h1act-h1sat) (kJ/kg): '))
        
        if abs(h_hsat_1) > 30:
            print("Please make sure your answer is in kJ/kg not J/kg")
        else:
            break
    except ValueError:
        print("Please enter a number only.")
h_hsat_1 *= 1000 #convert to J/kg
#easier to detect user error in input units when using kJ/kg then convert to J/kg afterwards
print('')

while True:
    try:
        h_hsat_3 = float(input('Enter enthalpy difference from wet saturated at point 3 (h3act-h3sat) (kJ/kg): '))
        if abs(h_hsat_3) > 30:
            print("Please make sure your answer is in kJ/kg not J/kg")
        else:
            break
    except ValueError:
        print("Please enter a number only.")
h_hsat_3 *= 1000 #convert to J/kg
#easier to detect user error in input units when using kJ/kg then convert to J/kg afterwards
print('')

#end of variable user inputs.



# Find critcal-point and triple-point pressures
pc = cp.PropsSI (fluid,'pcrit')
pt = cp.PropsSI (fluid,'ptriple')

#calculates cycle parameters for an input of T4 and T2
#evaporator entry and condenser exit refrigerant temperature respectively

#We have to assume that there is no pressure drop in the condenser in the gas phase region
#We must do this because CoolProp cannot accept T-h as an input pair so instead 
# we must use the quality of 1 to find the gaseous saturation pressure for T2
# and assume that it is the same as the actual P2

#This is due to multiple and metastable states where particularly T-h inputs can result in
# a very high pressure and lower pressure solution. 
#RefProp can handle this but CoolProp unfortunately cannot

#The assumption that condenser pressure drop in the gas phase is 0 is reasonable as
# we know that pipe flow pressure drop is proportional to density

#then assume that all remaining condenser pressure drop occurs in the two phase region 
# so that overall condenser pressure drop is conserved

#start analysis at point 4 as we can confidently assume it is in 2-phase region always
#assume that point 4 is in the saturation region therefore can be specified by temperature
#P4 is independednt of quality in sat region so any value can be used (0 chosen here)
P4 = cp.PropsSI ('P','T',T4,'Q',0.0,fluid)

P1 = P4 - evaporator_p_drop
h1sat = cp.PropsSI ('H','P',P1,'Q',1.0,fluid)
h1 = h1sat + h_hsat_1
T1 = cp.PropsSI ('T','P',P1,'H',h1,fluid)
s1 = cp.PropsSI ('S','P',P1,'H',h1,fluid)

h2isen = cp.PropsSI ('H','T',T2,'S',s1,fluid)
h2 = h1 + (h2isen-h1)/compressor_isen_eff
P2sat = cp.PropsSI ('P','T',T2,'Q',0.0,fluid)
P2 = P2sat
s2 = cp.PropsSI ('S','P',P2,'H',h2,fluid)

P3 = P2 - condenser_p_drop
h3sat = cp.PropsSI ('H','P',P3,'Q',0.0,fluid)
h3 = h3sat + h_hsat_3
T3 = cp.PropsSI ('T','P',P3,'H',h3,fluid)
s3 = cp.PropsSI ('S','P',P3,'H',h3,fluid)

#throttle is isenthalpic
h4 = h3
s4 = cp.PropsSI ('S','P',P4,'H',h4,fluid)

win = h2 - h1 #note opposite to standard sign convention
qout = h2 - h3 #note opposite to standard sign convention
qin = h1 - h4
COP = qout/win

print('Cycle salient values')
print('')
print('P1: ', P1/1e5, ' bar')
print('T1: ', T1-273.15, ' C')
print('h1: ', h1/1000, ' kJ/kg')
print('s1: ', s1/1000, ' kJ/kg.K')

print('')
print('P2: ', P2/1e5, ' bar')
print('T2: ', T2-273.15, ' C')
print('h2: ', h2/1000, ' kJ/kg')
print('s2: ', s2/1000, ' kJ/kg.K')

print('')
print('P3: ', P3/1e5, ' bar')
print('T3: ', T3-273.15, ' C')
print('h3: ', h3/1000, ' kJ/kg')
print('s3: ', s3/1000, ' kJ/kg.K')

print('')
print('P4: ', P4/1e5, ' bar')
print('T4: ', T4-273.15, ' C')
print('h4: ', h4/1000, ' kJ/kg')
print('s4: ', s4/1000, ' kJ/kg.K')
print('')

print('win: ', win/1000, ' kJ/kg')
print('qout: ', qout/1000, ' kJ/kg')
print('COP: ', COP)

#end of circuit parameter calculations and outputs



# Create array of pressures with geometric distribution 
ps  = np.geomspace(pt,pc,500)
# Use the CoolProp routines to get T and s (note Q is same as dryness)
ts = cp.PropsSI ('T','P',ps,'Q',0.0,fluid)
sf = cp.PropsSI ('S','P',ps,'Q',0.0,fluid)
sg = cp.PropsSI ('S','P',ps,'Q',1.0,fluid)
hf = cp.PropsSI ('H','P',ps,'Q',0.0,fluid)
hg = cp.PropsSI ('H','P',ps,'Q',1.0,fluid)

# Plot both wet and dry sat together (may be a bit flat)
T_sat_line = np.concatenate((ts,np.flip(ts)[1:]))
s_sat_line = np.concatenate((sf,np.flip(sg)[1:]))
P_sat_line = np.concatenate((ps,np.flip(ps)[1:]))
h_sat_line = np.concatenate((hf,np.flip(hg)[1:]))


def plot_Ts(resolution):
    #plot state 1-2
    #assume that in the compressor ds/dh = constant
    #therefore: plot with h and s linearly spaced between h1-h2, and s1-s2, respectively
    h12 = np.linspace(h1,h2,resolution)
    s12 = np.linspace(s1,s2,resolution)
    T12 = cp.PropsSI('T','H',h12,'S',s12,fluid)
    plt.plot(s12/1000,T12-273.15, label = 'Compressor')
    
    #plot state 2-3
    #assume that in the condenser dP/dx = const - reasonable assumption from pipe flow theory
    #assume that rate of heat transfer and thus dh/dx = constant
    #realistically dP/dx is not constant and proportional to density 
    # but dh/dx is likely to vary similarly so the assumption is not bad
    #therefore: plot with h and P linearly spaced beteen h2-h3, and P2-P3, respectively
    h23 = np.linspace(h2,h3,resolution)
    P23 = np.linspace(P2,P3,resolution)
    s23 = cp.PropsSI('S','H',h23,'P',P23,fluid)
    T23 = cp.PropsSI('T','H',h23,'P',P23,fluid)
    plt.plot(s23/1000,T23-273.15, label = 'Condenser')
    
    #plot state 3-4
    #throttle can confidently assume is isenthalpic as no work and assumed adiabatic
    #assume pressure drop is linear in the throttle
    #therefore: plot with h = h3 = h4 and P linearly spaced between P3-P4
    h34 = np.ones(resolution) * h3
    P34 = np.linspace(P3,P4,resolution)
    s34 = cp.PropsSI('S','H',h34,'P',P34,fluid)
    T34 = cp.PropsSI('T','H',h34,'P',P34,fluid)
    plt.plot(s34/1000,T34-273.15, label = 'Throttle')
    
    #plot state 4-1
    #same assumptions as condenser (states 2-3)
    #assume that in the evaporator dP/dx = const - reasonable assumption from pipe flow theory
    #assume that rate of heat transfer and thus dh/dx = constant
    #realistically dP/dx is not constant and proportional to density 
    # but dh/dx is likely to vary similarly so the assumption is not bad
    #therefore: plot with h and P linearly spaced beteen h4-h1, and P4-P1, respectively
    h41 = np.linspace(h4,h1,resolution)
    P41 = np.linspace(P4,P1,resolution)
    s41 = cp.PropsSI('S','H',h41,'P',P41,fluid)
    T41 = cp.PropsSI('T','H',h41,'P',P41,fluid)
    plt.plot(s41/1000,T41-273.15, label = 'Evaporator')
    
    
    #plot saturation line and set up axes titles and scales
    plt.plot (s_sat_line/1000,T_sat_line-273.15, label = 'Saturation Line')
    plt.xlabel('Specific entropy (kJ/K.kg)')
    plt.ylabel('Temperature (deg. C)')
    plt.title ('Cycle Diagram and Saturation Line for %s'%fluid)
    #plt.grid(which="both")
    plt.legend(loc = 'upper left')
    plt.savefig('T_s_T2_opposite.eps', format = 'eps')
    plt.show()


def plot_Ph(resolution):
    #plot state 1-2
    #assume that in the compressor ds/dh = constant
    #therefore: plot with h and s linearly spaced between h1-h2, and s1-s2, respectively
    h12 = np.linspace(h1,h2,resolution)
    s12 = np.linspace(s1,s2,resolution)
    P12 = cp.PropsSI('P','H',h12,'S',s12,fluid)
    plt.plot(h12/1000,P12/1e5, label = 'Compressor')
    
    #plot state 2-3
    #assume that in the condenser dP/dx = const - reasonable assumption from pipe flow theory
    #assume that rate of heat transfer and thus dh/dx = constant
    #realistically dP/dx is not constant and proportional to density 
    # but dh/dx is likely to vary similarly so the assumption is not bad
    #therefore: plot with h and P linearly spaced beteen h2-h3, and P2-P3, respectively
    h23 = np.linspace(h2,h3,resolution)
    P23 = np.linspace(P2,P3,resolution)
    plt.plot(h23/1000,P23/1e5, label = 'Condenser')
    
    #plot state 3-4
    #throttle can confidently assume is isenthalpic as no work and assumed adiabatic
    #assume pressure drop is linear in the throttle
    #therefore: plot with h = h3 = h4 and P linearly spaced between P3-P4
    h34 = np.ones(resolution) * h3
    P34 = np.linspace(P3,P4,resolution)
    plt.plot(h34/1000,P34/1e5, label = 'Throttle')
    
    #plot state 4-1
    #same assumptions as condenser (states 2-3)
    #assume that in the evaporator dP/dx = const - reasonable assumption from pipe flow theory
    #assume that rate of heat transfer and thus dh/dx = constant
    #realistically dP/dx is not constant and proportional to density 
    # but dh/dx is likely to vary similarly so the assumption is not bad
    #therefore: plot with h and P linearly spaced beteen h4-h1, and P4-P1, respectively
    h41 = np.linspace(h4,h1,resolution)
    P41 = np.linspace(P4,P1,resolution)
    plt.plot(h41/1000,P41/1e5, label = 'Evaporator')
    
    
    #plot saturation line and set up axes titles and scales
    plt.plot (h_sat_line/1000,P_sat_line/1e5,)
    plt.yscale('log')
    plt.xlabel('Specific enthalpy (kJ/kg)')
    plt.ylabel('Pressure (bar)')
    plt.title ('Cycle Diagram and Saturation Line for %s'%fluid)
    #plt.grid(which="both")
    plt.legend(loc = 'upper left')
    plt.savefig('P_h_T2_opposite.eps', format = 'eps')
    plt.show()

print('')
while True:
    Ts_query = input('Would you like to plot a T-s diagram of the cycle (y/n)? ')
    if Ts_query == 'y':
        while True:
            try: 
                res = int(input('Please enter a resolution for T-s plot calculations, recommended 100-200: '))
                #check integer entered and >1
                test1 = 1/res
                test2 = 1/(res-1)
                plot_Ts(res)
                break
            except ValueError:
                print('Please enter an integer >1 only')
            except ZeroDivisionError:
                print('Please enter an integer >1 only')
        break
    elif Ts_query == 'n':
        break
    else:
        print('Please enter lowercase "y" or "n" only')

print('')
while True:
    Ph_query = input('Would you like to plot a P-h diagram of the cycle (y/n)? ')
    if Ph_query == 'y':
        while True:
            try: 
                res = int(input('Please enter a resolution (>1) for T-s plot calculations, recommended 100-200: '))
                #check integer entered and >1
                test1 = 1/res
                test2 = 1/(res-1)
                plot_Ph(res)
                break
            except ValueError:
                print('Please enter an integer >1 only ')
            except ZeroDivisionError:
                print('Please enter an integer >1 only ')
        break
    elif Ph_query == 'n':
        break
    else:
        print('Please enter lowercase "y" or "n" only')










########

#separate python file below for input investigations

########










#plotting of COP vs combinations of different inputs
import CoolProp.CoolProp as cp
import numpy as np
import matplotlib.pyplot as plt

#work in scientific units until plotting as CoolProp accepts scientific units

# Set fluid name and key cycle properties

fluid = 'R134a'
condenser_p_drop = 0.05e5 #[Pa]
evaporator_p_drop = 0.1e5 #[Pa]
compressor_isen_eff = 0.85
compressor_p_ratio = 3.5
#T4 from experiments can be approximated by a small (~5K) offset below the outside air temperature
#Allowing adequate heat transfer in the evaporator
T4 = 13.5 + 273.15 #[K]
T2 = 70 + 273.15 #Reasonable hot water temperature for a home
h_hsat_1 = 5*1000 #[J/kg]
h_hsat_3 = 5*1000 #[J/kg]

#end of cycle inputs.


def cycle_analysis_T4_pressure_ratio(fluid,condenser_p_drop,evaporator_p_drop,compressor_isen_eff,compressor_p_ratio,T4,h_hsat_1,h_hsat_3):
    #calculates COP for an input of T4 and the compressor pressure ratio
    
    #start analysis at point 4 as we can confidently assume it is in 2-phase region always
    #assume that point 4 is in the saturation region therefore can be specified by temperature
    #P4 is independednt of quality in sat region so any value can be used (0 chosen here)
    P4 = cp.PropsSI ('P','T',T4,'Q',0.0,fluid)

    P1 = P4 - evaporator_p_drop
    h1sat = cp.PropsSI ('H','P',P1,'Q',1.0,fluid)
    h1 = h1sat + h_hsat_1
    #T1 = cp.PropsSI ('T','P',P1,'H',h1,fluid)
    s1 = cp.PropsSI ('S','P',P1,'H',h1,fluid)

    P2 = P1 * compressor_p_ratio
    h2isen = cp.PropsSI ('H','P',P2,'S',s1,fluid)
    h2 = h1 + (h2isen-h1)/compressor_isen_eff
    #T2 = cp.PropsSI ('T','P',P2,'H',h2,fluid)
    #s2 = cp.PropsSI ('S','P',P2,'H',h2,fluid)

    P3 = P2 - condenser_p_drop
    h3sat = cp.PropsSI ('H','P',P3,'Q',0.0,fluid)
    h3 = h3sat + h_hsat_3
    #T3 = cp.PropsSI ('T','P',P3,'H',h3,fluid)
    #s3 = cp.PropsSI ('S','P',P3,'H',h3,fluid)

    #throttle is isenthalpic
    #h4 = h3
    #s4 = cp.PropsSI ('S','P',P4,'H',h4,fluid)

    win = h2 - h1 #note opposite to standard sign convention
    qout = h2 - h3 #note opposite to standard sign convention
    #qin = h1 - h4
    COP = qout/win

    #end of circuit parameter calculations and outputs
    return COP


def COP_analysis_T4_T2(fluid,condenser_p_drop,evaporator_p_drop,compressor_isen_eff,T4,T2,h_hsat_1,h_hsat_3):
    #calculates COP for an input of T4 and T2
    #evaporator entry and condenser exit refrigerant temperature respectively
    
    #We have to assume that there is no pressure drop in the condenser in the gas phase region
    #We must do this because CoolProp cannot accept T-h as an input pair so instead 
    # we must use the quality of 1 to find the gaseous saturation pressure for T2
    # and assume that it is the same as the actual P2
    
    #This is due to multiple and metastable states where particularly T-h inputs can result in
    # a very high pressure and lower pressure solution. 
    #RefProp can handle this but CoolProp unfortunately cannot
    
    #The assumption that condenser pressure drop in the gas phase is 0 is reasonable as
    # we know that pipe flow pressure drop is proportional to density
    
    #then assume that all remaining condenser pressure drop occurs in the two phase region 
    # so that overall condenser pressure drop is conserved
    
    #start analysis at point 4 as we can confidently assume it is in 2-phase region always
    #assume that point 4 is in the saturation region therefore can be specified by temperature
    #P4 is independednt of quality in sat region so any value can be used (0 chosen here)
    P4 = cp.PropsSI ('P','T',T4,'Q',0.0,fluid)

    P1 = P4 - evaporator_p_drop
    h1sat = cp.PropsSI ('H','P',P1,'Q',1.0,fluid)
    h1 = h1sat + h_hsat_1
    s1 = cp.PropsSI ('S','P',P1,'H',h1,fluid)

    h2isen = cp.PropsSI ('H','T',T2,'S',s1,fluid)
    h2 = h1 + (h2isen-h1)/compressor_isen_eff
    P2 = cp.PropsSI ('P','T',T2,'Q',0.0,fluid)

    P3 = P2 - condenser_p_drop
    h3sat = cp.PropsSI ('H','P',P3,'Q',0.0,fluid)
    h3 = h3sat + h_hsat_3

    win = h2 - h1 #note opposite to standard sign convention
    qout = h2 - h3 #note opposite to standard sign convention
    COP = qout/win

    #end of circuit parameter calculations and outputs
    return COP


#######
#variable/s to be investigated (amend where required)
#######
fluid_list = ['R134a','R32','R290','R410a','R407C','R22','R1234ZE'] #R290 = n-propane, R744 = C02 (T crit = 30.98 degC)
condenser_p_drop_list = np.linspace(0,10,41) * 1e5 #convert bar to Pa
evaporator_p_drop_list = np.linspace(0,1,41) * 1e5 #convert bar to Pa
compressor_isen_eff_list = np.linspace(0.5,1,41)
compressor_p_ratio_list = np.linspace(1.1,10,51)
T4_list = np.arange(-20,31,1) + 273.15 #convert degC to K
T2_list = np.arange(50,71,1) + 273.15 #convert degC to K
h_hsat_1_list = np.linspace(-10,10,41) * 1000 #convert kJ/kg to J/kg
h_hsat_3_list = np.linspace(-10,10,41) * 1000 #convert kJ/kg to J/kg

#######
# 1 variable plotting (fluid)
#######

'''

size = len(fluid_list)
COPs = np.zeros(size)
for i in range(size):
    COPs[i] = COP_analysis_T4_T2(fluid_list[i],condenser_p_drop,evaporator_p_drop,compressor_isen_eff,T4,T2,h_hsat_1,h_hsat_3)

plt.bar(fluid_list, COPs, color = 'maroon', width = 0.4)
plt.xlabel("Refrigerant")
plt.ylabel("COP")
#plt.savefig('COP_fluid_T2_70.eps', format = 'eps')
plt.show()

'''

#######
# 1 variable plotting (number)
#######

'''

size = len(evaporator_p_drop_list)
COPs = np.zeros(size)
for i in range(size):
    COPs[i] = COP_analysis_T4_T2(fluid,condenser_p_drop,evaporator_p_drop_list[i],compressor_isen_eff,T4,T2,h_hsat_1,h_hsat_3)

plt.plot(evaporator_p_drop_list/1e5, COPs)
plt.xlabel("Evaporator Pressure Drop (bar)")
plt.ylabel("COP")
#plt.savefig('COP_evaporator_p_drop.eps', format = 'eps')
#plt.show()

'''

#######
# 2 variable plotting (both numbers)
#######

'''

T2mat, T4mat = np.meshgrid(T2_list,T4_list)
rows, cols = np.shape(T2mat)
COPs_mat = np.zeros((rows,cols))
for i in range(rows):
    for j in range(cols):
        COPs_mat[i,j] = COP_analysis_T4_T2(fluid,condenser_p_drop,evaporator_p_drop,compressor_isen_eff,T4mat[i,j],T2mat[i,j],h_hsat_1,h_hsat_3)

fig = plt.figure()
ax = plt.axes(projection='3d')
ax.plot_surface(T4mat, T2mat, COPs_mat, cmap='viridis',edgecolor='green')
plt.xlabel('T4 [degC]')
plt.ylabel('T2 [degC]')
ax.set_zlabel('COP')
#plt.show()

'''

#######
# 2 variable plotting (one fluid, one number)
#######

'''

size_fluid = len(fluid_list)
size_var = len(T4_list)
COPs_mat = np.zeros((size_fluid,size_var))
for i in range(size_fluid):
    for j in range(size_var):
        COPs_mat[i,j] = COP_analysis_T4_T2(fluid_list[i],condenser_p_drop,evaporator_p_drop,compressor_isen_eff,T4_list[j],T2,h_hsat_1,h_hsat_3)

for i in range(size_fluid):
    plt.plot(T4_list-273.15,COPs_mat[i,:],label = fluid_list[i])
plt.xlabel('T4 [degC]')
plt.ylabel('COP')
plt.legend()
#plt.savefig('COP_T4_fluid.eps', format = 'eps')
#plt.show()

'''

