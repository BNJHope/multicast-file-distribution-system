class PacketKeyEnum :

	#packet type code
	PACKET_TYPE = 'type'

	#packet content
	PACKET = 'pack'

	# key used in packets to denote a file name
	FILE_NAME_PACKET_KEY = "flnm"

	# protocol statement
	PROTCOL_KEY = "prot"

	# name of protocol
	PROTCOL_NAME = "BHP"

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