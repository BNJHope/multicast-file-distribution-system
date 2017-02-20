import socket
import uuid
import select 

from FileTransferAbstract import FileTransferAbstract
from packetconstruction import PacketConstructor

class FileTransferClient(FileTransferAbstract):

    # address of the file server node
    server_node = "pc3-035-l.cs.st-andrews.ac.uk"

    # constructs packets to be sent between client and server
    packet_constructor = None

    # socket connecting this client over TCP to the server
    control_sock = None

    # socket for receiving data over the udp connection
    file_data_sock = None

    # constructor for server
    def __init__(self):

        # read in values from the config file for MCAST_ADDRESS and MCAST_PORT
        self.set_up_config_file_values()

        # set up a new instance of the packet constructor
        self.packet_constructor = PacketConstructor()

        # set up and connect to server socket
        self.control_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    # wait to receive a file from the server
    def receive_file(self) :

        # determines whether this client is connected to the server or not
        connected = False
        
        #while not connected, keep trying to connect to the server
        while not connected :

            # connect to the server control port
            try :
                self.control_sock.connect((self.server_node, self.CONTROL_PORT))
                connected = True
            except OSError as msg:
                None

        # pick out the socket connection to the server that
        # we want to communicate with
        ready_to_read, ready_to_write, _ = \
           select.select(
              [],
              [self.control_sock],
              [])

        # the server socket connection
        server_sock = ready_to_write[0]

        print("connection with ", server_sock)
        
        # initialise the transmission and get the number of sequences that
        # will be made in return
        num_of_seqs, file_descriptor = self.initialise_transmission(server_sock)

        # receive the rest of the file transmission and
        # write it to the given file
        self.receive_file(num_of_seqs, file_to_write, server_sock)


    # receive the initial packet with the server
    def initialise_transmission(self, server_sock) :

        # read this many bytes from the server
        # for the init pack
        init_pack_length = 1299

        # read the initial data from the server
        init_data_from_server = sock.recv(init_pack_length)

        return -1, ""

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
