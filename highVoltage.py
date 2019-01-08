# ============================================
# Wiener High Voltage Control Program
# Thomas J Langford, Yale University
# thomas.langford@yale.edu
# ============================================

import os
import subprocess
from array import array
import time


class highVoltage:
    
    def __init__(self, ip):
        self.ip = ip
        
        
    def walk(self, cmd):
        sts = os.popen("snmpwalk -Oqs -v 2c -m +WIENER-CRATE-MIB -c guru " + self.ip + " " + cmd)
        ret = sts.read().split('\n')
        return ret

    def get(self, cmd):
        sts = os.popen("snmpget -Oqs -v 2c -m +WIENER-CRATE-MIB -c guru " + self.ip + " " + cmd)
        ret = sts.read().split('\n')
        return ret
    
    def set(self, cmd):
        sts = os.popen("snmpset -v 2c -m +WIENER-CRATE-MIB -c guru " + self.ip + " " + cmd)
        ret = sts.read().split('\n')
        return ret    
    
    
    def voltagesFromFile(self, fileName):
        
        with open(fileName,'r') as file:
            data = file.read().split('\r')        # Switch to appropriate line-ending
            
        voltageArr = []
        channelArr = []

        for line in data[0:-1]:
            channelArr.append(line.split(' ')[0].split('.u')[1])
            voltageArr.append(line.split(' ')[1])
                
        return channelArr, voltageArr
        
        
    def voltagesToFile(self, fileName=None):
        
        sts = self.walk("outputVoltage")
        if(fileName == None):
            fileName = "voltages.txt"
        
        with open(fileName,'w') as f:
            for row in sts:    
                f.write(row + '\r')
            
        
    def setVoltages(self, channelArr, voltageArr):
    
        for i in range(len(channelArr)):
            rate = "outputVoltageRiseRate.u" + str(channelArr[i]) + " F " + "100"
            self.set(rate)
            v = "outputVoltage.u" + str(channelArr[i]) + " F " + str(voltageArr[i])
            self.set(v)
            if(voltageArr[i] != '0'):
                on  = "outputSwitch.u" + str(channelArr[i]) + " i 1"
                self.set(on)
            else:
                off = "outputSwitch.u" + str(channelArr[i]) + " i 0" 
                self.set(off)
    
    def checkVoltages(self, channelArr=None):
        
        if channelArr == None:
            name = "outputName"
            sts = self.walk(name)
            channelArr = []
            for row in sts:
                channelArr.append(row.split(' ')[1][1:])
            cmd = "outputMeasurementSenseVoltage"
            sts = self.walk(cmd)
        else:
            sts = []
            for ch in channelArr:
                cmd = "outputMeasurementSenseVoltage.u" + str(ch)
                sts.append(self.get(cmd)[0])
        voltageArr = []
                
        for row in sts:
            tmp = row.split(' ')
            voltageArr.append(tmp[1])
                
        return channelArr, voltageArr    
        
    def checkCurrents(self, channelArr=None):
        if channelArr == None:
            name = "outputName"
            sts = self.walk(name)
            channelArr = []
            for row in sts:
                channelArr.append(row.split(' ')[1][1:])
            cmd = "outputMeasurementCurrent"
            sts = self.walk(cmd)
        else:
            sts = []
            for ch in channelArr:
                cmd = "outputMeasurementCurrent.u" + str(ch)
                sts.append(self.get(cmd)[0])
        currentArr = []
                
        for row in sts:
            tmp = row.split(' ')
            currentArr.append(tmp[1])
                
        return channelArr, currentArr    
        

    def setDefaults(self):

        fileName = "HVDefaults.txt"        
        self.voltagesToFile(fileName)
        
    def setLastUsedVoltages(self):
        
        fileName = "LastUsedHVSettings.txt"        

        self.voltagesToFile(fileName)        

    def status(self):
        channel,voltage = self.checkVoltages()
        channel,current = self.checkCurrents()
        outTuple = zip(channel,voltage,current)
        return outTuple

    def logStatus(self,fileName):
        outFile = open(fileName,'a')
        outFile.write(str(time.time())+'\t')
        
        for element in self.status():
            outFile.write(str(element)+'\t')
        outFile.write('\n')
        outFile.close()

    def startUp(self, fileName=None):
        if fileName is None:
            fileName = "LastUsedHVSettings.txt"
        cA, vA = self.voltagesFromFile(fileName)
        print("Loading voltages from file: " + fileName)
        self.setVoltages(cA, vA)

    def shutDown(self):
        from time import sleep
        cA, vA = self.checkVoltages()
        fileName = "LastUsedHVSettings.txt"
        self.voltagesToFile(fileName)
        self.setVoltages(cA, [0] * len(cA))

        for i in range(100):
            sleep(2)
            print("Ramping down...")
            voltage = float(self.checkVoltages(cA[-1])[1][0])
            if voltage < 10:
                break
        print("Voltages are down")


if __name__ == "__main__":
    from sys import argv
    hv = highVoltage('10.10.0.1')
        
    if "on" in argv[1]:
        hv.startUp(fileName="LastUsedHVSettings.txt")
    elif "off" in argv[1]:
        hv.shutDown()
    elif "status" in argv[1]:
        chA, vA = hv.checkVoltages()
        chA, cA = hv.checkCurrents()
        for i in range(len(chA)):
            print("Ch:"+chA[i] +", "+ vA[i]+"V, " + cA[i]+"A, " + '\n')
