import math

class FileTransmissionConfig :

	# name of protocol
	PROTOCOL_NAME = "BHP"
	
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

	# address of the server node
	SERVER_ADDRESS = "pc3-035-l.cs.st-andrews.ac.uk"

	# list of clients to address to
	CLIENT_ADDRESS_LIST = [ "pc3-001-l.cs.st-andrews.ac.uk",
							# "pc3-002-l.cs.st-andrews.ac.uk",
							# "pc3-003-l.cs.st-andrews.ac.uk",
							# "pc3-004-l.cs.st-andrews.ac.uk",
							# "pc3-005-l.cs.st-andrews.ac.uk",
							# "pc3-006-l.cs.st-andrews.ac.uk",
							# "pc3-016-l.cs.st-andrews.ac.uk",
							# "pc3-008-l.cs.st-andrews.ac.uk",
							# "pc3-009-l.cs.st-andrews.ac.uk",
							# "pc3-010-l.cs.st-andrews.ac.uk",
							# "pc3-011-l.cs.st-andrews.ac.uk",
							# "pc3-012-l.cs.st-andrews.ac.uk",
							# "pc3-013-l.cs.st-andrews.ac.uk",
							# "pc3-014-l.cs.st-andrews.ac.uk",
							# "pc3-015-l.cs.st-andrews.ac.uk"
							]

	# maximum length of a file name in a packet
	MAX_FILE_NAME_LENGTH = 256