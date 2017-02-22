import socket
import uuid
import select 
import struct
import os
import sys
import zlib

from FileTransferAbstract import FileTransferAbstract
from packetconstruction import PacketConstructor
from packet_deconstructor import PacketDeconstructor
from file_transmission_config import FileTransmissionConfig
from protocol_codes.packet_constants import PacketKeyConstants
from protocol_codes.message_code import MessageCodeEnum
from protocol_codes.server_return_codes import ServerReturnCodes

class FileTransferClient(FileTransferAbstract):

    # address of the file server node
    server_node = ""

    # constructs packets to be sent between client and server
    packet_constructor = None

    # parses packets from the server
    packet_parser = None

    # socket connecting this client over TCP to the server
    control_sock = None

    # socket for receiving data over the udp connection
    file_data_sock = None

    # the connection set up with the server
    server_connection = None

    # the file which we write to
    file_to_write = None

    # constructor for server
    def __init__(self):

        self.server_node = FileTransmissionConfig.SERVER_ADDRESS

        # read in values from the config file for MCAST_ADDRESS and MCAST_PORT
        self.set_up_config_file_values()

        # set up a new instance of the packet constructor
        self.packet_constructor = PacketConstructor()

        # make new instance of packet parser
        self.packet_parser = PacketDeconstructor()

        # set up and connect to server socket
        self.control_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # wait to receive a file from the server
    def listen_for_file(self) :

        self.control_sock.bind((socket.gethostname(), self.CONTROL_PORT))

        self.control_sock.listen(5)

        # determines whether this client is connected to the server or not
        connected = False
        
        #while not connected, keep trying to connect to the server
        while not connected :

        # pick out the socket connection to the server that
        # we want to communicate with
            ready_to_read, ready_to_write, _ = \
                select.select(
                  [self.control_sock],
                  [],
                  [],
                  0.1)

            # when a connection with the server is made...
            if(len(ready_to_read) > 0) :

                # make sure to break the loop
                connected = True

                # start begin the interaction with the server
                self.start_server_interaction()


    # begins the process of receiving
    # a file from the server
    def start_server_interaction(self) :

        # get the connection and the address from accepting
        # the connection
        conn, addr = self.control_sock.accept()
        print("connection with ", addr)
    
        self.server_connection = conn

        # initialise the transmission and get the number of sequences that
        # will be made in return
        init_packet = self.packet_parser.translate_packet(self.initialise_transmission(conn))

        # get the session uuid
        session_uuid = init_packet[PacketKeyConstants.INIT_FILE_UUID_POS]

        # get the number of sequences to be sent from the init packet
        num_of_seqs = init_packet[PacketKeyConstants.INIT_NUM_OF_FILE_SEQUENCES_POS]

        # the checksum of the file
        checksum = init_packet[PacketKeyConstants.INIT_CHECKSUM_POS].decode()

        # get the file name from the init packet
        file_name = init_packet[PacketKeyConstants.INIT_FILENAME_POS]

        # receive the rest of the file transmission and
        # write it to the given file
        self.receive_file(session_uuid, file_name, num_of_seqs, checksum)

    # receive data from the udp connection and write it all to the file
    def receive_file(self, file_uuid, file_name, num_of_seqs, checksum) :
        
        file_data_packet_size = struct.calcsize(self.packet_constructor.general_header_format + self.packet_constructor.file_data_packet_format) + FileTransmissionConfig.FILE_DATA_PER_PACKET_AMOUNT

        transmission_complete = False

        sequence_complete = False

        current_sequence_id = 0

        current_chunk_id = -1

        missed_packets = []

        # form the filename of the file we will write to
        filename_to_write = self.get_write_file_name(file_name.decode())

        # set up the udp stream ready to receive files
        self.setup_file_data_socket()

        # set up the file that we will write to
        self.set_up_file_to_write(filename_to_write)

        # send the response to the initial message from the server
        self.send_init_response(file_uuid)

        # while we still have file data to receive
        while not transmission_complete :

            # while the end of the sequence has not yet been reached
            while not sequence_complete :

                # listen for any incoming connections
                ready_to_read, ready_to_write, _ = \
                select.select(
                    [self.server_connection, self.file_data_sock],
                    [],
                    [],
                    0.0001)

                for s in ready_to_read :

                    # receive data packet from the socket
                    raw_file_data_packet = s.recv(file_data_packet_size)

                    # parse the data packet
                    refined_file_data_packet = self.packet_parser.translate_packet(raw_file_data_packet)

                    if isinstance(refined_file_data_packet, ServerReturnCodes) :
                    
                        print("Lost connection with server")
                        sys.exit(1)
                    
                    else :

                        # determine the type of packet that was received
                        file_type = refined_file_data_packet[PacketKeyConstants.PACKET_TYPE_POS]

                        # if its a file data packet...
                        if file_type ==  MessageCodeEnum.FILE_DATA : # self.handle_file_data_packet(refined_file_data_packet, current_sequence_id, current_chunk_id)

                            receive_file_uuid = refined_file_data_packet[PacketKeyConstants.DATA_FILE_UUID_POS]
                            
                            received_file_seq_id = refined_file_data_packet[PacketKeyConstants.DATA_SEQUENCE_NUMBER_POS]

                            received_file_chunk_id = refined_file_data_packet[PacketKeyConstants.DATA_CHUNK_ID_POS]

                            # print("RECEIVED DATA : " + str(received_file_seq_id) + str(received_file_chunk_id))

                            # if the session uuid's do not match then identify this problem
                            if receive_file_uuid == file_uuid :

                                # if sequence ids don't match then highlight the problem
                                if received_file_seq_id == current_sequence_id :

                                    # print("Received chunk : " + str(received_file_chunk_id))

                                    # if chunk id's don't match then extend the missing packets list
                                    # but still write to the file
                                    if received_file_chunk_id != current_chunk_id + 1 :

                                        print("missed packets between " + str(current_chunk_id) + " and " + str(received_file_chunk_id))
                                        missed_packets.extend(self.get_missed_packets(current_chunk_id, refined_file_data_packet[PacketKeyConstants.DATA_CHUNK_ID_POS]))

                                    self.write_data_to_file(refined_file_data_packet[PacketKeyConstants.DATA_FILE_DATA_POS], received_file_seq_id, received_file_chunk_id)

                                    current_chunk_id = received_file_chunk_id

                                else :
                                    if(current_sequence_id < received_file_seq_id) :
                                        print("Missed sequence")
                                        print("Original : " + str(current_sequence_id))
                                        print("Received : " + str(received_file_seq_id))
                            
                            else : print("UUID incorrect")

                        # if its a control packet for checking to see
                        # if the client has received the whole sequence...
                        elif file_type == MessageCodeEnum.SEQ_CHECK :

                            # get the sequence that we want to check for
                            sequence_to_check = refined_file_data_packet[PacketKeyConstants.SEQ_CHECK_SEQ_ID_POS]

                            # the id of the last chunk that was sent in
                            # this sequence
                            last_chunk_id = refined_file_data_packet[PacketKeyConstants.SEQ_CHECK_LAST_CHUNK_ID_POS]

                            # if there were packets at the end that were missed,
                            # add those missed packets to the missed packets list
                            if last_chunk_id > current_chunk_id :

                                missed_packets.extend(range(current_chunk_id, last_chunk_id + 1))

                            self.send_for_missed_packets(file_uuid, current_sequence_id, missed_packets)

                            # increment the sequence id and reset the other
                            # values ready for the next sequence transmission
                            current_sequence_id += 1

                            current_chunk_id = -1

                            missed_packets = []

                        # if its a control packet that states the end of the file transmission...
                        elif file_type == MessageCodeEnum.END_OF_FILE_TRANSMISSION :

                            print("end of transmission")

                            # the checksum calculated from the received file
                            result_checksum = self.get_checksum_of_file(filename_to_write)

                            # if the result checksum and original transmitted
                            # checksum match, then the transmission was successful
                            if result_checksum == checksum :
                                success_packet = self.packet_constructor.assemble_successful_transmission_packet(file_uuid, True)
                                sent = self.server_connection.send(success_packet)
                                print("CHECKSUM SUCCESS - FILE TRANSMITTED SUCCESSFULLY")

                            else :
                                success_packet = self.packet_constructor.assemble_successful_transmission_packet(file_uuid, False)
                                sent = self.server_connection.send(success_packet)
                                print("CHECKSUM FAILED - NEED TO TRANSMIT FILE AGAIN")

                            transmission_complete = True

                        # if its anything else, handle the error
                        else :
                            print("UNEXPECTED MESSAGE TYPE")

    # handles getting the missed packets from the server
    def send_for_missed_packets(self, file_uuid, seq_id, missed_packets) :

        file_data_packet_size = struct.calcsize(self.packet_constructor.general_header_format + self.packet_constructor.file_data_packet_format) + FileTransmissionConfig.FILE_DATA_PER_PACKET_AMOUNT

        chunks_are_missing = True

        if not missed_packets :
            chunks_are_missing = False

        packet_to_send = self.packet_constructor.assemble_missing_chunks_packet(file_uuid, seq_id, chunks_are_missing, missed_packets)

        sent = self.server_connection.send(packet_to_send)

        while chunks_are_missing :

            ready_to_read, ready_to_write, _ = \
            select.select(
                [self.server_connection, self.file_data_sock],
                [],
                [],
                0.0001)

            for s in ready_to_read :

                # receive data packet from the socket
                raw_file_data_packet = s.recv(file_data_packet_size)

                # parse the data packet
                refined_file_data_packet = self.packet_parser.translate_packet(raw_file_data_packet)

                # if its a server error code
                # then output the error code
                if isinstance(refined_file_data_packet, ServerReturnCodes) :
                    return

                else :

                    # determine the type of packet that was received
                    file_type = refined_file_data_packet[PacketKeyConstants.PACKET_TYPE_POS]

                    # if its a file data packet...
                    if file_type ==  MessageCodeEnum.FILE_DATA :

                            receive_file_uuid = refined_file_data_packet[PacketKeyConstants.DATA_FILE_UUID_POS]
                            
                            received_file_seq_id = refined_file_data_packet[PacketKeyConstants.DATA_SEQUENCE_NUMBER_POS]

                            received_file_chunk_id = refined_file_data_packet[PacketKeyConstants.DATA_CHUNK_ID_POS]

                            # print("RECEIVED DATA : " + str(received_file_seq_id) + str(received_file_chunk_id))

                            # if the session uuid's do not match then identify this problem
                            if receive_file_uuid == file_uuid :

                                # if sequence ids don't match then highlight the problem
                                if received_file_seq_id == seq_id :

                                    #print("Received chunk : " + str(received_file_chunk_id))

                                    # if the packet we received is in the missed packets list
                                    # then write the packet to the file and remove it from the list
                                    # of missing packets
                                    if received_file_chunk_id in missed_packets :

                                        self.write_data_to_file(refined_file_data_packet[PacketKeyConstants.DATA_FILE_DATA_POS], received_file_seq_id, received_file_chunk_id)

                                        missed_packets.remove(received_file_chunk_id)

                                else : print("Missed segment : " + current_sequence_id)

                            else :
                                print("UUID incorrect")

                    # if its a control sequence packet
                    elif file_type == MessageCodeEnum.SEQ_CHECK :

                        # if the list of missed packets is now
                        # empty then set the exit condition to true
                        if not missed_packets :
                            chunks_are_missing = False

                        packet_to_send = self.packet_constructor.assemble_missing_chunks_packet(file_uuid, seq_id, chunks_are_missing, missed_packets)

                        sent = self.server_connection.send(packet_to_send)

        return

    # get a list of the packets that have been missed depending on the last
    # received chunk and the most recently received chunk
    def get_missed_packets(self, current_chunk_id, most_recently_received_chunk_id) :

        if current_chunk_id == most_recently_received_chunk_id + 2 :
            return [current_chunk_id + 1]

        else : return range(current_chunk_id + 1, most_recently_received_chunk_id)

    # write the data at the given position in the file according to the
    # sequence and chunk ids
    def write_data_to_file(self, data_to_write, seq_id, chunk_id) :

        offset = seq_id * FileTransmissionConfig.SEQUENCE_SIZE * FileTransmissionConfig.FILE_DATA_PER_PACKET_AMOUNT + (chunk_id * FileTransmissionConfig.FILE_DATA_PER_PACKET_AMOUNT) 

        os.lseek(int(self.file_to_write), offset , os.SEEK_SET)

        return os.write(self.file_to_write, data_to_write)

    # set up the file descriptor for writing the file to
    def set_up_file_to_write(self, filename) :

        # creates a new file
        file_to_receive = os.open(filename, os.O_WRONLY|os.O_CREAT)

        # sets this client's file to write as
        # the file that we just created
        self.file_to_write = file_to_receive

    # receive the initial packet with the server
    def initialise_transmission(self, server_sock) :

        # read this many bytes from the server
        # for the init pack
        init_pack_length = struct.calcsize(self.packet_constructor.general_header_format + self.packet_constructor.init_packet_format) + FileTransmissionConfig.MAX_FILE_NAME_LENGTH

        # read the initial data from the server
        init_data_from_server = server_sock.recv(init_pack_length)

        return init_data_from_server

    # send a response to the server that the connection is ready to transmit
    def send_init_response(self, uuid) :

        packet = self.packet_constructor.assemble_file_resp_packet(uuid)

        sent_bytes = self.server_connection.send(packet)

    # sets up the udp file data socket
    def setup_file_data_socket(self) :

        # Set up a UDP socket - flags specifies IPv4,
        # datagram socket.
        self.file_data_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.file_data_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.file_data_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        # Some systems don't support SO_REUSEPORT
        except AttributeError:
            pass

        self.file_data_sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 20)
        self.file_data_sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_LOOP, 1)

        self.file_data_sock.bind((self.MCAST_ADDRESS, self.MCAST_PORT))

        # interface provided by the local host name
        intf = socket.gethostbyname(socket.gethostname())
        self.file_data_sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(intf))
        self.file_data_sock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(self.MCAST_ADDRESS) + socket.inet_aton(intf))
        

    # Listens on the port and multicast address for data
    def receive_udp_segments(self):

        while True:
            data, addr = sock.recvfrom(1024)
            print(data)

    # get the filename of the file to write to
    def get_write_file_name(self, filename) :

        # split the path name at the last path separator
        file_partitions = filename.rsplit('/', 1)

        # split the raw filename on the first . occurence
        new_file_name_parts = file_partitions[1].split('.', 1)

        # insert the ".received." where the first dot occured in the original filename
        new_file_name = new_file_name_parts[0] + ".received." + new_file_name_parts[1]

        # put all the components together to form the complete file name
        new_file_path = file_partitions[0] + "/" + new_file_name

        return new_file_path

    # get the checksum of the file so that it can
    # be sent to the client beforehand as a check
    def get_checksum_of_file(self, filename) :
        print("Calculating checksum...")
        prev = 0
        for eachLine in open(filename,"rb"):
            prev = zlib.crc32(eachLine, prev)
        print("Checksum calculated")
        return "%X"%(prev & 0xFFFFFFFF)