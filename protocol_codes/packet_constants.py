class PacketKeyConstants :

	# location of protocol statement in header
	PROTOCOL_KEY_POS = 0

	#packet type code
	PACKET_TYPE_POS = 1

	#position of the file uuid in the packet
	INIT_FILE_UUID_POS = 2

	# position of where the num of sequences is
	# in the initial packet
	INIT_NUM_OF_FILE_SEQUENCES_POS = 3

	# location of filename in local tuple
	INIT_FILENAME_POS = 4

	# location of file uuid in resp
	INIT_RESP_FILE_UUID_POS = 2

	# position of file uuid in file data packet
	DATA_FILE_UUID_POS = 2

	# position of seq id in file data packet
	DATA_SEQUENCE_NUMBER_POS = 3

	# position of data chunk id in file data packet
	DATA_CHUNK_ID_POS = 4

	# location of file data in local tuple
	DATA_FILE_DATA_POS = 5

	# the position of the file uuid in
	# the sequence check packet
	SEQ_CHECK_FILE_UUID_POS = 2

	# the position of the sequence id in
	# the sequence check packet
	SEQ_CHECK_SEQ_ID_POS = 3

	# position of file id in missing chunk packet
	MISSING_CHUNKS_ID_POS = 2

	# position of seq id in missing chunks packet
	MISSING_CHUNKS_SEQ_ID_POS = 3

	# list of missing chunks location
	MISSING_CHUNKS_LIST_OF_MISSING_CHUNKS = 4

	# position of the boolean determining if there are
	# chunks missing or not in the packet
	MISSING_CHUNKS_IS_MISSING_CHUNKS_POS = 4

	#multiple data separator
	DATA_SEPARATOR = ','