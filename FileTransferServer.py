import socket
import select
import uuid
import os
import math

from FileTransferAbstract import FileTransferAbstract
from packetconstruction import PacketConstructor
from file_transmission_config import FileTransmissionConfig

class FileTransferServer(FileTransferAbstract):

    # target nodes to go for
    target_nodes = ["pc3-034-l.cs.st-andrews.ac.uk"]

    # current address of the server
    server_address = socket.gethostname()

    # constructs packets to be sent between client and server
    packet_constructor = None

    # socket connecting server to clients to send and receive
    # control messages
    server_control_sock = None

    # socket that broadcasts file segments to all listening clients
    filestream_udp_sock = None

    # constructor for server
    def __init__(self):

        # read in values from the config file for MCAST_ADDRESS and MCAST_PORT
        self.set_up_config_file_values()

        # initialise a new packet constructor
        self.packet_constructor = PacketConstructor()

        # set up the TCP control connection
        self.server_control_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #set up the udp socket
        self.filestream_udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.filestream_udp_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 20)

    def send_file(self, filename) :

        # get the number of sequences that will be used in the file transmission
        # to split the file up
        num_seqs = self.get_num_of_seqs(filename)

        # file id to pass for this file session
        file_id = str(uuid.uuid1())

        # send the init packet
        self.send_init(filename, file_id, num_seqs)

        self.send_file(filename, file_id, num_seqs)
        
    # send a file to all available clients
    def send_init(self, filename, file_uuid, num_seqs) :

        self.server_control_sock.bind((self.server_address, self.CONTROL_PORT))

        self.server_control_sock.listen(5)

        while(True) :

            ready_to_read, ready_to_write, err = \
                   select.select(
                      [self.server_control_sock],
                      [],
                      [],
                      0.0001)

            print(len(ready_to_read), len(ready_to_write))
            for s in ready_to_read :
                conn, _ = s.accept()
                packet = self.packet_constructor.assemble_file_init_packet(filename, file_uuid)
                sent = conn.send(packet.encode())
                print("trying to exit")

        return

    # send the given file
    def send_file(filename, file_id, num_seqs) :

        # open the file to be transferred in reading mode
        read_file = open(filename, 'r')

        # the current packet number that we have reached
        current_packet_num = 0

        # get all the control listeners and set up
        # writing to the udp stream
        control_messages, file_data_stream_list , _ = \
                select.select(
                  [self.server_control_sock],
                  [self.filestream_udp_sock],
                  [],
                  0.0001)

        # determines if clients missed packets or not
        clients_missed_packets = False

        # the list of packets that were missed and need to be rebroadcasted
        missed_packets_list = []

        # for every sequence of packets
        for seq_num in range(num_seqs):
            
            #broadcast the inital chunks of this sequence
            self.broadcast_sequence_chunks(seq_num, file_id, read_file)

            # handle any chunks of this sequence that need to be sent again
            self.handle_repeat_packets(seq_num, control_messages, read_file)

    # broadcast sequence
    def broadcast_sequence_chunks(self, seq_id, file_id, read_file) :

            # for all of the chunks in this sequence
            for chunk_id in range (FileTransmissionConfig.SEQUENCE_SIZE) :

                file_data = self.get_file_chunk(seq_id, chunk_id, read_file)

                packet = self.assemble_file_data_packet(file_id, seq_id, chunk_id, file_data)

                self.filestream_udp_sock.sendto(packet, (self.MCAST_ADDRESS, self.MCAST_PORT))

    # listens to all control signals from the clients and resends and segments from the file that they want broadcasted again
    def handle_repeat_packets(self, seq_id, control_messages, read_file) :

        print("handle repeat section reached")

    # get the required file chunk using the sequence id and the chunk id
    def get_file_chunk(self, seq_id, chunk_id, read_file) :

        # get the offset in the file
        offset = (seq_id * FileTransmissionConfig.SEQUENCE_SIZE * FileTransmissionConfig.FILE_DATA_PER_PACKET_AMOUNT) + (chunk_id + FileTransmissionConfig.FILE_DATA_PER_PACKET_AMOUNT)

        # set the read position of the file 
        os.lseek(read_file, offset, os.SEEK_SET)

        return read_file.read(FILE_DATA_PER_PACKET_AMOUNT)

    # gets the number of sequences that will be transmitted in total
    def get_num_of_seqs(self, filename) :

        # get the size of the file
        size_of_file = os.path.getsize(filename)

        # get the total number of data packets that
        # the file can be split up into
        total_chunks = math.ceil(float(size_of_file) / float(FileTransmissionConfig.FILE_DATA_PER_PACKET_AMOUNT))

        return math.ceil(float(total_chunks) / float(FileTransmissionConfig.SEQUENCE_SIZE)) 
