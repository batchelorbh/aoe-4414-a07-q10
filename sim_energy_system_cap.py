#!/usr/bin/env python
# sim_energy_system_cap.py
#
# Simulates a capacitor-based energy system and outputs voltage and time data
#   to a CSV file
#
# Usage: python3 sim_energy_system_cap.py sa_m2 eff voc c_f r_esr q0_c
#                                         p_on_w v_thresh dt_s dur_s
#
# Written by Blake Batchelor, batchelorbh@vt.edu
# Other contributors: none
#
# Parameters:
#    sa_m2               solar array area in square meters
#    eff                 solar panel efficiency [0,1]
#    voc                 open-circuit voltage of the solar panel in volts
#    c_f                 capacitance of the capacitor in farads
#    r_esr               equivalent series resistance of the capacitor in ohms
#    q0_c                initial charge of the capacitor in coulombs
#    p_on_w              power consumption in watts
#    v_thresh            voltage threshold in volts
#    dt_s                time step for the simulation in seconds
#    dur_s               duration of the simulation in seconds
#
# Output:
#    log.csv file containing time and voltage data points
#
# Revision history:
#    12/06/2024          Script created
#
###############################################################################

#Import relevant modules
import sys
import csv
import math

#Constants
irr_w_m2 = 1366.1 #Solar irradiance [W/m^2]

#User-defined functions
#Calculates solar current
def solar_current(irr_w_m2, sa_m2, eff, voc):
    return irr_w_m2 * sa_m2 * eff / voc

#Calculates 
def node_discrim(q_c, c_f, i_a, esr_ohm, power_w):
    return (q_c / c_f + i_a * esr_ohm)**2 - 4 * power_w * esr_ohm

def node_voltage(q_c, c_f, i_a, esr_ohm, disc):
    return (q_c / c_f + i_a * esr_ohm + math.sqrt(disc)) / 2

#Pre-initialize input parameters
sa_m2 = float('nan') #solar array area in square meters
eff = float('nan') #solar panel efficiency [0,1]
voc = float('nan') #open-circuit voltage of the solar panel in volts
c_f = float('nan') #capacitance of the capacitor in farads
r_esr = float('nan') #equivalent series resistance of the capacitor in ohms
q0_c = float('nan') #initial charge of the capacitor in coulombs
p_on_w = float('nan') #power consumption in watts
v_thresh = float('nan') #voltage threshold in volts
dt_s = float('nan') #time step for the simulation in seconds
dur_s = float('nan') #duration of the simulation in seconds

#Arguments are strings by default
if len(sys.argv) == 11:
   sa_m2 = float(sys.argv[1])
   eff = float(sys.argv[2])
   voc = float(sys.argv[3])
   c_f = float(sys.argv[4])
   r_esr = float(sys.argv[5])
   q0_c = float(sys.argv[6])
   p_on_w = float(sys.argv[7])
   v_thresh = float(sys.argv[8])
   dt_s = float(sys.argv[9])
   dur_s = float(sys.argv[10])
else:
   print(('Usage: sim_energy_system_cap.py sa_m2 eff voc c_f r_esr q0_c ' \
          'p_on_w v_thresh dt_s dur_s'))
   sys.exit()

#Main body of script

#Initialize values
isc_a = solar_current(irr_w_m2, sa_m2, eff, voc)
i1_a = isc_a
qt_c = q0_c
p_mode_w = p_on_w
t_s = 0

#Calculate node discriminant and voltage
node_discr = node_discrim(qt_c, c_f, i1_a, r_esr, p_mode_w)
node_v = node_voltage(qt_c, c_f, i1_a, r_esr, node_discr)
log = [[t_s,node_v]]

if voc <= node_v and i1_a != 0.0:
    i1_a = 0.0

if node_v < v_thresh:
    p_mode_w = 0.0

#Iterate
while log[-1][0] < dur_s:
    i3_a = p_mode_w / node_v 
    qt_c += (i1_a - i3_a) * dt_s
    
    if qt_c < 0.0:
        qt_c = 0.0
    
    if p_mode_w == 0.0 and node_v >= voc:
        p_mode_w = p_on_w
    
    i1_a = isc_a if 0 <= node_v < voc else 0.0
    node_discr = node_discrim(qt_c, c_f, i1_a, r_esr, p_mode_w)
    
    if(node_discr<0.0):
        p_mode_w = 0.0
        node_discr = node_discrim(qt_c, c_f, i1_a, r_esr, p_mode_w)
        
    node_v = node_voltage(qt_c, c_f, i1_a, r_esr, node_discr)
    
    if voc <= node_v and i1_a != 0.0:
        i1_a = 0.0
        
    if node_v < v_thresh:
        p_mode_w = 0.0
        
    log.append([t_s,node_v])
    t_s += dt_s

with open('./log.csv',mode='w',newline='') as outfile:
  csvwriter = csv.writer(outfile)
  csvwriter.writerow(\
   ['t_s','volts']\
  )
  for e in log:
    csvwriter.writerow(e)