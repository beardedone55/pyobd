#!/usr/bin/env python
# vim: shiftwidth=4:tabstop=4:expandtab
###########################################################################
# odb_io.py
# 
# Copyright 2004 Donour Sizemore (donour@uchicago.edu)
# Copyright 2009 Secons Ltd. (www.obdtester.com)
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
# along with pyOBD; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
###########################################################################

import serial
import string
import time
from math import ceil
import wx #due to debugEvent messaging

import obd_sensors

from obd_sensors import hex_to_int

GET_DTC_COMMAND   = "03"
CLEAR_DTC_COMMAND = "04"
GET_PENDING_DTC_COMMAND = "07"
GET_DTC_RESPONSE = "43"
GET_PENDING_DTC_RESPONSE = "47"

from debugEvent import *

#__________________________________________________________________________
def decrypt_dtc_code(code):
    """Returns the 5-digit DTC code from hex encoding"""
    dtc = []
    current = code
    for i in range(0,3):
        if len(current)<4:
            raise "Tried to decode bad DTC: %s" % code

        tc = obd_sensors.hex_to_int(current[0]) #typecode
        tc = tc >> 2
        if   tc == 0:
            type = "P"
        elif tc == 1:
            type = "C"
        elif tc == 2:
            type = "B"
        elif tc == 3:
            type = "U"
        else:
            raise tc

        dig1 = str(obd_sensors.hex_to_int(current[0]) & 3)
        dig2 = str(obd_sensors.hex_to_int(current[1]))
        dig3 = str(obd_sensors.hex_to_int(current[2]))
        dig4 = str(obd_sensors.hex_to_int(current[3]))
        dtc.append(type+dig1+dig2+dig3+dig4)
        current = current[4:]
    return dtc
#__________________________________________________________________________

