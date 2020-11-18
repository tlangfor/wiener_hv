# wiener_hv

An object-oriented python wrapper for sending SNMP commands to Wiener high voltage modules. 


## Requirements

- python (currently only tested on python2, migration to python3 in-progress)
- WIENER-CRATE-MIB.mib file installed in either local directory or `/usr/local/share/snmp/mibs/`

## Operation

The `highVoltage` class contains methods for applying voltages to individual channels or the whole board. 
Voltages can be read from or outputted to text files.

```
from highVoltage import highVoltage
hv = highVoltage('10.10.0.1')    # input correct IP address here

# read values from file named HVDefaults.txt
channelArr, voltageArr = hv.voltageFromFile("HVDefaults.txt")

# apply values to boards
hv.setVoltages(channelArr, voltageArr)

# check voltages and print them to terminal
hv.checkVoltages()

```

## Command-line operation
The script can also be called from the command line with three arguments: `on`, `off`, and `status`. 

`python highVoltage.py on`
This will pull voltages from the default file (`LastUsedHVSettings.txt`) and apply them to the boards.

`python highVoltage.py off`
This will shutdown all channels of the crate

`python highVoltage.py status`
This will print to screen the channels with their read-out voltage and current. 


