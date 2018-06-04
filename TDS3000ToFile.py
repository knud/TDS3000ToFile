#-------------------------------------------------------------------------------
# Name:  TDS3000ToFile
#  Save Hardcopy to computer using PyVisa for TDS3000 series oscilloscope
#
# Created:  2016-02-27
#
# Development Environment: Python 2.7 PyVisa 1.8, OS X 10.11.3
#
# Compatible Instruments: TDS3000 series
#
# Compatible Interfaces: Ethernet 
#
#-------------------------------------------------------------------------------

import time, warnings # std visa libraries
import visa # https://pyvisa.readthedocs.org/en/stable/
import sys, getopt

# convenience method to convert an array of bytes to an int
def from_bytes (data, big_endian = False):
	if isinstance(data, str):
		data = bytearray(data)
	if big_endian:
		data = reversed(data)
	num = 0
	for offset, byte in enumerate(data):
		num += byte << (offset * 8)
	return num

# Some definitions

vc = visa.constants # Alias for easier reading

# Modify the following lines to configure this script for your instrument
#==============================================
visaResourceAddr = 'TDS3054'
fileSaveLocation = r'/Users/knud/foo'
bufferSize = 1024

#==============================================

def captureToFile (address, outputFileName):
	# Open session to instrument
	rm = visa.ResourceManager()
	lib = rm.visalib
	scope = rm.open_resource("TCPIP::"+address+"::inst0::INSTR")
	scope.timeout = 10000
	startDelaySec = 1

	# Some settings depend on which interface is being used
	interface = lib.get_attribute(scope.session, vc.VI_ATTR_INTF_TYPE)[0]
	port = 'GPIB'

	print(scope.query("*IDN?"))
	scope.write("HARDCOPY:FORMAT BMPColor")
	scope.write("HARDCOPY:INKSAVER OFF")
	scope.write("HARDCOPY:LAYOUT PORTRait")
	scope.write("HARDCOPY:PALETTE NORMAL")
	scope.write("HARDCOPY:PORT " + port)
	scope.write("HARDCOPY START")

	print("Starting Transfer in: ")
	for x in range(0, startDelaySec):
			print(str.format("{0}...", startDelaySec - x))
			time.sleep(1)
	print("Now!")

	# Read the BMP header bytes and extract the file size
	warnings.filterwarnings("ignore", category=Warning) #The read will produce a VI_SUCCESS_MAX_CNT warning so suppress
	imgBytes = lib.read(scope.session, 14)[0]
	lengthBytes = imgBytes[2:6]
	fileSize = from_bytes(lengthBytes, False)
	print(str.format("file size is {0}", fileSize))
	bytesLeft = fileSize - 14

	# Read the rest of the image
	while bytesLeft > 0:
		imgBytes = imgBytes + lib.read(scope.session, bufferSize)[0]
		bytesLeft = bytesLeft - bufferSize

		if bytesLeft < bufferSize:
			imgBytes = imgBytes + lib.read(scope.session, bytesLeft)[0]
			bytesLeft = 0


	# Save the bytes to a file
	imgFile = open(outputFileName+'.bmp', "wb")
	imgFile.write(imgBytes)
	imgFile.close()

	print("Transfer Complete!")
	print("Image saved to " + outputFileName+'.bmp')

	scope.close()
	rm.close()

def main(argv):
   inputfile = ''
   outputfile = ''
   
   if len(sys.argv) != 5:
      print 'TDS3000ToFile.py -e <instrument ipv4 address> -o <outputfile>'
      print 'Not enough arguments'
      sys.exit(2)
   try:
      opts, args = getopt.getopt(argv,"he:o:",["ipv4Addr=","ofile="])
   except getopt.GetoptError:
      print 'TDS3000ToFile.py -e <instrument ipv4 address> -o <outputfile>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'test.py -e <instrument ipv4 address> -o <outputfile>'
         sys.exit()
      elif opt in ("-e", "--ipv4Addr"):
         address = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg
   print 'Instrument address is ', address
   print 'Output file is ', outputfile

   captureToFile(address, outputfile)

if __name__ == "__main__":
   main(sys.argv[1:])

