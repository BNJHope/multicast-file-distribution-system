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

    # constructor for server
    def __init__(self):

        # read in values from the config file for MCAST_ADDRESS and MCAST_PORT
        self.set_up_config_file_values()

        # set up a new instance of the packet constructor
        self.packet_constructor = PacketConstructor()

        # set up and connect to server socket
        self.control_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #=========
    #TEST SECTION
    #===========

    # start the server loop
    def listen_to_server(self) :

        connected = False
        
        #while not connected
        while not connected :

            # connect to the server control port
            try :
                self.control_sock.connect((self.server_node, self.CONTROL_PORT))
                connected = True
            except OSError as msg:
                None

        if not (self.control_sock is None) :
            ready_to_read, ready_to_write, _ = \
               select.select(
                  [],
                  [self.control_sock],
                  [])
            if(ready_to_write != None) :
                print(ready_to_write)

            with self.control_sock :
                print("connection with ", self.control_sock)
                
                while True :
                    data = self.control_sock.recv(1024)
                    if data :
                        print(repr(data))
                        break;

    #=========
    #TEST SECTION CLOSE
    #===========

    # send a given file
    def send_file(self, filename):

        file_uuid = uuid.uuid1()

        self.send_initial_file_message(filename, file_uuid)
        

    # send the initial intro message for file transmission to all clients
    def send_initial_file_message(self, filename, file_uuid):

        # the initial packet to send
        initPacket = self.packet_constructor.assemble_file_init_packet(self, filename, file_uuid)


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
