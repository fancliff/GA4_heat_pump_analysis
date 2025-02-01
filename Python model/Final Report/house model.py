import CoolProp.CoolProp as cp
import numpy as np
import numba as nb
import matplotlib.pyplot as plt
from subcrit_investigations import COP_analysis_Tevap_Tcond as COP_subcrit
from transcrit_investigations import COP_analysis_Tevap_Tcond as COP_transcrit
import time

#work in scientific units until plotting as CoolProp accepts scientific units

#set basic house parameters

data_path1 = 'C:\\Users\Freddie\OneDrive - University of Cambridge\Engineering\GA4\Python model\Final Report\\Mean_temperature_cambridge_2006.txt'
data_path2 = 'C:\\Users\Freddie\OneDrive - University of Cambridge\Engineering\GA4\Python model\Final Report\\uk_daily_avg_carbon_intensity_2023.txt'


house_temp = 18 # stable house temp thoughout the year
# no heating if ambient exceeds this value
house_U = 322 # heat transfer coefficient of the house W/K - Q = U*deltaT


with open(data_path1,'r') as f:
    lines = f.readlines()
air_temps = np.array([float(line.strip()) for line in lines]) # degrees Celsius

with open(data_path2,'r') as f:
    lines = f.readlines()
CO2_intensities = np.array([float(line.strip()) for line in lines]) # gCO2/kWh

house_temps = np.zeros(len(air_temps)) + house_temp # degrees Celsius

Qs_reqd = np.array([(house - air)*house_U if air < house_temp else 0 for air, house in zip(air_temps, house_temps)])

CO2_intens_boiler = 204.7e-6 #kgCO2/Wh of heat input to house from boiler
#assumes: 
#   gross CV 14.6kWh/kg
#   2.75 kgCO2/kg natural gas i.e ~100% methane
#   boiler efficiency of 0.92 (constant for all hot water temps)

CO2_boiler = Qs_reqd*CO2_intens_boiler*24

# for U = 322, house temp = 18:
# mean Q reqd is 2200
# sum Q reqd is 805966
# 60th percentile is 2608
# 70th percentile is 3220
# 80th percentile is 4064
# 90th percentile is 4862
# 100th percentile is 6504
# assuming COP approximately 4, and to cover up to the 80th percentile:
# pick a compressor power of 1kW for the undersized test
comp_W_cap = 1000

# define hot water temperature for house heating system
# 35 degrees C for underfloor, 65 for radiators usually
T_hotwater = 35 + 273.15 # convert to K

# T evaporator is 5 degrees below ambient air temperature from experiments
# approximate T condenser as 10 degrees above required hot water temperature to allow for adequate heat transfer
# h_hsat_1 is approximately 2kJ/kg from experiments (experiments on subcritical cycle)
# (average of 2.5degrees of superheating measured at evap exit)
# approximate that point 3 is on the saturation line for the subcritical cycles

fluid_list = ['R134a','R32','R290','R22','R1234ZE','R1234yf','R1233ZD'] #R290 = n-propane
COPs_list_subcrit = []
for i in range(len(fluid_list)):
    COPs_list_subcrit.append([COP_subcrit(fluid_list[i],0.05e5,0.1e5,0.85,air+268.15,T_hotwater+10,2e3,0) if air < house_temp else 1 for air in air_temps])

COPs_transcrit = []
for i in range(len(air_temps)):
    air = air_temps[i]
    if air < house_temp:
        while True:
            try:
                #approximate that h_hsat_4 = 35kJ/kg - unable to find a guide value in literature
                COPs_transcrit.append(COP_transcrit('R744',0.05e5,0.1e5,0.85,air+268.15,T_hotwater+10,2e3,35e3))
                break
            except ValueError:
                # if CoolProp fails at calculation try an air temperature 0.01 degrees lower until calculation success
                air -= 0.01
                #print('fail')
    else:
        # if air temp is greater than house temp then no heating required
        # so need not bother calculate COP and any value can be used
        COPs_transcrit.append(1)


E_dmd_list_subcrit = [] # in W required throughout the day
CO2_list_subcrit = [] # in kgCO2 per day
for i in range(len(COPs_list_subcrit)):
    E_dmd = [Q/COP if Q/COP <= comp_W_cap else comp_W_cap*(1-COP)+Q for Q,COP in zip(Qs_reqd,COPs_list_subcrit[i])]
    E_dmd_list_subcrit.append(E_dmd)
    CO2_list_subcrit.append([E*C*24/1e6 for E,C in zip(E_dmd,CO2_intensities)]) 

E_dmd_transcrit = [Q/COP if Q/COP <= comp_W_cap else comp_W_cap*(1-COP)+Q for Q,COP in zip(Qs_reqd,COPs_transcrit)]
CO2_transcrit = [E*C*24/1e6 for E,C in zip(E_dmd_transcrit,CO2_intensities)] 

E_dmd_list_subcrit_nocap = [] # in W required throughout the day
CO2_list_subcrit_nocap = [] # in kgCO2 per day
for i in range(len(COPs_list_subcrit)):
    E_dmd = [Q/COP for Q,COP in zip(Qs_reqd,COPs_list_subcrit[i])]
    E_dmd_list_subcrit_nocap.append(E_dmd)
    CO2_list_subcrit_nocap.append([E*C*24/1e6 for E,C in zip(E_dmd,CO2_intensities)])

