import socket
import uuid
import select 

from FileTransferAbstract import FileTransferAbstract
from packetconstruction import PacketConstructor
from packet_deconstructor import PacketDeconstructor
from file_transmission_config import FileTransmissionConfig

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

            # # connect to the server control port
            # try :
            #     self.control_sock.accept((self.server_node, self.CONTROL_PORT))
            #     connected = True
            # except Error as msg:
            #     None

        # pick out the socket connection to the server that
        # we want to communicate with
            ready_to_read, ready_to_write, _ = \
                select.select(
                  [self.control_sock],
                  [],
                  [],
                  0.1)

            if(len(ready_to_read) > 0) :
                connected = True
                conn, addr = self.control_sock.accept()
                print("connection with ", addr)
            
                # initialise the transmission and get the number of sequences that
                # will be made in return
                init_packet = self.packet_parser.translate_packet(self.initialise_transmission(conn))

                print(str(init_packet))

            # receive the rest of the file transmission and
            # write it to the given file
            # self.receive_file(num_of_seqs, file_to_write, server_sock)


    # receive the initial packet with the server
    def initialise_transmission(self, server_sock) :

        # read this many bytes from the server
        # for the init pack
        init_pack_length = 1299

        # read the initial data from the server
        init_data_from_server = server_sock.recv(init_pack_length)

        return init_data_from_server

    # receive data from the udp connection and write it all to the file
    def receive_file(self, file_to_write, num_of_seqs, control_sock) :
        print("receiving file")

    # Listens on the port and multicast address for data
    def receive_udp_segments(self):

        # Set up a UDP socket - flags specifies IPv4,
        # datagram socket.
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        # Some systems don't support SO_REUSEPORT
        except AttributeError:
            pass

        sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 20)
        sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_LOOP, 1)

        sock.bind((self.MCAST_ADDRESS, self.MCAST_PORT))

        # interface provided by the local host name
        intf = socket.gethostbyname(socket.gethostname())
        sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(intf))
        sock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(self.MCAST_ADDRESS) + socket.inet_aton(intf))

        print("Addr " + self.MCAST_ADDRESS)
        print("Port " + str(self.MCAST_PORT))
        print("Socket " + str(sock))

        print("Socket bound")

        while True:
            data, addr = sock.recvfrom(1024)
            print(data)
