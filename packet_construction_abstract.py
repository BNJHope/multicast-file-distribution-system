from file_transmission_config import FileTransmissionConfig

class PacketStructFormats :

	# the format for when the file uuid is included
	file_uuid_format = "36s"

	# format for the file name i.e string of length 20
	file_name_format = "20s"

	# specifies the format of how the sequence id is represented
	# in packets
	seq_id_format = "L"

	# unsigned int to represent the id of the chunk in
	# the current sequence
	chunk_id_format = "I"

	# format for the boolean that determines if a packet for
	# missing chunks contains a list of missing chunks or not
	is_missing_chunks_format = "?"

	# format for the file data packets - uses the transmission config's
	# file data per packet to determine the pattern of it
	file_data_format = str(FileTransmissionConfig.FILE_DATA_PER_PACKET_AMOUNT) + "s"

	# the format for the header i.e protocol name and then integer code for message
	general_header_format = "3sI"

	# the format for the init apcket
	init_packet_format = file_uuid_format + seq_id_format

	# the format for the response packet
	resp_packet_format = file_uuid_format

	# the format for a packet containing file data
	file_data_packet_format = file_uuid_format + seq_id_format + chunk_id_format

	# the format for the packet that checks that clients have received
	# all of the packets
	seq_check_packet_format = file_uuid_format + seq_id_format + chunk_id_format

	# the format for packets that are responding to the call for 
	missing_chunks_packet_format = file_uuid_format + seq_id_format + is_missing_chunks_format

	# format for the end transmission packet
	end_transmission_packet_format = file_uuid_format

	# format for the successful transmission packet
	successful_transmission_packet_format = file_uuid_format