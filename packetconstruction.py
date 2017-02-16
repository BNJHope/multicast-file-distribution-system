from protocol_codes.packet_constants import PacketKeyEnum
from protocol_codes.message_code import MessageCodeEnum
import uuid

class PacketConstructor :

	# assembles a packet to start initial file transmission
	def assemble_file_init_packet(self, filename, file_uuid):

		# list of all the packet data to have
		packetdata = []

		# the data for the filename to add to the packet
		filename_packet_data = self.assemble_packet_value(PacketKeyEnum.FILE_NAME_PACKET_KEY, filename)

		# uuid to determine the transfer id for future references to this file transfer
		file_uuid_packet_data = self.assemble_packet_value(PacketKeyEnum.FILE_UUID, file_uuid)

		packetdata.append(filename_packet_data)
		packetdata.append(file_uuid_packet_data)

		packet = self.assemble_generic_packet_parts(MessageCodeEnum.FILE_INIT, packetdata)

		return packet

	# assemble packet for file init response
	def assemble_file_resp_packet(self, uuid):

		# list of all the packet data to have
		packetdata = []

		# uuid to determine the transfer id for future references to this file transfer
		file_uuid_packet_data = self.assemble_packet_value(PacketKeyEnum.FILE_UUID, uuid)

		packetdata.append(file_uuid_packet_data)

		packet = self.assemble_generic_packet_parts(MessageCodeEnum.FILE_INIT_RESP, packetdata)

		return packet

	# assemble packet for file start packet for meta data
	def assemble_file_start_packet(self, filename, numberOfFileChunks) :

		# list of all the packet data to have
		packetdata = []


	# assembles the packet with the given packet type message and the packet segments
	def assemble_generic_packet_parts(self, packettype, packetsegs) :

		# overall packet that we are sending
		packet = ""

		# the protocol that the packet is using
		protocolheader = self.assemble_packet_value(PacketKeyEnum.PROTOCOL_KEY, PacketKeyEnum.PROTOCOL_NAME)

		# the type of the message that we are sending
		messagetype = self.assemble_packet_value(PacketKeyEnum.PACKET_TYPE, packettype)

		# the packet content assembled
		packetcontent = PacketKeyEnum.PACKET + PacketKeyEnum.MAPPING_SEPARATOR + PacketKeyEnum.PACKET_OPEN

		for item in packetsegs :
			packetcontent += item

		# close the packet content
		packetcontent += PacketKeyEnum.PACKET_CLOSE

		# add protocol header to the packet
		packet += protocolheader

		# add message type to the header
		packet += messagetype

		# add packet contents to the packet
		packet += packetcontent

		return packet

	# takes a key and a value and assembles it in the packet format
	def assemble_packet_value(self, key, value) :
		return key + PacketKeyEnum.MAPPING_SEPARATOR + value + PacketKeyEnum.VALUE_SEPARATOR

def main() :
	uuidtouse = str(uuid.uuid1())
	p = PacketConstructor()
	res1 = p.assemble_file_init_packet("testfile.txt", uuidtouse)
	res2 = p.assemble_file_resp_packet(uuidtouse)
	print(res1, "\n", res2)

main()