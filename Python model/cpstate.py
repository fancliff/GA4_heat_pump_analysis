# Simple State Fluid objects
import CoolProp as CP
import numpy as np
import ioutils as io
from tabulate import tabulate
deffl = None # Default fluid
Lname = True
Lunit = True
Lfluid = True
props = 'pThsqdAB'
fdict = {'L':CP.iphase_liquid,'V':CP.iphase_gas,'T':CP.iphase_twophase}
idict = {'p':'P','T':'T','h':'Hmass','s':'Smass','q':'Q'}
pdict = {'p':'p','T':'T','h':'hmass','s':'smass','q':'Q',
             'A':'isobaric_expansion_coefficient',
             'B':'isothermal_compressibility','d':'rhomass'}
Plist = ['Liquid','Supercritical','Supercritical (g)','Supercritical (l)',
         'Critical','Gas','Two phase']
cunit = {"p":'bar  ',"T":'K   ',"q":'-   ',"h":'kJ/kg ',"s":'kJ/kg.K ',
         "u":'kJ/kg ',"d":'kg/m3 ',"b":'kJ/kg ',"C":'', 't':'C   '}
facts = {"p":100000,"T":1,"q":1,"h":1000,"s":1000,"u":1000,"d":1,
         "b":1000,"C":None,"t":1}
forms = {'p':'%7.3f ','T':'%6.2f ','h':'%7.2f ','s':'%6.3f ','q':'%5.3f ',
         'u':'%6.1f ','d':'%8.3f ','b':'%7.2f ','C':'%s ', 't':'%7.3f '}

class Fluid(CP.AbstractState):
    """Note that this is just a wrapper around CoolProp AbstractState(),
    treating it as a Fluid rather than a State"""
    count = 0
    insts = []
    names = []
    def __new__(cls,name):
        instance = super().__new__(cls,"HEOS",name)
        return instance
    def __init__(self,name):
        self.id = Fluid.count
        self.label = name
        Fluid.count += 1
        Fluid.insts.append(self)
        Fluid.names.append(name)
        Tt = self.Ttriple()
        Pt = CP.CoolProp.PropsSI('ptriple',name)
        self.ref = State('ref',fluid=self,desc='Ref.')
        self.crt = State('crit',desc='Crit.')
        self.trl = State('pT',Pt,Tt,phase='L',desc='Trip. (L)')
        self.trv = State('pT',Pt,Tt,phase='V',desc='Trip. (V)')                
        return
    def satline(self,props='sT',npt=200,Tmin=None):
        """Creates arrays of properties along the saturation line (both liquid
        and vapour). props specifies the properties to be returned. These are 
        returned as numpy arrays within an "ioutils" Dictionary. If Tmin is not
        specified then it is set to the triple point temperature."""
        if not Tmin: Tmin = self.trl.T
        Tmax = self.crt.T
        prop = np.zeros((len(props),2*npt))
        T = np.linspace(Tmin,Tmax,npt)
        state = State('ref',fluid=self,desc='dummy')
        count = 0
        for t in T:
            state.update('TC',t,'f')
            for j,p in enumerate(props):
                prop[j,count] = getattr(state,p)
            count += 1
        T = np.flip(T)
        for t in T:
            state.update('TC',t,'g')
            for j,p in enumerate(props):
                prop[j,count] = getattr(state,p)
            count += 1
        output = io.Dict({'desc':'Satline for %s'%self.label})
        state = State.insts.pop(-1)
        del(state)
        State.count -= 1
        for j,p in enumerate(props):
            output.pack(p,prop[j])
        return output

    def delete (self,allstates=True):
        """Deletes the current instance and removes from the list of instances.
        If allstates is true and this is Fluid object then all thermodynamic 
        states using this fluid are also deleted."""
        if type(self) == Fluid and allstates:
            dellist = []
            for state in State.insts:
                if state.fluid == self:
                    dellist.append(state)
            for state in dellist:
                state.delete()
        idx = self.insts.index(self)
        for i in range (idx,len(self.insts)):
            self.insts[i].id -= 1
        state = self.insts.pop(idx)
        del(state)
        return

