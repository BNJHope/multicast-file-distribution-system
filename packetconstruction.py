import struct
import uuid

from protocol_codes.packet_constants import PacketKeyEnum
from protocol_codes.message_code import MessageCodeEnum

class PacketConstructor :

	# assembles a packet to start initial file transmission
	def assemble_file_init_packet(self, filename, file_uuid):

		# list of all the packet data to have
		packetdata = []

		# the data for the filename to add to the packet
		packetdata.append(self.assemble_packet_value(PacketKeyEnum.FILE_NAME_PACKET_KEY, filename))

		# uuid to determine the transfer id for future references to this file transfer
		packetdata.append(self.assemble_packet_value(PacketKeyEnum.FILE_UUID, file_uuid))

		packet = self.assemble_generic_packet_parts(MessageCodeEnum.FILE_INIT, packetdata)

		return packet

	# assemble packet for file init response
	def assemble_file_resp_packet(self, file_uuid):

		# list of all the packet data to have
		packetdata = []

		# uuid to determine the transfer id for future references to this file transfer
		packetdata.append(self.assemble_packet_value(PacketKeyEnum.FILE_UUID, file_uuid))

		packet = self.assemble_generic_packet_parts(MessageCodeEnum.FILE_INIT_RESP, packetdata)

		return packet

	# assemble packet for file start packet for meta data
	def assemble_file_start_packet(self, file_uuid, num_seqs) :

		# list of all the packet data to have
		packetdata = []

		# uuid to determine the transfer id for future references to this file transfer
		packetdata.append(self.assemble_packet_value(PacketKeyEnum.FILE_UUID, file_uuid))

		# number of sequuences that will be sent
		packetdata.append(self.assemble_packet_value(PacketKeyEnum.NUM_OF_FILE_SEQUENCES , num_seqs))

		packet = self.assemble_generic_packet_parts(MessageCodeEnum.FILE_START_INFO, packetdata)

		return packet

	# assemble packet for a piece of file data, given which sequence it is a part of
	# and also where in the sequence it lies
	def assemble_file_data_packet(self, file_uuid, seq_id, chunk_id, file_data) :

		# list of all the packet data to have
		packetdata = []

		# uuid to determine the transfer id for future references to this file transfer
		packetdata.append(self.assemble_packet_value(PacketKeyEnum.FILE_UUID, file_uuid))
	
		# sequence id - the sequence which this packet comes in
		packetdata.append(self.assemble_packet_value(PacketKeyEnum.SEQUENCE_NUMBER, seq_id))

		# chunk id - where the packet lies in the sequence of chunks
		packetdata.append(self.assemble_packet_value(PacketKeyEnum.CHUNK_ID, chunk_id))

		# file data - the actual data to be transmitted in this packet
		packetdata.append(self.assemble_packet_value(PacketKeyEnum.FILE))

		packet = self.assemble_generic_packet_parts(MessageCodeEnum.FILE_DATA, packetdata)

		return packet

	# assemble a packet for the end of transmission message
	def assemble_end_transmission_packet(self, file_uuid) :

		# list of all the packet data to have
		packetdata = []

		# uuid to determine the transfer id for future references to this file transfer
		packetdata.append(self.assemble_packet_value(PacketKeyEnum.FILE_UUID, file_uuid))

		packet = self.assemble_generic_packet_parts(MessageCodeEnum.END_OF_FILE_TRANSMISSION, packetdata)

		return packet

	# assemble a packet for missing chunks
	def assemble_missing_chunks_packet(self, file_uuid, missing_chunk_ids) :

		# list of all the packet data to have
		packetdata = []

		# uuid to determine the transfer id for future references to this file transfer
		packetdata.append(self.assemble_packet_value(PacketKeyEnum.FILE_UUID, file_uuid))

		packet = self.assemble_generic_packet_parts(MessageCodeEnum.MISSING_PACKETS_REQ, packetdata)

		return packet


	# # assemble a packet for successful transmission
	# def assemble_successful_transmission_packet(self, file_uuid) :

	# def assemble_generic_struct(self, packettype, packetsegs) :


	# assembles the packet with the given packet type message and the packet segments
	def assemble_generic_packet_parts(self, packettype, packetsegs) :

		# overall packet that we are sending
		packet = ""

		# the protocol that the packet is using
		protocolheader = self.assemble_packet_value(PacketKeyEnum.PROTOCOL_KEY, PacketKeyEnum.PROTOCOL_NAME)

		# the type of the message that we are sending
		messagetype = self.assemble_packet_value(PacketKeyEnum.PACKET_TYPE, packettype)

		# the application packet
		packetcontent = PacketKeyEnum.PACKET_OPEN

		# put the application packet together
		for item in packetsegs :
			packetcontent += item

		# close the packet content
		packetcontent += PacketKeyEnum.PACKET_CLOSE

		# the application packet to add to the packet to send
		app_packet = self.assemble_packet_value(PacketKeyEnum.PACKET, packetcontent)

		# add protocol header to the packet
		packet += protocolheader

		# add message type to the header
		packet += messagetype

		# add application packet to the overall packet
		packet += app_packet

		return packet

	# takes a key and a value and assembles it in the packet format
	def assemble_packet_value(self, key, value) :
		return key + PacketKeyEnum.MAPPING_SEPARATOR + value + PacketKeyEnum.VALUE_SEPARATOR

	# assembles the missing chunks part of the packet
	# def assemble_missing_chunks_data(self, missing_chunks) :

	# 	# the data that will be attached to the packet in the end
	# 	packet_value = ""

	# 	# for every chunk in the set of missing chunks, add it to
	# 	# the packet value to return 
	# 	for chunk in missing_chunks :



	# 	return packet_value
