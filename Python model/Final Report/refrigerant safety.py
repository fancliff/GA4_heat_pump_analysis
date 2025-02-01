import CoolProp.CoolProp as cp
import numpy as np
import matplotlib.pyplot as plt


fluid_list = ['R134a','R32','R290','R22','R1234ZE','R1234yf','R1233ZD','R744']
GWP_list = [1430, 675, 3, 1810, 6, 4, 1, 1]
ODP_list = [0, 0, 0, 0.05, 0, 0, 0, 0]
flam_list = [1, 1.5, 3, 1, 1.5, 1.5, 1, 1] # 2L = 1.5 for this metric from ASHRAE ratings
tox_list = [0, 0, 0, 0, 0, 0, 0, 0] # A = 0, B = 1 from ASHRAE ratings
P_max_Tw_65 = [23.6, 54.2, 28.5, 33.2, 18.0, 22.7, 5.8, 111.4]
P_max_Tw_35 = [11.6, 27.9, 15.3, 17.3, 8.8, 11.5, 2.5, 75.8]

'''
P_max_Tw_35 = []
P_max_Tw_65 = []
for i in range(len(fluid_list)-1):
    P_max_Tw_65.append(cp.PropsSI('P','T',75+273.15,'Q',0.5,fluid_list[i]))
    P_max_Tw_35.append(cp.PropsSI('P','T',45+273.15,'Q',0.5,fluid_list[i]))
P_max_Tw_65.append(111.4e5)
P_max_Tw_35.append(75.8e5)
print(np.round(10*np.array(P_max_Tw_35)/1e5)/10)
print(np.round(10*np.array(P_max_Tw_65)/1e5)/10)
'''

plt.bar(fluid_list, GWP_list, color = 'maroon', width = 0.4)
plt.xlabel('Refrigerant')
plt.ylabel('GWP')
plt.yscale('log')
plt.setp(plt.gca().get_xticklabels(), rotation=90, ha='center')
plt.tight_layout()
#plt.savefig('GWP_fluid.eps', format = 'eps')
plt.show()

plt.bar(fluid_list, ODP_list, color = 'maroon', width = 0.4)
plt.xlabel('Refrigerant')
plt.ylabel('ODP - relative to R11')
plt.setp(plt.gca().get_xticklabels(), rotation=90, ha='center')
plt.tight_layout()
#plt.savefig('ODP_fluid.eps', format = 'eps')
plt.show()

plt.bar(fluid_list, flam_list, color = 'maroon', width = 0.4)
plt.xlabel('Refrigerant')
plt.ylabel('ASHRAE Flammability Level')
plt.setp(plt.gca().get_xticklabels(), rotation=90, ha='center')
plt.tight_layout()
plt.savefig('flam_fluid.eps', format = 'eps')
plt.show()

x = np.arange(len(fluid_list))
bar_width = 0.4
plt.bar(x-bar_width/2, P_max_Tw_35, color = 'royalblue', width = bar_width, label = 'Twater = 35 degC')
plt.bar(x+bar_width/2, P_max_Tw_65, color = 'lightcoral', width = bar_width, label = 'Twater = 65 degC')
plt.xticks(x,fluid_list)
plt.xlabel('Refrigerant')
plt.ylabel('Maximum Cycle Pressure (bar)')
#plt.yscale('log')
plt.legend(loc = 'upper left', ncols = 1)
plt.setp(plt.gca().get_xticklabels(), rotation=90, ha='center')
plt.tight_layout()
#plt.ylim(bottom = 1)
plt.grid(which='major', axis = 'y', color='lightgrey', linestyle='-')
#plt.grid(which='minor', axis = 'y', color='lightgrey', linestyle='--')
#plt.savefig('Cycle_Pmax_fluid.eps', format = 'eps')
plt.show()