class State():
    """This creates thermodynamic states which can subsequently be updated"""
    count = 0
    insts = []
    deffl = None
    P0,T0 = 1.0E5, 298.15
    tablist = 'ptqhsbdC'
    delete = Fluid.delete
    def __init__(self,AB,propA=None,propB=None,desc='No name',fluid=None,phase=None):
        self.id = State.count
        State.count += 1
        State.insts.append(self)
        if fluid is not None:
            State.deffl = fluid
        self.fluid = State.deffl
        if self.fluid is None:
            print ('** No fluid has been selected **')
            return
        self.desc = desc
        self.update(AB,propA,propB,phase)
        return
    
    def update(self,AB,propA,propB,phase=None):
        """Updates the thermodynamic state. AB contains the two specified 
        properties (e.g., 'pT') which should be in alphabetical order [with the
        exception of 'C' which is always second. Current possibilities are as 
        listed in idict [top of file] plus 'C' which may be either 'f' (wet sat.)
        or 'g' (dry sat.). The variable phase may be specified ('L' = liuid, 
        'V' = vapour or 'T' = two-phase) to force the phase. Also, AB accepts the 
        special cases of 'ref' and 'crt' for reference condtions and the 
        critical point respectively."""
        if AB == 'crit':
            p = self.fluid.p_critical()
            T = self.fluid.T_critical()
            self.update('pT',p,T)
            return
        elif AB == 'ref':
            self.update('pT',State.P0,State.T0)
            return
        elif AB[1] == 'C':
            if propB == 'f': q = 0
            if propB == 'g': q = 1
            if AB[0] == 'p':
                CPinputs = CP.PQ_INPUTS
                propB = q
            if AB[0] == 'T':
                CPinputs = CP.QT_INPUTS
                propB, propA = propA, q
        else:
            CPinputs = eval("CP.%s%s_INPUTS" %(idict[AB[0]],idict[AB[1]]))
        if phase: self.fluid.specify_phase(fdict[phase])
        self.fluid.update(CPinputs,propA,propB)
        if phase: self.fluid.unspecify_phase()
        for p in props:
            expression = 'self.fluid.%s()'%pdict[p]
            setattr(self,p,eval(expression))
        self.C = Plist[self.fluid.phase()]
        self.b = self.h - State.T0 * self.s
        self.t = self.T - 273.15
        return

    def __str__ (self):
        str = "%s %s state " %(self.fluid.label,self.desc)
        for name in State.tablist:
            if hasattr (self, name):
                prop = getattr (self, name)
                fact = facts[name]
                if fact is not None:
                    prop /= fact
                if Lname:
                    str += "%s = " %name 
                str += forms[name] %prop
                if Lunit:
                    str += "%s  " %cunit[name]
        return str

    def tabline (self):
        """Generates one line for inclusion in a table of states."""            
        line = []
        if Lfluid:
            line.append(self.fluid.label)
        line.append(self.desc)        
        for name in State.tablist:
            str = ""
            if hasattr (self, name):
                prop = getattr (self, name)
                fact = facts[name]
                if fact is not None:
                    prop /= fact
                str = forms[name] %prop
            line.append(str)                    
        return line

    def tabhead (self):
        """Generates the header for inclusion in a table of states."""            
        head = []
        if Lfluid:
            head.append("Fluid")
        head.append("State")
        for name in State.tablist:
            str = name
            if str == 'C':
                str = 'Condition'
            str += "   \n%s" %cunit[name]
            head.append(str)                    
        return head

    def table (self):
        """Creates a table of states with all currently active states"""
        head = self.tabhead()
        data = []
        for state in self.insts:
            data.append(state.tabline())
        table = tabulate (data,headers=head,tablefmt="fancy_grid",numalign="decimal",floatfmt=".3f")
        return table

        



    
        
    



