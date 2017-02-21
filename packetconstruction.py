import struct
import uuid

from protocol_codes.packet_constants import PacketKeyEnum
from protocol_codes.message_code import MessageCodeEnum
from packet_construction_abstract import PacketStructFormats

class PacketConstructor(PacketStructFormats) :

	# assembles a packet to start initial file transmission
	def assemble_file_init_packet(self, filename, file_uuid, num_seqs):

		app_packet = struct.pack(self.init_packet_format, str(file_uuid).encode(), num_seqs) + filename.encode()

		packet = self.assemble_generic_packet_parts(MessageCodeEnum.FILE_INIT, app_packet)

		return packet

	# assemble packet for file init response
	def assemble_file_resp_packet(self, file_uuid):

		app_packet = struct.pack(self.resp_packet_format, str(file_uuid).encode())

		packet = self.assemble_generic_packet_parts(MessageCodeEnum.FILE_INIT_RESP, app_packet)

		return packet

	# assemble packet for a piece of file data, given which sequence it is a part of
	# and also where in the sequence it lies
	def assemble_file_data_packet(self, file_uuid, seq_id, chunk_id, file_data) :

		app_packet = struct.pack(self.file_data_packet_format, str(file_uuid).encode(), seq_id, chunk_id) + file_data.encode()

		packet = self.assemble_generic_packet_parts(MessageCodeEnum.FILE_DATA, app_packet)

		return packet

	# assemble a packet for checking whether or not the client received
	# all of the packets or not
	def assemble_seq_check_packet(self, file_uuid, seq_id) :

		app_packet = struct.pack(self.seq_check_packet_format, str(file_uuid).encode(), seq_id)

		packet = self.assemble_generic_packet_parts(MessageCodeEnum.SEQ_CHECK, app_packet)

		return packet

	# assemble a packet to respond missing chunks call
	def assemble_missing_chunks_packet(self, file_uuid, seq_id, is_missing_chunks, missing_chunk_ids) :

		missing_chunks_part = ""

		if is_missing_chunks :

			missing_chunks_part = self.convert_missing_chunks_list(missing_chunk_ids)

		app_packet = struct.pack(self.missing_chunks_packet_format, str(file_uuid).encode(), seq_id) + missing_chunks_part.encode()

		packet = self.assemble_generic_packet_parts(MessageCodeEnum.MISSING_PACKETS_REQ, app_packet)

		return packet

	# assemble a packet for the end of transmission message
	def assemble_end_transmission_packet(self, file_uuid, last_seq, last_chunk) :

		app_packet = struct.pack(self.end_transmission_packet_format, str(file_uuid).encode(), last_seq, last_chunk)

		packet = self.assemble_generic_packet_parts(MessageCodeEnum.END_OF_FILE_TRANSMISSION, packetdata)

		return packet

	# assembles the packet with the given packet type message and the packet segments
	def assemble_generic_packet_parts(self, packettype, app_packet) :
		return struct.pack(self.general_header_format.encode(), PacketKeyEnum.PROTOCOL_NAME.encode(), packettype) + app_packet

	# convert the list of missing pacets into a string
	# of comma separated values of the packets
	# that are missing
	def convert_missing_chunks_list(missing_chunks_list) :

		return PacketKeyEnum.DATA_SEPARATOR.join(missing_chunks_list)

# def main() :
# 	p = PacketConstructor()
# 	id = uuid.uuid1()

# 	init_pack = p.assemble_file_init_packet("filename.txt", id, 5)
# 	init_format = p.general_header_format + p.init_packet_format
# 	print("Details : " + str(struct.unpack(init_format, init_pack[:struct.calcsize(init_format)])) + "File name : " + init_pack[56:].decode())

# 	resp_pack = p.assemble_file_resp_packet(id)
# 	resp_format = p.general_header_format + p.resp_packet_format
# 	print("Details : " + str(struct.unpack(resp_format, resp_pack[:struct.calcsize(resp_format)])))

# 	data_pack = p.assemble_file_data_packet(id, 4, 6, "jdklawjlkjfajglkjajgijojgsoijeog")
# 	data_pack_format = p.general_header_format + p.file_data_packet_format
# 	print("Details : " + str(struct.unpack(data_pack_format, data_pack[:struct.calcsize(data_pack_format)])))
# 	print("File data : " + data_pack[struct.calcsize(data_pack_format):].decode())
# 	print(p.assemble_seq_check_packet(id, 4) )

# main()