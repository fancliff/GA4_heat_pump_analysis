import CoolProp.CoolProp as cp
import numpy as np
import matplotlib.pyplot as plt

def COP_analysis_Tevap_Tcond(fluid,condenser_p_drop,evaporator_p_drop,compressor_isen_eff,Tevap,Tcond,h_hsat_1,h_hsat_4):
    #calculates COP for an input of T4 and T2
    #evaporator entry and condenser exit refrigerant temperature respectively
    
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

    T2 = Tcond
    P2isen = cp.PropsSI ('P','T',T2,'S',s1,fluid)
    h2isen = cp.PropsSI ('H','T',T2,'S',s1,fluid)
    h2est = h1 + (h2isen-h1)/compressor_isen_eff
    T2est = cp.PropsSI ('T','H',h2est,'P',P2isen,fluid)
    s2est = cp.PropsSI ('S','H',h2est,'P',P2isen,fluid)
    s2 = s1 + (s2est-s1)*(T2est-T1)/(T2-T1) # assume compression is a straight line on T-S diagram
    h2 = cp.PropsSI ('H','T',T2,'S',s2,fluid)
    P2 = cp.PropsSI ('P','T',T2,'S',s2,fluid)

    P3 = P2 - condenser_p_drop
    h3 = h4 #throttle is isenthalpic
    T3 = cp.PropsSI ('T','P',P3,'H',h3,fluid)
    s3 = cp.PropsSI ('S','P',P3,'H',h3,fluid)

    win = h2 - h1 #note opposite to standard sign convention
    qout = h2 - h3 #note opposite to standard sign convention
    qin = h1 - h4
    COP = qout/win

    #end of circuit parameter calculations and outputs
    return COP


if __name__ == '__main__':

    #work in scientific units until plotting as CoolProp accepts scientific units
    
    # Set fluid name and key cycle properties

    fluid = 'R744'
    condenser_p_drop = 0.05e5 #[Pa]
    evaporator_p_drop = 0.1e5 #[Pa]
    compressor_isen_eff = 0.85
    Tevap = 13.5 + 273.15 #[K] 
    #experimental value for an ambient temperature of approx 18.5 degrees
    Tcond = 75 + 273.15 
    #65 degrees is reasonable hot water temperature for a home and sufficient deltaT for heat transfer
    h_hsat_1 = 5*1000 #[J/kg]
    h_hsat_4 = 50*1000 #[J/kg]

    #end of cycle inputs.




    #######
    #variable/s to be investigated (amend where required)
    #######
    condenser_p_drop_list = np.linspace(0,10,41) * 1e5 #convert bar to Pa
    evaporator_p_drop_list = np.linspace(0,1,41) * 1e5 #convert bar to Pa
    compressor_isen_eff_list = np.linspace(0.5,1,41)
    Tevap_list = np.linspace(-30,30,100) + 273.15 #convert degC to K
    Tcond_list = np.linspace(40,95,100) + 273.15 #convert degC to K
    h_hsat_1_list = np.linspace(-10,10,41) * 1000 #convert kJ/kg to J/kg
    h_hsat_4_list = np.linspace(-20,100,41) * 1000 #convert kJ/kg to J/kg



    #######
    # 1 variable plotting (number)
    #######



    size = len(h_hsat_4_list)
    COPs = np.zeros(size)
    for i in range(size):
        COPs[i] = COP_analysis_Tevap_Tcond(fluid,condenser_p_drop,evaporator_p_drop,compressor_isen_eff,Tevap,Tcond,h_hsat_1,h_hsat_4_list[i])

    plt.plot(h_hsat_4_list/1e3, COPs)
    plt.xlabel('H4 - Hsat4 (kJ/kg)')
    plt.ylabel('COP')
    #plt.savefig('COP_transcrit_h_hsat4.eps', format = 'eps')
    plt.show()
    


    #######
    # 2 variable plotting (both numbers)
    #######

    '''

    Tcondmat, Tevapmat = np.meshgrid(Tcond_list,Tevap_list)
    rows, cols = np.shape(Tcondmat)
    COPs_mat = np.zeros((rows,cols))
    for i in range(rows):
        for j in range(cols):
            try:
                COPs_mat[i,j] = COP_analysis_Tevap_Tcond(fluid,condenser_p_drop,evaporator_p_drop,compressor_isen_eff,Tevapmat[i,j],Tcondmat[i,j],h_hsat_1,h_hsat_4)
            except ValueError:
                print(Tevapmat[i,j]-273.15,', ',Tcondmat[i,j]-273.15)
                COPs_mat[i,j] = None



    fig = plt.figure()
    ax = plt.axes(projection='3d')
    ax.plot_surface(Tevapmat-278.15, Tcondmat-283.15, COPs_mat, cmap='viridis',edgecolor='green')
    plt.xlabel('T air [degC]') # 5 degrees below Tevap
    plt.ylabel('T hot water [degC]') # 10 degrees below Tcond
    ax.set_zlabel('COP')
    plt.show()

    fig = plt.figure()
    ax = plt.axes(projection='3d')
    ax.plot_surface(Tevapmat-273.15, Tcondmat-273.15, COPs_mat, cmap='viridis',edgecolor='green')
    plt.xlabel('T evap [degC]') 
    plt.ylabel('T cond max [degC]') 
    ax.set_zlabel('COP')
    plt.show()


    '''