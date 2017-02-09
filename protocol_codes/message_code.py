#Enumeration for the message codes
class MessageCodeEnum :

	#Request to see if node has file or not
	FILE_REQ = "1"

	#Response for checking when a node has a file or not
	FILE_REQ_RESP = "2"

	#Denotes a packet that holds information about an incoming file transmission
	FILE_START_INFO = "3"

	#Denotes a packet that contains file data
	FILE_DATA = "4"