class OBDPort:
    """ OBDPort abstracts all communication with OBD-II device."""
    def __init__(self,portnum,baudrate,_notify_window,SERTIMEOUT,RECONNATTEMPTS):
        """Initializes port by resetting device and gettings supported PIDs. """
        # These should really be set by the user.
        #baud     = 9600
        baud = int(baudrate)		 
        databits = 8
        par      = serial.PARITY_NONE  # parity
        sb       = 1                   # stop bits
        to       = SERTIMEOUT
        self.ELMver = "Unknown"
        self.State = 1 #state SERIAL is 1 connected, 0 disconnected (connection failed)
         
        self._notify_window=_notify_window
        self._notify_window.DebugEvent.emit(1,'Opening interface (serial port)')
        self.port = None
        self.protocol = None
        self.prot_is_CAN = False
        self.ecu_addresses = []

        try:
            self.port = serial.Serial(portnum,baud, parity = par, stopbits = sb, \
                bytesize = databits,timeout = to)
             
        except serial.SerialException:
            self.State = 0
            return None
             
        self._notify_window.DebugEvent.emit(1,"Interface successfully " + self.port.portstr + " opened")
        self._notify_window.DebugEvent.emit(1,"Connecting to ECU...")
         
        def ConnectionError(count, msg = ''):
            self._notify_window.DebugEvent.emit(2,"Connection attempt failed: " + msg)
            count += 1
            if count <= RECONNATTEMPTS:
                time.sleep(5)
                self._notify_window.DebugEvent.emit(2,"Reconnection attempt:" + str(count))
            return count

        count=0
        while count <= RECONNATTEMPTS: #until error is returned try to connect
            try:
                self.send_command("atz")   # initialize
            except serial.SerialException:
                self.State = 0
                return None

            res = self.get_result()
            if res == None:
                count = ConnectionError(count)
                continue

            self.ELMver = res[-1]  #Last Non-Blank Line Returned is ELM Version
            self._notify_window.DebugEvent.emit(2,"atz response: " + self.ELMver)
            self.send_command("ate0")  # echo off
            res = self.get_result() # ATE0 command should echo command and return OK
            if res == None:
                count = ConnectionError(count, res[0])
                continue

            self._notify_window.DebugEvent.emit(2,"ate0 response: " + res[-1])

            self.send_command('atdp') #Send Display Protocol Command
            res = self.get_result()
            if res == None:
                count = ConnectionError(count, res[0])
                continue

            self.protocol = res[0]
            self.prot_is_CAN = self.protocol.upper().find('CAN') != -1

            self.send_command('ath1') #Turn on headers
            self.get_result()


            #Ping all ECUs in Vehicle
            self.send_command("0100")
            res = self.get_result()
            if res == None:
                count = ConnectionError(count)
                continue

            #For CAN expecting something like this for each ECU:
            #   7E8 06 41 00
            #    ^  ^   ^  ^
            #    |  |   |  --- PID
            #    |  |    ------Response Code Service 1
            #    |  -----------PCI Byte
            #    --------------ECU Response Address
            #    
            #For others, expecting something like this:
            #   41 6B E0 41 00
            #         ^  ^  ^
            #         |  |  --- PID
            #         |  -------Response Code Service 1
            #         ----------ECU Address

            for ready in res:
                self._notify_window.DebugEvent.emit(2,"0100 response1: " + ready)
                ready = ready.split(' ')
                if not self.prot_is_CAN:
                    ecu = ready[2]
                    ready = ready[3:]   #Remove header bytes
                else:
                    ecu = ready[0]
                    ready = ready[2:]   #Remove CAN header and PCI byte

                if ready[0:2] == ['41', '00']:    #Expected Response code from any ECU
                    self.ecu_addresses.append(ecu)

            self.ecu_addresses = sorted(self.ecu_addresses)

            if len(self.ecu_addresses) > 0:
                return None

            count = ConnectionError(count, res[-1])

        self.close()
        self.State = 0
        return None
              
    def getEcuNum(self, ecuAddress):
        if ecuAddress in self.ecu_addresses:
            return self.ecu_addresses.index(ecuAddress)
        else:
            return 0

    def close(self):
        """ Resets device and closes all associated filehandles"""
         
        if (self.port!= None) and self.State==1:
            self.send_command("atz")
            self.port.close()
         
        self.port = None
        #self.ELMver = "Unknown"

    def send_command(self, cmd):
        """Internal use only: not a public interface"""
        if self.port:
            try:
                self.port.flushOutput()
                self.port.flushInput()
                cmd += '\r\n'
                self.port.write(cmd.encode('ascii', 'ignore'))
                self.port.flush()
                self._notify_window.DebugEvent.emit(3,"Send command: " + cmd)
            except:
                self._notify_window.DebugEvent.emit(3,"Error Sending command: " + cmd)
             

    def interpret_result(self,data,ecu):
        """Internal use only: not a public interface"""
        # Code will be the string returned from the device.
        # It should look something like this:
        # '41 11 0 0\r\r'
         
        # get the first thing returned, echo should be off
        if data is None:
            return "NODATA"

        retVal = {}

        # 9 seems to be the length of the shortest valid response
        for code in data:
            if len(code) < 7:
                raise "BogusCode"
         
            #cables can behave differently 
            if code[:6] == "NODATA": # there is no such sensor
                return "NODATA"

            code = code.split(' ')

            if not self.prot_is_CAN:
                code = code[2:]

            returned_ecu = code[0]
            if self.prot_is_CAN:
                code = code[2:] #Remove ECU and PCI Byte
            else:
                code = code[1:] #Remove ECU

            #Squash data together
            code = ''.join(code)
            # first 4 characters are code from ELM
            code = code[4:]
            retVal[returned_ecu] = code

        if ecu is None:
            if len(retVal) == 0:
                return 'NODATA'
            else:
                return retVal

        if ecu in retVal:
            return retVal[ecu]
        else:
            return "NODATA"
     
    #get_result reads input from serial port and 
    #returns array of lines returned with 
    def get_result(self):
        """Internal use only: not a public interface"""
        if self.port:
            buffer = ""
            result = []

            while True: 
                try:
                    c = self.port.read(1).decode('utf8', 'ignore')
                except Exception as e:
                    self._notify_window.DebugEvent.emit(3,"Get Result Failed: " + str(e))
                    break 
                    
                if len(c) == 0 or c == '>': #Loop until SOI or buffer is empty
                    break
                if c != '\r' and c != '\n': #Ignore line feeds
                    buffer = buffer + c
                elif (c == '\r' or c == '\n') and len(buffer) > 0: #ignore blank lines
                    result.append(buffer) #add line to return result
                    buffer = ''
                     
            for line in result:
                self._notify_window.DebugEvent.emit(3,"Get result: " + line)

            if len(result) == 0:
                result = None

            return result
        else:
            self._notify_window.DebugEvent.emit(3,"NO self.port!" + buffer)
        return None

    def get_obd_data_bytes(self):
        """Internal use only: not a public interface"""
        retVal = {}
        byteCount = {}
        data = self.get_result()
        if data is None:
            return None

        for line in data:
            line = line.split(' ') #Turn data into list of bytes 
            if not self.prot_is_CAN:
                line = line[2:]
            ecu = line[0]
            if ecu not in retVal:
                retVal[ecu] = []
            if self.prot_is_CAN:
                if line[1][0] == '0':  #PCI Byte indicates single line response
                    byteCount[ecu] = int(line[1][1]) #Second half of PCI byte is data length
                    line = line[2:]  #Remove ecu address and byte count
                    retVal[ecu] += line[0:byteCount[ecu]] #Get the data

                elif line[1][0] == '1':   #PCI Byte indicates 1st frame of multiframe response
                    byteCount[ecu] = hex_to_int(line[1][1] + line[2]) #PCI Byte extended 1 byte for byte count
                    retVal[ecu] += ['00'] * (byteCount[ecu]-len(retVal[ecu])) #Fill out data with zeroes                      
                    retVal[ecu] = retVal[ecu][0:byteCount[ecu]]               #Truncate list to byte count
                    line = line[3:]                                           #Remove ECU Address and Byte Count
                    i = 0
                    for byte in line:
                        retVal[ecu][i] = byte
                        i += 1
                elif line[1][0] == '2':            #PCI Byte indicates Next frame of multiframe response
                    i = hex_to_int(line[1][1])  #Indicates frame # of multiframe response
                    i = i*7 - 1
                    line = line[2:]
                    if ecu not in byteCount:
                        retVal[ecu] += ['00'] * (i+7 - len(retVal[ecu])) #Next Frame came before 1st frame.
                            #Fill through this frame with zeroes. 
                    for data in line:
                        if i < len(retVal[ecu]):
                            retVal[ecu][i] = data
                        else:
                            break
                        i += 1
                          
            else:
                retVal[ecu] += line[1:]

        return retVal

    # get sensor value from command
    def get_sensor_value(self,sensor,ecu):
        """Internal use only: not a public interface"""
        data = self.get_result()
         
        if data != None:
            data = self.interpret_result(data,ecu)
            if data != "NODATA":
                if ecu is None:
                    for key in data:
                        data[key] = sensor.value(data[key])
                else:
                    data = sensor.value(data)
                      
        else:
            return "NORESPONSE"
        return data

    # return string of sensor name and value from sensor index
    def sensor(self , sensor_index, ecu = None, mode = None, sensors = obd_sensors.SENSORS):
        """Returns 3-tuple of given sensors. 3-tuple consists of
         (Sensor Name (string), Sensor Value (string), Sensor Unit (string) ) """
        sensor = sensors[sensor_index]
        cmd = sensor.cmd
        if mode is not None:
            cmd = mode + cmd[2:]

        self.send_command(cmd)
        r = self.get_sensor_value(sensor, ecu)
        return (sensor.name,r, sensor.unit)

    def get_sensors(self, sensor_index_list, ecu = None, mode = '01', sensors = obd_sensors.SENSORS):
        retVal = {}
        sil = list(sensor_index_list)
        if self.prot_is_CAN and ecu is not None:
            while len(sil) > 0:
                cmd = mode
                cmd_dict = {}
                for i in sil[:6]:  #Read up to 6 at a time!
                    pid = sensors[i].cmd[2:]
                    cmd_dict[pid] = i
                    cmd += pid
                self.send_command(cmd)
                res = self.get_obd_data_bytes()
                if res is not None and ecu in res:
                    res = res[ecu]
                    if res[0] == '4' + mode[1]:
                        res = res[1:]
                        while len(res) > 0:
                            pid = res[0] #PID
                            data = res[1:5] #A to D
                            data = ''.join(data)
                            i = cmd_dict[pid]
                            sensor = sensors[i]
                            data = sensor.value(data)
                            retVal[i] = (sensor.name, data, sensor.unit)
                            res = res[5:] #goto next result

                sil = sil[6:] #Remove last 6

        else:
            for i in sensor_index_list:
                retVal[i] = sensor(self, i, ecu, mode, sensors)

        return retVal 

    def get_supported(self, ecu, mode = '01', sensors = obd_sensors.SENSORS):
        data = self.get_sensors(obd_sensors.SUPPORTED_PIDS, ecu, mode, sensors)
        retVal = ''
        for i in obd_sensors.SUPPORTED_PIDS:
            if i in data:
                retVal += data[i][1]
            else:
                retVal += '0' * 32 #Assume not supported (32 zeroes) 

        return retVal

    def sensor_names(self):
        """Internal use only: not a public interface"""
        names = []
        for s in obd_sensors.SENSORS:
            names.append(s.name)
        return names
         
    def get_tests_MIL(self):
        statusText=["Unsupported","Supported - Completed","Unsupported","Supported - Incompleted"]
         
        statusRes = self.sensor(1)[1] #GET values
        statusTrans = [] #translate values to text
         
        statusTrans.append(str(statusRes[0])) #DTCs
         
        if statusRes[1]==0: #MIL
            statusTrans.append("Off")
        else:
            statusTrans.append("On")
            
        for i in range(2,len(statusRes)): #Tests
            statusTrans.append(statusText[statusRes[i]]) 
         
        return statusTrans
          
    def get_dtc(self):
        """Returns a list of all pending DTC codes. Each element consists of
        a 2-tuple: (DTC code (string), Code description (string) )"""
        #Separate Data received into codes for each ECU.
        def parse_get_dtc_data(res, DTCCodes, DTCType, dtcNumber=None):
            dtcLetters = ["P", "C", "B", "U"]
            for ecu in res:
                i=0
                dataList = res[ecu]
                if ecu not in DTCCodes:
                    DTCCodes[ecu] = []

                while i < len(dataList):
                    #check Mode Response byte (Should be GET_DTC_RESPONSE(0x43))
                    if (self.prot_is_CAN and i == 0) or (not self.prot_is_CAN and (i % 7) == 0):
                        if dataList[i] != GET_DTC_RESPONSE and dataList[i] != GET_PENDING_DTC_RESPONSE:
                            self._notify_window.DebugEvent.emit(1,'Unexpected Response to GET_DTC (%s)' % (dataList[i]))
                            break
                        i += 1
                    
                    #For CAN, 1st byte is Number of DTCs        
                    if self.prot_is_CAN and i == 1:
                        NumCodes = hex_to_int(dataList[i])
                        i += 1
                        if dtcNumber is not None and (NumCodes != dtcNumber[ecu]):
                            self._notify_window.DebugEvent.emit(1,'Expected Codes (%d) != Received Codes (%d)' % (dtcNumber[ecu], NumCodes))

                    if i >= len(dataList):
                        break

                    val1 = hex_to_int(dataList[i])
                    val2 = hex_to_int(dataList[i+1]) #get DTC codes from response (3 DTC each 2 bytes)
                    val  = (val1<<8)+val2 #DTC val as int

                    i += 2
                    
                    if val==0: #skip fill of last packet
                        continue
                       
                    DTCStr=dtcLetters[(val&0xC000)>>14]+str((val&0x3000)>>12)+str(val&0x0fff) 
                    DTCCodes[ecu].append([DTCType, DTCStr])
         
            return DTCCodes 

        DTCCodes = {}
        r = self.sensor(1)[1] #data
        dtcNumber = {}
        mil = {}
        if r != 'NODATA' and r != 'NORESPONSE':
            #Each ECU may return different number of DTCs
            for ecu in r: 
                dtcNumber[ecu] = r[ecu][0]
                mil[ecu] = r[ecu][1]
                self._notify_window.DebugEvent.emit(1,'Number of stored DTC: %d' % dtcNumber[ecu])

            # Get Active DTCs
            self.send_command(GET_DTC_COMMAND)
            res = self.get_obd_data_bytes()

            if res is None:
                return None #Connection Lost

            DTCCodes = parse_get_dtc_data(res, DTCCodes, 'Active', dtcNumber)
        else:
            return None #Connection Lost

        #read mode 7
        self.send_command(GET_PENDING_DTC_COMMAND)
        res = self.get_obd_data_bytes()
          
        if res != None: #Pending Trouble Codes Returned
            DTCCodes = parse_get_dtc_data(res, DTCCodes, 'Passive')
            
        return DTCCodes
          
    def clear_dtc(self):
        """Clears all DTCs and freeze frame data"""
        self.send_command(CLEAR_DTC_COMMAND)     
        r = self.get_result()
        if r != None:
            r = r[0]
        return r
     
    def log(self, sensor_index, filename): 
        file = open(filename, "w")
        start_time = time.time() 
        if file:
            data = self.sensor(sensor_index)
            file.write("%s     \t%s(%s)\n" % \
                         ("Time", string.strip(data[0]), data[2])) 
            while 1:
                now = time.time()
                data = self.sensor(sensor_index)
                line = "%.6f,\t%s\n" % (now - start_time, data[1])
                file.write(line)
                file.flush()
          
