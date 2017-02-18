import socket
import uuid

from FileTransferAbstract import FileTransferAbstract
from packetconstruction import PacketConstructor

class FileTransferClient(FileTransferAbstract):

    target_nodes = ["pc3-033-l.cs.st-andrews.ac.uk"]

    packet_constructor = None

    # constructor for server
    def __init__(self):

        # read in values from the config file for MCAST_ADDRESS and MCAST_PORT
        self.set_up_config_file_values()

        # set up a new instance of the packet constructor
        self.packet_constructor = PacketConstructor()

    # send a given file
    def send_file(self, filename):

        file_uuid = uuid.uuid1()

        self.send_initial_file_message(filename, file_uuid)

        

    # send the initial intro message for file transmission to all clients
    def send_initial_file_message(self, filename, file_uuid):

        self.packet_constructor.assemble_file_init_packet(self, filename, file_uuid)

    # Listens on the port and multicast address for data
    def receive_data(self):

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
