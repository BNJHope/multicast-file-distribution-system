#Enumeration for the message codes
class MessageCodeEnum :

	#Request to see if node has file or not
	FILE_INIT = 1

	#Response for checking when a node has a file or not
	FILE_INIT_RESP = 2

	#Denotes a packet that contains file data
	FILE_DATA  = 3

	#Denotes a packet that contains file data
	SEQ_CHECK = 4

	# denotes the end of a file transmission session
	END_OF_FILE_TRANSMISSION = 5

	# missing packets message
	MISSING_PACKETS_REQ = 6

	# transmission successful code
	SUCCESSFUL_TRANSMISSION = 7