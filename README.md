# TDS3000ToFile
Simple Python to transfer Tektronix TDS3000 scope images to file

# Requirements
Needs PyVISA, which can be found at (pyvisa.org)[https://pyvisa.readthedocs.org/en/stable/]

To get pyvisa to work correctly, I had to add to .bash_profile
````
#
# PyVISA
#
export PYTHONPATH=/Library/Python/2.7/site-packages:$PYTHONPATH
````

##
#
# Example
#
python TDS3000ToFile.py -e 192.168.1.11 -o screen_cap_20180221

