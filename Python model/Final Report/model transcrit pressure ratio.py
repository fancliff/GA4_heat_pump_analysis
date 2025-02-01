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

#Tevap from experiments can be approximated by a small offset below the outside air temperature
#Allowing adequate heat transfer in the evaporator
while True:
    try:
        Tevap = float(input('Enter evaporator temperature in Celsisus: '))
        if Tevap < -70 or  Tevap > 30:
            print("Evaporator temperature must be between -70 and 70 degrees Celsius")
        else:
            break
    except ValueError:
        print("Please enter a number only.")
print('')
Tevap += 273.15 #Convert to K

while True:
    try:
        compressor_p_ratio = float(input('Enter Compressor Pressure Ratio: '))
        if compressor_p_ratio <= 1:
            print("Compressor pressure ratio must be > 1.")
        else:
            break
    except ValueError:
        print("Please enter a number only.")
print('')

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
        h_hsat_4 = float(input('Enter enthalpy difference from wet saturated at point 4 (h4act-h4sat) (kJ/kg): '))
        
        if abs(h_hsat_4) > 50:
            print("Please make sure your answer is in kJ/kg not J/kg")
        else:
            break
    except ValueError:
        print("Please enter a number only.")
h_hsat_4 *= 1000 #convert to J/kg
#easier to detect user error in input units when using kJ/kg then convert to J/kg afterwards
print('')


#end of variable user inputs.



# Find critcal-point and triple-point pressures
pc = cp.PropsSI (fluid,'pcrit')
pt = cp.PropsSI (fluid,'ptriple')
Tc = cp.PropsSI (fluid,'Tcrit')
Tt = cp.PropsSI (fluid,'Ttriple')

#start analysis at point 4
hsat4 = cp.PropsSI ('H','T',Tevap,'Q',0.0,fluid)
h4 = hsat4 + h_hsat_4
Psat4 = cp.PropsSI ('P','T',Tevap,'Q',0.0,fluid)
P4 = Psat4 #assumption that minimal pressure drop if point 4 lies outside the saturation region
T4 = cp.PropsSI ('T','P',P4,'H',h4,fluid)
s4 = cp.PropsSI ('S','P',P4,'H',h4,fluid)


P1 = P4 - evaporator_p_drop
h1sat = cp.PropsSI ('H','P',P1,'Q',1.0,fluid)
h1 = h1sat + h_hsat_1
T1 = cp.PropsSI ('T','P',P1,'H',h1,fluid)
s1 = cp.PropsSI ('S','P',P1,'H',h1,fluid)

P2 = P1 * compressor_p_ratio
h2isen = cp.PropsSI ('H','P',P2,'S',s1,fluid)
h2 = h1 + (h2isen-h1)/compressor_isen_eff
T2 = cp.PropsSI ('T','P',P2,'H',h2,fluid)
s2 = cp.PropsSI ('S','P',P2,'H',h2,fluid)

P3 = P2 - condenser_p_drop
h3 = h4 #throttle is isenthalpic
T3 = cp.PropsSI ('T','P',P3,'H',h3,fluid)
s3 = cp.PropsSI ('S','P',P3,'H',h3,fluid)

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
    #plt.savefig('T-s.eps', format = 'eps')
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
    #plt.savefig('P-h.eps', format = 'eps')
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