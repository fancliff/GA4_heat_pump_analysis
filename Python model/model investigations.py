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
fluid_list = ['R134a','R32','R290','R410a','R22','R1234ZE','R1233ZD','R1234yf'] #R290 = n-propane, R744 = C02 (T crit = 30.98 degC)
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



size = len(fluid_list)
COPs = np.zeros(size)
for i in range(size):
    COPs[i] = COP_analysis_T4_T2(fluid_list[i],condenser_p_drop,evaporator_p_drop,compressor_isen_eff,T4,T2,h_hsat_1,h_hsat_3)

plt.bar(fluid_list, COPs, color = 'maroon', width = 0.4)
plt.xlabel("Refrigerant")
plt.ylabel("COP")
#plt.savefig('COP_fluid_T2_70.eps', format = 'eps')
plt.show()



#######
# 1 variable plotting (number)
#######



size = len(evaporator_p_drop_list)
COPs = np.zeros(size)
for i in range(size):
    COPs[i] = COP_analysis_T4_T2(fluid,condenser_p_drop,evaporator_p_drop_list[i],compressor_isen_eff,T4,T2,h_hsat_1,h_hsat_3)

plt.plot(evaporator_p_drop_list/1e5, COPs)
plt.xlabel("Evaporator Pressure Drop (bar)")
plt.ylabel("COP")
#plt.savefig('COP_evaporator_p_drop.eps', format = 'eps')
plt.show()



#######
# 2 variable plotting (both numbers)
#######



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
plt.show()



#######
# 2 variable plotting (one fluid, one number)
#######



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
plt.show()

