import socket
import select
import uuid
import os
import math
import struct
import copy
import time

from FileTransferAbstract import FileTransferAbstract
from packetconstruction import PacketConstructor
from file_transmission_config import FileTransmissionConfig
from packet_deconstructor import PacketDeconstructor
from protocol_codes.packet_constants import PacketKeyConstants
from protocol_codes.message_code import MessageCodeEnum
from protocol_codes.server_return_codes import ServerReturnCodes

class FileTransferServer(FileTransferAbstract):

    # target nodes to go for
    target_node_addresses = None

    # the set of connections to target nodes
    target_nodes = []

    # current address of the server
    server_address = socket.gethostname()

    # constructs packets to be sent between client and server
    packet_constructor = None

    # parses packets received from clients
    packet_parser = None

    # socket that broadcasts file segments to all listening clients
    filestream_udp_sock = None

    # constructor for server
    def __init__(self):

        # get the list of target nodes from the file transmission config
        self.target_node_addresses = FileTransmissionConfig.CLIENT_ADDRESS_LIST

        # read in values from the config file for MCAST_ADDRESS and MCAST_PORT
        self.set_up_config_file_values()

        # initialise a new packet constructor
        self.packet_constructor = PacketConstructor()

        # initialise packet parser
        self.packet_parser = PacketDeconstructor()

        #set up the udp socket
        self.filestream_udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.filestream_udp_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 20)

    def start_send_file(self, filename) :

        # set up control sockets with the clients
        self.set_up_client_control_sockets()

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

        # stay connected until there is at least one receiver
        stay_connected = True

        while(stay_connected) :

            ready_to_read, ready_to_write, err = \
                   select.select(
                      [],
                      self.target_nodes,
                      [],
                      0.001)

            print("Found Connections : " + str(len(ready_to_write)))

            # for every connection in the ready to write list,
            # try to send and receive the initial connection
            # to set up the receiver for file transmission
            for s in ready_to_write :

                stay_connected = False

                # assemble the file transmission init packet
                packet_to_send = self.packet_constructor.assemble_file_init_packet(filename, file_uuid.encode(), num_seqs)
                sent = s.send(packet_to_send)
                
                # calculate the size in bytes of the response packet
                size_of_resp_packet = struct.calcsize(self.packet_constructor.general_header_format + self.packet_constructor.resp_packet_format)
                received_packet = s.recv(size_of_resp_packet)

                refined_received_packet = self.packet_parser.translate_packet(received_packet)

                # if the uuids do not match
                if refined_received_packet[PacketKeyConstants.INIT_RESP_FILE_UUID_POS].decode() != file_uuid :
                    print("UUIDS DO NOT MATCH IN RESP PACKET")

        return

    # send the given file
    def send_file(self, filename, file_id, num_seqs) :

        # open the file to be transferred in reading mode
        read_file = os.open(filename, os.O_RDWR|os.O_CREAT)

        # the current packet number that we have reached
        current_packet_num = 0

        # get all the control listeners and set up
        # writing to the udp stream
        control_messages, file_data_stream_list , _ = \
                select.select(
                  [],
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
            num_of_chunks_sent = self.broadcast_sequence_chunks(seq_num, file_id, read_file)

            # sleep so that all UDP packets can go through
            time.sleep(0.001)

            # handle any chunks of this sequence that need to be sent again
            self.handle_repeat_packets(file_id, seq_num, read_file, num_of_chunks_sent)

        # send the end transmission packet
        self.send_end_transmission_packet(file_id)

    # broadcast sequence
    def broadcast_sequence_chunks(self, seq_id, file_id, read_file) :

            return self.broadcast_chunks(range(FileTransmissionConfig.SEQUENCE_SIZE), seq_id, file_id, read_file)

    # broadcast the given set of chunks
    def broadcast_chunks(self, chunks, seq_id, file_id, read_file) :

        # for all of the chunks in this sequence
        for chunk_id in chunks :

            file_data = self.get_file_chunk(seq_id, chunk_id, read_file)

            # if there is no more file data to read then 
            # return the id of the last chunk that we read
            if(file_data == b'') :

                return chunk_id - 1

            packet = self.packet_constructor.assemble_file_data_packet(file_id, seq_id, chunk_id, file_data)

            self.filestream_udp_sock.sendto(packet, (self.MCAST_ADDRESS, self.MCAST_PORT))
        
        return chunk_id

    # listens to all control signals from the clients and resends and segments from the file that they want broadcasted again
    def handle_repeat_packets(self, file_uuid, seq_id, read_file, num_of_chunks_sent) :

        clients_to_ask = copy.copy(self.target_nodes)

        all_clients_data_received = False

        missing_packets_list = []

        # while clients are still missing data
        while clients_to_ask :

            # for every client we have in the list of connections
            for client in clients_to_ask :
        
                # send an end of sequence message and get the missing packets from the client
                client_missing_packets = self.send_end_of_sequence_message(client, file_uuid, seq_id, num_of_chunks_sent)

                # if they are not missing packets then
                # remove the client from the list to ask
                if not client_missing_packets :

                    clients_to_ask.remove(client)

                else :

                    # add the missing packets of this client to the current list
                    # of missing packets
                    missing_packets_list.extend(int(x) for x in client_missing_packets)

            # broadcast the missing chunks and then ask around again afterwards
            # for missing packets until all clients have received the packets for
            # this sequence
            self.broadcast_chunks(missing_packets_list, seq_id, file_uuid, read_file)
        
            time.sleep(0.001)

    # send end of sequence message to ask client
    # which packets they are missing if any
    def send_end_of_sequence_message(self, client, file_uuid, seq_id, chunks_sent) :

        list_of_chunks = []

        end_of_seq_packet = self.packet_constructor.assemble_seq_check_packet(file_uuid, seq_id, chunks_sent)

        sent_bytes = client.send(end_of_seq_packet)

        size_of_missing_chunks_packet = struct.calcsize(self.packet_constructor.general_header_format + self.packet_constructor.missing_chunks_packet_format) + 2048
        
        received_packet = client.recv(size_of_missing_chunks_packet)

        refined_received_packet = self.packet_parser.translate_packet(received_packet)

        # make sure the packet is a packet to request for missing packets
        if(refined_received_packet[PacketKeyConstants.PACKET_TYPE_POS] == MessageCodeEnum.MISSING_PACKETS_REQ) :

            # if the client has said they are missing chunks
            if refined_received_packet[PacketKeyConstants.MISSING_CHUNKS_IS_MISSING_CHUNKS_POS] is True :

                list_of_chunks = refined_received_packet[PacketKeyConstants.MISSING_CHUNKS_LIST_OF_MISSING_CHUNKS]

            else :

                list_of_chunks = []
        
        else :
            print("UNEXPECTED PACKET TYPE")

            return ServerReturnCodes.INVALID_CODE_MATCH

        return list_of_chunks

    # get the required file chunk using the sequence id and the chunk id
    def get_file_chunk(self, seq_id, chunk_id, read_file) :

        # get the offset in the file
        offset = (seq_id * FileTransmissionConfig.SEQUENCE_SIZE * FileTransmissionConfig.FILE_DATA_PER_PACKET_AMOUNT) + (chunk_id * FileTransmissionConfig.FILE_DATA_PER_PACKET_AMOUNT)

        # set the read position of the file 
        os.lseek(read_file, offset, os.SEEK_SET)

        return os.read(read_file, FileTransmissionConfig.FILE_DATA_PER_PACKET_AMOUNT)

    # gets the number of sequences that will be transmitted in total
    def get_num_of_seqs(self, filename) :

        # get the size of the file
        size_of_file = os.path.getsize(filename)

        # get the total number of data packets that
        # the file can be split up into
        total_chunks = math.ceil(float(size_of_file) / float(FileTransmissionConfig.FILE_DATA_PER_PACKET_AMOUNT))

        total_seqs = math.ceil(float(total_chunks) / float(FileTransmissionConfig.SEQUENCE_SIZE)) 

        return total_seqs

    # set up the socket connections
    def set_up_client_control_sockets(self) :

        # for every node address in the set of target
        # node addresses
        for index in range(len(self.target_node_addresses)) :

            #get the current node_addr to work with
            node_addr = self.target_node_addresses[index]

            # make a new socket with the addresses
            new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # connect the socket
            new_sock.connect((node_addr, self.CONTROL_PORT))

            # put the socket connection in the list
            self.target_nodes.append(new_sock)
