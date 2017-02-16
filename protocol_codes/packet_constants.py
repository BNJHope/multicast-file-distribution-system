class PacketKeyEnum :

	# protocol statement
	PROTOCOL_KEY = "prot"

	# name of protocol
	PROTOCOL_NAME = "BHP"

	#packet type code
	PACKET_TYPE = 'type'

	#packet content
	PACKET = 'pack'

	# key used in packets to denote a file name
	FILE_NAME_PACKET_KEY = "flnm"

	# uuid for the file that will be used in future transactions to represent the transmission
	FILE_UUID = "flid"
	
	# separates general values in packet
	VALUE_SEPARATOR = ';'

	#multiple data separator
	DATA_SEPARATOR = ','

	#denotes that a given key is mapped to a given value
	MAPPING_SEPARATOR = ":"

	#denotes the opening of the packet data
	PACKET_OPEN = "{"

	#denotes the closing of the packet data
	PACKET_CLOSE = "}"