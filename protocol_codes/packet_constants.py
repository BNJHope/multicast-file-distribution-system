class PacketKeyEnum :

	#packet type code
	PACKET_TYPE = 't'

	#packet content
	PACKET = 'p'

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

	#key used in packets to denote a file name
	FILE_NAME_PACKET_KEY = "fn"