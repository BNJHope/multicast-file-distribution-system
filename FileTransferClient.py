import socket
import uuid
import select 

from FileTransferAbstract import FileTransferAbstract
from packetconstruction import PacketConstructor
from packet_deconstructor import PacketDeconstructor
from file_transmission_config import FileTransmissionConfig
from protocol_codes.packet_constants import PacketKeyConstants
from protocol_codes.message_code import MessageCodeEnum

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
                self.start_server_interation()


    # begins the process of receiving
    # a file from the server
    def start_server_interation(self) :

        # get the connection and the address from accepting
        # the connection
        conn, addr = self.control_sock.accept()
        print("connection with ", addr)
    
        self.server_connection = conn

        # initialise the transmission and get the number of sequences that
        # will be made in return
        init_packet = self.packet_parser.translate_packet(self.initialise_transmission(conn))

        print(str(init_packet))

        # get the session uuid
        session_uuid = init_packet[PacketKeyConstants.INIT_FILE_UUID_POS]

        # get the number of sequences to be sent from the init packet
        num_of_seqs = init_packet[PacketKeyConstants.INIT_NUM_OF_FILE_SEQUENCES_POS]

        # get the file name from the init packet
        file_name = init_packet[PacketKeyConstants.INIT_FILENAME_POS]

        # receive the rest of the file transmission and
        # write it to the given file
        self.receive_file(session_uuid, file_name, num_of_seqs)

    # receive data from the udp connection and write it all to the file
    def receive_file(self, uuid, file_name, num_of_seqs) :
        
        file_data_packet_size = self.packet_constructor.general_header_format + self.packet_constructor.file_data_packet_format + FileTransmissionConfig.FILE_DATA_PER_PACKET_AMOUNT

        transmission_complete = False

        sequence_complete = False

        current_sequence_id = 0

        current_chunk_id = 0

        missed_packets = []

        # set up the udp stream ready to receive files
        self.setup_file_data_socket()

        self.set_up_file_to_write(file_name)

        self.send_init_response()

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

                    # determine the type of packet that was received
                    file_type = refined_file_data_packet[PacketKeyConstants.PACKET_TYPE_POS]

                    # if its a file data packet...
                    if file_type ==  MessageCodeEnum.FILE_DATA : # self.handle_file_data_packet(refined_file_data_packet, current_sequence_id, current_chunk_id)

                        receive_file_uuid = refined_file_data_packet[PacketKeyConstants.DATA_FILE_UUID_POS]
                        
                        received_file_seq_id = refined_file_data_packet[PacketKeyConstants.DATA_SEQUENCE_NUMBER_POS]

                        received_file_chunk_id = refined_file_data_packet[PacketKeyConstants.DATA_CHUNK_ID_POS]

                        # if the session uuid's do not match then identify this problem
                        if receive_file_uuid == uuid :

                            # if sequence ids don't match then highlight the problem
                            if received_file_seq_id == current_sequence_id :

                                # if chunk id's don't match then extend the missing packets list
                                # but still write to the file
                                if received_file_chunk_id != current_chunk_id  :

                                    missed_packets.extend(self.get_missed_packets(current_chunk_id, refined_file_data_packet[PacketKeyConstants.DATA_CHUNK_ID_POS]))

                                self.write_data_to_file()

                            else : print("Missed segment : " + current_sequence_id)

                        else : print("UUID incorrect")

                    # if its a control packet for checking to see
                    # if the client has received the whole sequence...
                    elif file_type == MessageCodeEnum.SEQ_CHECK :



                    # if its a control packet that states the end of the file transmission...
                    elif file_type == MessageCodeEnum.END_OF_FILE_TRANSMISSION :

                    # if its anything else, handle the error
                    else : print("UNEXPECTED MESSAGE TYPE")

    # handles getting the missed packets from the server
    def send_for_missed_packets(self, file_uuid, seq_id, missed_packets) :

        # boolean to determine if the loop can be exited or not
        can_exit = False

        while not can_exit :

                ready_to_read, ready_to_write, _ = \
                select.select(
                    [self.server_connection],
                    [],
                    [],
                    0.0001)

                for s in ready_to_read :


            # if the list of missed packets is empty
            if not missed_packets :

                can_exit = True

                seq_success_packet = self.packet_constructor.assemble_missing_chunks_packet(file_uuid, seq_id, False, [])

                self.server_connection.send(seq_success_packet)

            # if there are still packets missing
            else :

                missed_chunks_packet = self.packet_constructor.assemble_missing_chunks_packet(file_uuid, seq_id, True, missed_packets)

                self.server_connection.send(seq_success_packet)

        return

    # def handle_file_data_packet(self, refined_file_data_packet, seq_id, chunk_id) :

    # get a list of the packets that have been missed depending on the last
    # received chunk and the most recently received chunk
    def get_missed_packets(self, current_chunk_id, most_recently_received_chunk_id) :

        if current_chunk_id == most_recently_received_chunk_id + 2 :
            return [current_chunk_id + 1]

        else : return range(current_chunk_id + 1, most_recently_received_chunk_id)

    # write the data at the given position in the file according to the
    # sequence and chunk ids
    def write_data_to_file(self, data_to_write, seq_id, chunk_id) :

        offset = seq_id * FileTransmissionConfig.SEQUENCE_SIZE * FILE_DATA_PER_PACKET_AMOUNT + chunk_id 

        os.lseek(self.file_to_write, offset , os.SEEK_SET)

        return self.file_to_write.write(data_to_write)


    # set up the file descriptor for writing the file to
    def set_up_file_to_write(self, filename) :

        # creates a new file
        file_to_receive = open("received." + filename, 'a+')

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
