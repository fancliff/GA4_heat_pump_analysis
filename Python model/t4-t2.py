#######
# T4 and T2 as inputs
#######
P4 = cp.PropsSI ('P','T',T4,'Q',0.0,fluid)

P1 = P4 - evaporator_p_drop
h1sat = cp.PropsSI ('H','P',P1,'Q',1.0,fluid)
h1 = h1sat + h_hsat_1
s1 = cp.PropsSI ('S','P',P1,'H',h1,fluid)

h2isen = cp.PropsSI ('H','T',T2,'S',s1,fluid)
h2 = h1 + (h2isen-h1)/compressor_isen_eff
#######
P2 = cp.PropsSI ('P','T',T2,'H',h2,fluid) # error on this line
#######

P3 = P2 - condenser_p_drop
h3sat = cp.PropsSI ('H','P',P3,'Q',0.0,fluid)
h3 = h3sat + h_hsat_3

#######
# T4 and T3 as inputs
#######
P4 = cp.PropsSI ('P','T',T4,'Q',0.0,fluid)

P1 = P4 - evaporator_p_drop
h1sat = cp.PropsSI ('H','P',P1,'Q',1.0,fluid)
h1 = h1sat + h_hsat_1
s1 = cp.PropsSI ('S','P',P1,'H',h1,fluid)

h3sat = cp.PropsSI ('H','T',T3,'Q',0.0,fluid)
h3 = h3sat + h_hsat_3
######
P3 = cp.PropsSI ('P','T',T3,'H',h3,fluid) # error on this line
######

P2 = P3 + condenser_p_drop
h2isen = cp.PropsSI ('H','P',P2,'S',s1,fluid)
h2 = h1 + (h2isen-h1)/compressor_isen_eff

P3 = P2 - condenser_p_drop
h3sat = cp.PropsSI ('H','P',P3,'Q',0.0,fluid)
h3 = h3sat + h_hsat_3