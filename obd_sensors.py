#!/usr/bin/env python
# vim: shiftwidth=4:tabstop=4:expandtab
###########################################################################
# obd_sensors.py
#
# Copyright 2004 Donour Sizemore (donour@uchicago.edu)
# Copyright 2009 Secons Ltd. (www.obdtester.com)
# Copyright 2019 Brian LePage (github.com/beardedone55/)
#
# This file is part of pyOBD.
#
# pyOBD is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# pyOBD is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyOBD; if not, see https://www.gnu.org/licenses/.
############################################################################

def hex_to_int(str):
    i = eval("0x" + str, {}, {})
    return i

def maf(code):
    code = hex_to_int(code[:4])
    return '%4.3f' % (code * 0.00132276)

def throttle_pos(code):
    code = hex_to_int(code[:2])
    return '%3.1f' % (code * 100.0 / 255.0)

def intake_m_pres(code): # in kPa
    code = hex_to_int(code[:2])
    return '%4.3f' % (code * 0.14504)
    
def fuel_pres(code): # in 3kPa
    code = hex_to_int(code[:2])
    return '%4.3f' % (code * 0.43511)

def fuel_pres_10(code): # in 10kPa
    code = hex_to_int(code[:4])
    return '%4.3f' % (code * 1.4504)

def rel_fuel_pres(code): #in 0.079 kPa
    code = hex_to_int(code[:4])
    return '%4.3f' % (code * 0.14504 * 0.079)

def rpm(code):
    code = hex_to_int(code[:4])
    return str(code / 4)

def speed(code):
    code = hex_to_int(code[:2])
    return '%3.1f' % (code / 1.609)

def percent_scale(code):
    code = hex_to_int(code[:2])
    return '%3.1f' % (code * 100.0 / 255.0)

def abs_load_percent(code):
    code = hex_to_int(code[:4])
    return '%3.1f' % (code * 100.0 / 255.0)

def timing_advance(code):
    code = hex_to_int(code[:4])
    return '%3.1f' % (code - 128) / 2.0

def injection_timing(code):
    code = hex_to_int(code[:4])
    code = (code - 38665) / 128.0
    return '%3.3f' % (code)

def sec_to_min(code):
    code = hex_to_int(code[:4])
    return str(code / 60)

def temp(code):
    code = hex_to_int(code[:2])
    return str(code - 40) 

def cpass(code):
    #fixme
    return code

def fuel_trim_percent(code):
    code = hex_to_int(code[:2])
    return '%3.1f' % ((code - 128.0) * 100.0 / 128.0)

def dtc_decrypt(code):
    #first byte is byte after PID and without spaces
    num = hex_to_int(code[:2]) #A byte
    res = []

    if num & 0x80: # is mil light on
        mil = 1
    else:
        mil = 0
        
    # bit 0-6 are the number of dtc's. 
    num = num & 0x7f
    
    res.append(num)
    res.append(mil)
    
    numB = hex_to_int(code[2:4]) #B byte
      
    for i in range(0,3):
        res.append(((numB>>i)&0x01)+((numB>>(3+i))&0x02))
    
    numC = hex_to_int(code[4:6]) #C byte
    numD = hex_to_int(code[6:8]) #D byte
       
    for i in range(0,7):
        res.append(((numC>>i)&0x01)+(((numD>>i)&0x01)<<1))
    
    res.append(((numD>>7)&0x01)) #EGR SystemC7  bit of different 
    
    return res

def ol_cl(code):
    def ol_cl_convert(byte):
        olcl_lookup = {
            1 : 'OL',
            2 : 'CL',
            4 : 'OL-Drive',
            8 : 'OL-Fault',
            16 : 'CL-Fault'
        }
        byte = hex_to_int(byte)
        if byte in olcl_lookup:
            return olcl_lookup[byte]
        else:
            return 'UNKNOWN'

    codeA = ol_cl_convert(code[0:2])
    codeB = ol_cl_convert(code[2:4])
    return 'Fuel System 1: %s; Fuel System 2: %s' % (codeA, codeB)
		  
def sensor_voltage(code):
    code = hex_to_int (code[0:2])
    return '%1.3f' % (code * 0.005)

def cm_voltage(code):
    code = hex_to_int (code[0:4])
    return '%2.3f' % (code * 0.001)

def eq_ratio(code):
    code = hex_to_int(code[0:4]) #Bytes A/B contain Equivalence Ratio
    return '%1.4f' % (code * 0.0000305)

def evap_pres(code):
    code = hex_to_int(code[0:4])
    code = code if (code < 32768) else (code - 65535)
    return '%4.2f' % (code / 4.0)

def evap_pres2(code):
    code = hex_to_int(code[0:4])
    code = code if (code < 32768) else (code - 65535)
    return str(code)

