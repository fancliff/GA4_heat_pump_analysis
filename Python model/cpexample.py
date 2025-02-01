from cpstate import Fluid, State

CO2 = Fluid('CO2') # Set up CO2 as a the fluid
sat = CO2.satline() # Compute the saturation line for CO2
st1 = State('pT',1E5,300) # Create a thermodynamic state (CO2 assumed) at 1 bar 300K
tab = st1.table() # Create a table of all currently define thermodynamic states

# Now print out the table and the date for the saturation line

input ('Press RETURN to see table of currently defined states \n')

print (tab) # Note there are some reference and other states created when CO2 is initilised

input ('Press RETURN to see show saturation line dictionary (see also output in "CO2.sat" \n')

print (sat) # This is a funny AJW-style dictionary

# You can output the satuartion line  to a file (in this case, 'CO2.sat':

sat.write('CO2.sat')

input ('Press RETURN to see help for Fluid object \n')

help(CO2)

input ('Press RETURN again to see help for State object \n')

help(st1)



