from enum import Enum

class PacketKeyEnum(Enum) :

	#packet type code
	PACKET_TYPE = 't'

	#packet content
	PACKET = 'p'

	#packet separator
	PACKET_SEPARATOR = ';'

	#multiple data separator
	DATA_SEPARATOR = ','