E_dmd_transcrit_nocap = [Q/COP for Q,COP in zip(Qs_reqd,COPs_transcrit)]
CO2_transcrit_nocap = [E*C*24/1e6 for E,C in zip(E_dmd_transcrit_nocap,CO2_intensities)] 

days = [i for i in range(len(air_temps))]

'''

plt.plot(days,CO2_intensities)
plt.xlabel('Day of the year')
plt.ylabel('UK grid CO2 intensity [gCO2/kWh]')
#plt.savefig('CO2_intensity_2023.eps', format = 'eps')
plt.show()

'''

TotQs = np.sum(Qs_reqd)
SPF_transcrit = TotQs/np.sum(np.array(E_dmd_transcrit))
SPF_transcrit_nocap = TotQs/np.sum(np.array(E_dmd_transcrit_nocap))
SPF_list_subcrit = []
SPF_list_subcrit_nocap = []
for i in range(len(fluid_list)):
    SPF_list_subcrit.append(TotQs/np.sum(np.array(E_dmd_list_subcrit[i])))
    SPF_list_subcrit_nocap.append(TotQs/np.sum(np.array(E_dmd_list_subcrit_nocap[i])))

print(SPF_transcrit)
for i in range(len(fluid_list)):
    print(SPF_list_subcrit[i])
    
print('')

print(SPF_transcrit_nocap)
for i in range(len(fluid_list)):
    print(SPF_list_subcrit_nocap[i])



print(sum(CO2_transcrit))
for i in range(len(fluid_list)):
    print(sum(CO2_list_subcrit[i]))
print(sum(CO2_boiler))

plt.plot(days,E_dmd_transcrit,label = 'Transcrit R744')
for i in range(len(fluid_list)):
    plt.plot(days,E_dmd_list_subcrit[i],label = fluid_list[i])
plt.xlabel('Day of the year')
plt.ylabel('Energy demand [W]')
plt.legend()
#plt.savefig('Edmd_daily_fluid_35.eps', format = 'eps')
plt.show()

plt.plot(days,CO2_transcrit,label = 'Transcrit R744')
for i in range(len(fluid_list)):
    plt.plot(days,CO2_list_subcrit[i],label = fluid_list[i])
plt.plot(days,CO2_boiler,label = 'boiler')
plt.xlabel('Day of the year')
plt.ylabel('CO2 emissions [kg/day]')
plt.legend()
#plt.savefig('CO2_daily_fluid_35.eps', format = 'eps')
plt.show()

plt.bar('Transcrit R744',sum(CO2_transcrit),color = 'maroon', width = 0.4)
for i in range(len(fluid_list)):
    plt.bar(fluid_list[i],sum(CO2_list_subcrit[i]),color = 'maroon', width = 0.4)
plt.bar('Boiler',sum(CO2_boiler),color = 'maroon', width = 0.4)
plt.xlabel('Fluid')
plt.ylabel('CO2 emissions [kg/year]')
plt.setp(plt.gca().get_xticklabels(), rotation=90, ha='center')
plt.tight_layout()
#plt.savefig('CO2_total_fluid_35.eps', format = 'eps')
plt.show()

######
# no cap below
######

print('')
print(sum(CO2_transcrit_nocap))
for i in range(len(fluid_list)):
    print(sum(CO2_list_subcrit_nocap[i]))
print(sum(CO2_boiler))

plt.plot(days,E_dmd_transcrit_nocap,label = 'Transcrit R744')
for i in range(len(fluid_list)):
    plt.plot(days,E_dmd_list_subcrit_nocap[i],label = fluid_list[i])
plt.xlabel('Day of the year')
plt.ylabel('Energy demand [W]')
plt.legend()
#plt.savefig('Edmd_daily_fluid_nocap_35.eps', format = 'eps')
plt.show()

plt.plot(days,CO2_transcrit_nocap,label = 'Transcrit R744')
for i in range(len(fluid_list)):
    plt.plot(days,CO2_list_subcrit_nocap[i],label = fluid_list[i])
plt.plot(days,CO2_boiler,label = 'boiler')
plt.xlabel('Day of the year')
plt.ylabel('CO2 emissions [kg/day]')
plt.legend()
#plt.savefig('CO2_daily_fluid_nocap_35.eps', format = 'eps')
plt.show()

plt.bar('Transcrit R744',sum(CO2_transcrit_nocap),color = 'maroon', width = 0.4)
for i in range(len(fluid_list)):
    plt.bar(fluid_list[i],sum(CO2_list_subcrit_nocap[i]),color = 'maroon', width = 0.4)
plt.bar('Boiler',sum(CO2_boiler),color = 'maroon', width = 0.4)
plt.xlabel('Fluid')
plt.ylabel('CO2 emissions [kg/year]')
plt.setp(plt.gca().get_xticklabels(), rotation=90, ha='center')
plt.tight_layout()
#plt.savefig('CO2_total_fluid_nocap_35.eps', format = 'eps')
plt.show()