def abs_vapor_pres(code):
    code = hex_to_int(code[0:4])
    return '%4.5f' % (code * 0.005 * 0.14504)

def hex_to_bitstring(str):
    bitstring = ""
    for i in str:
        # silly type safety, we don't want to eval random stuff
        if type(i) == type(''): 
            v = eval("0x%s" % i)
            if v & 8 :
                bitstring += '1'
            else:
                bitstring += '0'
            if v & 4:
                bitstring += '1'
            else:
                bitstring += '0'
            if v & 2:
                bitstring += '1'
            else:
                bitstring += '0'
            if v & 1:
                bitstring += '1'
            else:
                bitstring += '0'                
    return bitstring

def km_to_mi(code):
    return '%6.1f' % (hex_to_int(code[:4]) * 0.6)

def fuel_rate(code):
    code = hex_to_int(code[:4])
    code = code * 0.05 *0.264172
    return '%4.2f' % (code)

def req_torque(code):
    code = hex_to_int(code[:2])
    return str(code - 125)

def ref_torque(code):
    code = hex_to_int(code[:4])
    return '%5.1f' % (code * 0.737562)

class Sensor:
    def __init__(self,sensorName, sensorcommand, sensorValueFunction, u):
        self.name = sensorName
        self.cmd  = sensorcommand
        self.value= sensorValueFunction
        self.unit = u

SUPPORTED_PIDS = (0, 0x20, 0x40, 0x60, 0x80)

