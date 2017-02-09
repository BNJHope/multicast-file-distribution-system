from protocol_codes.packet_constants import PacketKeyEnum
from protocol_codes.message_code import MessageCodeEnum

class PacketConstructor :

	# assembles a packet to request for a file
	def assemble_file_request_packet(self, filename):

		# list of all the packet data to have
		packetdata = []

		# the data for the filename to add to the packet
		filename_packet_data = PacketKeyEnum.FILE_NAME_PACKET_KEY + PacketKeyEnum.MAPPING_SEPARATOR + filename

		packetdata.append(filename_packet_data)

		packet = self.assemble_generic_packet_parts(MessageCodeEnum.FILE_REQ, packetdata)

		return packet

	# assembles the packet with the given packet type message and the packet segments
	def assemble_generic_packet_parts(self, packettype, packetsegs) :

		# overall packet that we are sending
		packet = ""

		# the type of the message that we are sending
		messagetype = PacketKeyEnum.PACKET_TYPE + PacketKeyEnum.MAPPING_SEPARATOR + packettype + PacketKeyEnum.VALUE_SEPARATOR 

		# the packet content assembled
		packetcontent = PacketKeyEnum.PACKET + PacketKeyEnum.MAPPING_SEPARATOR + PacketKeyEnum.PACKET_OPEN

		for item in packetsegs :
			packetcontent += item + PacketKeyEnum.VALUE_SEPARATOR

		packetcontent += PacketKeyEnum.PACKET_CLOSE

		packet += messagetype
		packet += packetcontent

		return packet


def main() :
	pc = PacketConstructor()
	print(pc.assemble_file_request_packet("Testfile.txt"))

main()