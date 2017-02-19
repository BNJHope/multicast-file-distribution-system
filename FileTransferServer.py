import socket
import select
import uuid

from FileTransferAbstract import FileTransferAbstract
from packetconstruction import PacketConstructor

class FileTransferServer(FileTransferAbstract):

    target_nodes = ["pc3-034-l.cs.st-andrews.ac.uk"]

    server_address = socket.gethostname()

    # constructs packets to be sent between client and server
    packet_constructor = None

    # socket connecting this client over TCP to the server
    server_sock = None

    # constructor for server
    def __init__(self):

        # read in values from the config file for MCAST_ADDRESS and MCAST_PORT
        self.set_up_config_file_values()

        self.packet_constructor = PacketConstructor()

        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #=========
    #TEST SECTION
    #===========

    def send_file(self, filename) :

        # file id to pass for this file session
        file_id = str(uuid.uuid1())

        # send the init packet
        self.send_init(filename, file_id)

        
    # send a file to all available clients
    def send_init(self, filename, file_uuid) :

        self.server_sock.bind((self.server_address, self.CONTROL_PORT))

        self.server_sock.listen(5)

        while(True) :

            ready_to_read, ready_to_write, _ = \
                   select.select(
                      [self.server_sock],
                      [],
                      [])

            print(len(ready_to_read))
            if len(ready_to_read) > 0 :
                s = ready_to_read[0]
                s.accept()
                while True :
                    packet = self.packet_constructor.assemble_file_init_packet(filename, file_uuid)
                    sent = s.send(packet.encode())
                    chunk = s.recv(100)
                    print("trying to exit")

        return

    #=========
    #TEST SECTION CLOSE
    #===========
        
    # # starts the server
    # def start_server() :

    #     # create an INET, STREAMing socket
    #     serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     # bind the socket to a public host, and a well-known port
    #     serversocket.bind((self., ))
    #     # become a server socket
    #     serversocket.listen(5)

    #handles a given message from a client
    # def handle_message(message) :


    # broadcast a file over the MCAST port and address to any listeners
    def send_udp_segments(self):

        # define the socket as a IPv4 datagram socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # set extra multicast options
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 20)

        print("Addr " + self.MCAST_ADDRESS)
        print("Port " + str(self.MCAST_PORT))
        print("Socket " + str(sock))

        print("Sending data")
        
        # send the numbers 0-99 to any listeners
        while True:
            sock.sendto(str.encode("ping from file transfer server"), (self.MCAST_ADDRESS, self.MCAST_PORT))
