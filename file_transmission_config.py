import math

class FileTransmissionConfig :

	#the address for all multicast operations to happen on
	MCAST_ADDRESS = "229.229.229.229"

	# the port for all mutlicast interactions to happen over
	MCAST_PORT = 45678

	# the port for all TCP control connections
	CONTROL_PORT = 45679

	# amount of file data in bytes to be sent on each file packet
	FILE_DATA_PER_PACKET_AMOUNT = 1024

	# number of packets per sequence
	SEQUENCE_SIZE = 256
