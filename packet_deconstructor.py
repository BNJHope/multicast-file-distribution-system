import struct

from protocol_codes.packet_constants import PacketKeyConstants
from protocol_codes.message_code import MessageCodeEnum
from protocol_codes.server_return_codes import ServerReturnCodes
from file_transmission_config import FileTransmissionConfig

class PacketDeconstructor(PacketStructFormats) :
	
	# translates a given packet
	def translate_packet(packet) :

		packet_header = ""

		# get the header from the packet
		# if the struct cannot parse the packet then
		# return a malformed packet error
		try :
			packet_header = struct.unpack(packet[:struct.calcsize(self.general_header_format)])
		except struct.error:
			return ServerReturnCodes.MALFORMED_PACKET

		# if the protocol does not match then return
		# an incorrect protocol error code
		if(packet_header[PacketKeyConstants.PROTOCOL_KEY_POS].decode() != FileTransmissionConfig.PROTOCOL_NAME) :
			return ServerReturnCodes.NO_PROTCOL_MATCH

		# determines the type of message being transmitted
		message_code = packet_header[PacketKeyConstants.PACKET_TYPE_POS]

		if message_code == MessageCodeEnum.FILE_INIT :
			return self.parse_init_packet(packet)

		elif message_code == MessageCodeEnum.FILE_INIT_RESP :
			return self.parse_init_resp_packet(packet)

		elif message_code == MessageCodeEnum.FILE_DATA :
			return self.parse_file_data_packet(packet)

		elif message_code == MessageCodeEnum.SEQ_CHECK : 
			return self.parse_seq_check_packet(packet)

		elif message_code = MessageCodeEnum.END_OF_FILE_TRANSMISSION :
			return self.parse_end_of_transmission_packet(packet)

		elif message_code = MessageCodeEnum.MISSING_PACKETS_REQ :
			return self.parse_missing_packets_req_packet(packet)

		elif message_code = MessageCodeEnum.SUCCESSFUL_TRANSMISSION :
			return self.parse_successful_transmission_packet(packet)

		else : return ServerReturnCodes.INVALID_CODE_MATCH

	# get the details from the init packet and send them back
	def parse_init_packet(packet) :

		# the format of the init packet struct
		init_format = self.general_header_format + self.init_packet_format

		# get the position of where the packet details ends and where the filename starts
		start_of_file_name_pos = struct.calcsize(init_format)

		#get the first details before the filename
		init_details = struct.unpack(init_format, packet[:start_of_file_name_pos])

		# get the file name
		filename = packet[start_of_file_name_pos:]

		# return an tuple formed of the initial details
		# and the filename
		return init_details + (filename,)

	# parse a response to an initial init packet
	def parse_init_resp_packet(packet) :

		# the format of the init response packet struct
		resp_format = self.general_header_format + self.resp_packet_format

		return struct.unpack(resp_format, packet)

	# parse a file data packet
	def parse_file_data_packet(packet) :

		# the format of the first struct part of the data packet
		data_pack_format = self.general_header_format + self.file_data_packet_format

		# get the size of the initial packet before the file data
		start_of_file_data_pos = struct.calcsize(data_pack_format)

		#get the first details before the file data
		file_data_details = struct.unpack(data_pack_format, packet[:start_of_file_data_pos])

		# get the file data from the end of the packet
		file_data = packet[start_of_file_data_pos:]

		# return a tuple containing the file data details and
		# the file data itself
		return file_data_details + (file_data,)

	# parse a sequence check packet
	def parse_seq_check_packet(packet) :

		# the format of the init response packet struct
		seq_check_format = self.general_header_format + self.seq_check_packet_format

		return struct.unpack(seq_check_format, packet)

	# parse a packet that indicates the end of a 
	# file transmission
	def parse_end_of_transmission_packet(packet) :

		end_transmission_format = self.general_header_format + self.end_transmission_packet_format

		return struct.unpack(end_transmission_format, packet)

	# parse a packet for missing chunks
	def parse_missing_packets_req_packet(packet) :

		# the format of the first struct part of the data packet
		missing_chunks_format = self.general_header_format + self.missing_chunks_packet_format

		# get the size of the initial packet before the list of missing chunks
		start_of_missing_chunks_list = struct.calcsize(missing_chunks_format)

		#get the first details before the list of missing chunks
		missing_chunks_details = struct.unpack(missing_chunks_format, packet[:start_of_missing_chunks_list])

		# get the file data from the end of the packet
		list_of_chunks = packet[start_of_missing_chunks_list:]decode().split(PacketKeyConstants.DATA_SEPARATOR)

		# return a tuple containing the missing chunks details and
		# the list of missing chunks
		return missing_chunks_details + (list_of_chunks,)

	# parse a packet for successful transmission
	def parse_successful_transmission_packet(packet) :

		successful_transmission_format = self.general_header_format + self.successful_transmission_packet_format

		return struct.unpack(successful_transmission_format, packet)
