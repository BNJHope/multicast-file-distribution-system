from enum import Enum

# numerical codes used to represent results from different actions taken on the server
class ServerReturnCodes(Enum) :
	
	# code for success
	SUCCESS = 1

	# code for when a packet is received that malformed
	MALFORMED_PACKET = 2

	# code for when a packet is received that is not for this protcol
	NO_PROTCOL_MATCH = 3

	# code for when a packet comes in that does not have a valid
	# packet type code
	INVALID_CODE_MATCH = 4