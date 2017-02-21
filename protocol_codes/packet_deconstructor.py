import struct

class PacketDeconstructor(PacketStructFormats) :
	
	# translates a given packet
	def translate_packet(packet) :

		# get the header from the packet
		packet_header = struct.unpack(packet[:struct.calcsize(self.general_header_format)])

		message_code = packet_header[]
	p = PacketConstructor()
	id = uuid.uuid1()

	init_pack = p.assemble_file_init_packet("filename.txt", id, 5)
	init_format = p.general_header_format + p.init_packet_format
	print("Details : " + str(struct.unpack(init_format, init_pack[:struct.calcsize(init_format)])) + "File name : " + init_pack[56:].decode())

	resp_pack = p.assemble_file_resp_packet(id)
	resp_format = p.general_header_format + p.resp_packet_format
	print("Details : " + str(struct.unpack(resp_format, resp_pack[:struct.calcsize(resp_format)])))

	data_pack = p.assemble_file_data_packet(id, 4, 6, "jdklawjlkjfajglkjajgijojgsoijeog")
	data_pack_format = p.general_header_format + p.file_data_packet_format
	print("Details : " + str(struct.unpack(data_pack_format, data_pack[:struct.calcsize(data_pack_format)])))
	print("File data : " + data_pack[struct.calcsize(data_pack_format):].decode())
	print(p.assemble_seq_check_packet(id, 4) )