SENSORS = [
    Sensor("          Supported PIDs", "0100", hex_to_bitstring  ,""       ),    
    Sensor("Status Since DTC Cleared", "0101", dtc_decrypt       ,""       ),    
    Sensor("DTC Causing Freeze Frame", "0102", cpass             ,""       ),    
    Sensor("      Fuel System Status", "0103", ol_cl             ,""       ),
    Sensor("   Calculated Load Value", "0104", percent_scale     ,""       ),    
    Sensor("     Coolant Temperature", "0105", temp              ,"C"      ),
    Sensor("Short Term Fuel Trim - Bank 1", "0106", fuel_trim_percent ,"%" ),
    Sensor("Long Term Fuel Trim - Bank 1", "0107", fuel_trim_percent ,"%"  ),
    Sensor("Short Term Fuel Trim - Bank 2", "0108", fuel_trim_percent ,"%" ),
    Sensor("Long Term Fuel Trim - Bank 2", "0109", fuel_trim_percent ,"%"  ),
    Sensor("      Fuel Rail Pressure", "010A", fuel_pres         ,"psi"    ),
    Sensor("Intake Manifold Pressure", "010B", intake_m_pres     ,"psi"    ),
    Sensor("              Engine RPM", "010C", rpm               ,"RPM"    ),
    Sensor("           Vehicle Speed", "010D", speed             ,"MPH"    ),
    Sensor("          Timing Advance", "010E", timing_advance    ,"degrees"),
    Sensor("         Intake Air Temp", "010F", temp              ,"C"      ),
    Sensor("     Air Flow Rate (MAF)", "0110", maf               ,"lb/min" ),
    Sensor("       Throttle Position", "0111", throttle_pos      ,"%"      ),
    Sensor("    Secondary Air Status", "0112", cpass             ,""       ),
    Sensor("  Location of O2 sensors", "0113", cpass             ,""       ),
    Sensor("        O2 Sensor: 1 - 1", "0114", sensor_voltage ,"V"      ),
    Sensor("        O2 Sensor: 1 - 2", "0115", sensor_voltage ,"V"      ),
    Sensor("        O2 Sensor: 1 - 3", "0116", sensor_voltage ,"V"      ),
    Sensor("        O2 Sensor: 1 - 4", "0117", sensor_voltage ,"V"      ),
    Sensor("        O2 Sensor: 2 - 1", "0118", sensor_voltage ,"V"      ),
    Sensor("        O2 Sensor: 2 - 2", "0119", sensor_voltage ,"V"      ),
    Sensor("        O2 Sensor: 2 - 3", "011A", sensor_voltage ,"V"      ),
    Sensor("        O2 Sensor: 2 - 4", "011B", sensor_voltage ,"V"      ),
    Sensor("         OBD Designation", "011C", cpass             ,""       ),
    Sensor("  Location of O2 sensors", "011D", cpass             ,""       ),
    Sensor("        Aux input status", "011E", cpass             ,""       ),
    Sensor(" Time Since Engine Start", "011F", sec_to_min        ,"min"    ),
    Sensor("          Supported PIDs", "0120", hex_to_bitstring  ,""       ),    
    Sensor("Distance Traveled w/ MIL", "0121", km_to_mi          ,"mi"    ),
    Sensor("      Fuel Rail Pressure", "0122", rel_fuel_pres     ,"psi"    ),
    Sensor("      Fuel Rail Pressure", "0123", fuel_pres_10      ,"psi"    ),
    Sensor("  Air/Fuel Sensor: 1 - 1", "0124", eq_ratio ,""      ),
    Sensor("  Air/Fuel Sensor: 1 - 2", "0125", eq_ratio ,""      ),
    Sensor("  Air/Fuel Sensor: 1 - 3", "0126", eq_ratio ,""      ),
    Sensor("  Air/Fuel Sensor: 1 - 4", "0127", eq_ratio ,""      ),
    Sensor("  Air/Fuel Sensor: 2 - 1", "0128", eq_ratio ,""      ),
    Sensor("  Air/Fuel Sensor: 2 - 2", "0129", eq_ratio ,""      ),
    Sensor("  Air/Fuel Sensor: 2 - 3", "012A", eq_ratio ,""      ),
    Sensor("  Air/Fuel Sensor: 2 - 4", "012B", eq_ratio ,""      ),
    Sensor("         Commanded EGR %", "012C", percent_scale ,"%"      ),
    Sensor("             EGR Error %", "012D", fuel_trim_percent,"%"      ),
    Sensor("Commanded Evaporative Purge", "012E", percent_scale ,"%"      ),
    Sensor("              Fuel Level", "012F", percent_scale ,"%"      ),
    Sensor("Warm-ups Since Codes Clear", "0130", hex_to_int, ""      ),
    Sensor("Distance Since Codes Clear", "0131", km_to_mi, "mi"      ),
    Sensor("     Evap Vapor Pressure", "0132", evap_pres, "Pa"      ),
    Sensor("     Barometric Pressure", "0133", intake_m_pres, "psi"      ),
    Sensor("  Air/Fuel Sensor: 1 - 1", "0134", eq_ratio ,""      ),
    Sensor("  Air/Fuel Sensor: 1 - 2", "0135", eq_ratio ,""      ),
    Sensor("  Air/Fuel Sensor: 1 - 3", "0136", eq_ratio ,""      ),
    Sensor("  Air/Fuel Sensor: 1 - 4", "0137", eq_ratio ,""      ),
    Sensor("  Air/Fuel Sensor: 2 - 1", "0138", eq_ratio ,""      ),
    Sensor("  Air/Fuel Sensor: 2 - 2", "0139", eq_ratio ,""      ),
    Sensor("  Air/Fuel Sensor: 2 - 3", "013A", eq_ratio ,""      ),
    Sensor("  Air/Fuel Sensor: 2 - 4", "013B", eq_ratio ,""      ),
    Sensor("Catalyst Temp - Bank 1, Sensor 1", "013C", temp ,"C"      ),
    Sensor("Catalyst Temp - Bank 2, Sensor 1", "013D", temp ,"C"      ),
    Sensor("Catalyst Temp - Bank 1, Sensor 2", "013E", temp ,"C"      ),
    Sensor("Catalyst Temp - Bank 2, Sensor 2", "013F", temp ,"C"      ),
    Sensor("          Supported PIDs", "0140", hex_to_bitstring  ,""       ),    
    Sensor("Monitor Status - Current", "0141", cpass  ,""       ),    
    Sensor("  Control Module Voltage", "0142", cm_voltage  ,"%"       ),    
    Sensor("         Absolute Load %", "0143", abs_load_percent  ,"%"       ),    
    Sensor("Commanded Equivalence Ratio", "0144", eq_ratio  ,""       ),    
    Sensor("Relative Throttle Position", "0145", percent_scale  ,"%"       ),    
    Sensor("Ambient Air Temperature", "0146", temp ,"C"      ),
    Sensor("Absolute Throttle Position B", "0147", percent_scale  ,"%"       ),    
    Sensor("Absolute Throttle Position C", "0148", percent_scale  ,"%"       ),    
    Sensor("Accelerator Pedal Position", "0149", percent_scale  ,"%"       ),    
    Sensor("Accelerator Pedal Position E", "014A", percent_scale  ,"%"       ),    
    Sensor("Accelerator Pedal Position F", "014B", percent_scale  ,"%"       ),    
    Sensor("Commanded Throttle Actuator", "014C", percent_scale  ,"%"       ),    
    Sensor("    Time Run with MIL on", "014D", sec_to_min  ,"min"       ),    
    Sensor("  Engine Run with MIL on", "014E", sec_to_min        ,"min"    ),
    Sensor("   Max Equivalence Ratio", "014F", hex_to_int      ,""    ),
    Sensor("       Max Air Flow Rate", "0150", hex_to_int      ,""    ),
    Sensor("               Fuel Type", "0151", cpass      ,""    ),
    Sensor("          Alcohol Fuel %", "0152", percent_scale      ,"%"    ),
    Sensor(" Absolute Vapor Pressure", "0153", abs_vapor_pres      ,"psi"    ),
    Sensor("     Evap Vapor Pressure", "0154", evap_pres2      ,"Pa"    ),
    Sensor("Secondary O2 STFT - Bank 1", "0155", fuel_trim_percent      ,"%"    ),
    Sensor("Secondary O2 LTFT - Bank 1", "0156", fuel_trim_percent      ,"%"    ),
    Sensor("Secondary O2 STFT - Bank 2", "0157", fuel_trim_percent      ,"%"    ),
    Sensor("Secondary O2 LTFT - Bank 2", "0158", fuel_trim_percent      ,"%"    ),
    Sensor("    Abs Fuel Rail Pressure", "0159", fuel_pres_10      ,"psi"    ),
    Sensor("Relative Acc Pedal Position", "015A", percent_scale  ,"%"       ),    
    Sensor("Hybrid Batt Remaining Life", "015B", percent_scale  ,"%"       ),    
    Sensor("  Engine Oil Temperature", "015C", temp  ,"C"       ),    
    Sensor("   Fuel Injection Timing", "015D", injection_timing  ,"degrees" ),
    Sensor("        Engine Fuel Rate", "015E", fuel_rate  ,"gal/h"       ),
    Sensor("   Emmission Requirement", "015F", cpass  ,""       ),
    Sensor("          Supported PIDs", "0160", hex_to_bitstring  ,""       ),    
    Sensor("        Requested Torque", "0161", req_torque  ,"%"       ),    
    Sensor("           Actual Torque", "0162", req_torque  ,"%"       ),    
    Sensor("        Reference Torque", "0163", ref_torque  ,"lbf*ft"  ),    
    Sensor("    Engine % Torque Data", "0164", cpass  ,""  ),    
    Sensor("Auxiliary Inputs/Outputs", "0165", cpass  ,""  ),    
    Sensor("         MAF Sensor Data", "0166", cpass  ,""  ),    
    Sensor("         ECT Sensor Data", "0167", cpass  ,""  ),    
    Sensor("         IAT Sensor Data", "0168", cpass  ,""  ),    
    Sensor("       Cmd EGR/EGR Error", "0169", cpass  ,""  ),    
    Sensor("       Diesel Intake Air", "016A", cpass  ,""  ),    
    Sensor("                EGR Temp", "016B", cpass  ,""  ),    
    Sensor("   Cmd Throtlle Actuator", "016C", cpass  ,""  ),    
    Sensor("   Fuel Pressure Control", "016D", cpass  ,""  ),    
    Sensor("Injection Pressure Control", "016E", cpass  ,""  ),    
    Sensor("Turbo Compressor Pressure", "016F", cpass  ,""  ),    
    Sensor("  Boost Pressure Control", "0170", cpass  ,""  ),    
    Sensor("           Turbo Control", "0171", cpass  ,""  ),    
    Sensor("       Wastegate Control", "0172", cpass  ,""  ),    
    Sensor("        Exhaust Pressure", "0173", cpass  ,""  ),    
    Sensor("       Turbo Charger RPM", "0174", cpass  ,""  ),    
    Sensor("    Turbo Charger Temp A", "0175", cpass  ,""  ),    
    Sensor("    Turbo Charger Temp B", "0176", cpass  ,""  ),    
    Sensor("  Charge Air Cooler Temp", "0177", cpass  ,""  ),    
    Sensor("   Exhaust Temp - Bank 1", "0178", cpass  ,""  ),    
    Sensor("   Exhaust Temp - Bank 2", "0179", cpass  ,""  ),    
    Sensor("  Diesel Filter - Bank 1", "017A", cpass  ,""  ),    
    Sensor("  Diesel Filter - Bank 2", "017B", cpass  ,""  ),    
    Sensor("      Diesel Filter Temp", "017C", cpass  ,""  ),    
    Sensor("         NOx NTE Control", "017D", cpass  ,""  ),    
    Sensor("          PM NTE Control", "017E", cpass  ,""  ),    
    Sensor("         Engine Run Time", "017F", cpass  ,""  ),    
    Sensor("          Supported PIDs", "0180", hex_to_bitstring  ,""       ),    
    Sensor("    Engine Run Time AECD", "0181", cpass  ,""  ),    
    Sensor("    Engine Run Time AECD", "0182", cpass  ,""  ),    
    Sensor("              NOx Sensor", "0183", cpass  ,""  ),    
    ]
     
    
#___________________________________________________________

def test():
    for i in SENSORS:
        print (i.name, i.value("F"))

if __name__ == "__main__":
    test()
