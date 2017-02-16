import socket

from FileTransferAbstract import FileTransferAbstract

class FileTransferServer(FileTransferAbstract):

    # socket for listening to requests
    listen_socket = None

    # constructor for server
    def __init__(self):

        # read in values from the config file for MCAST_ADDRESS and MCAST_PORT
        self.set_up_config_file_values()

    # initialise the server and loop
    def run(self):

        # set up the server multicast socket to listen for requests
        self.set_up_listen_socket()

    # runs a listener for requests
    def server_loop(self):
        print("loop")

    #handles when a tcp connection is made
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

    #handles messages received from client
    def data_received(self, data):
        message = data.decode()
        print('Data received: {!r}'.format(message))

        print('Send: {!r}'.format(message))
        self.transport.write(data)

        print('Close the client socket')
        self.transport.close()
        
    #handles a given message from a client
    def handle_message(message) :


    # broadcast a file over the MCAST port and address to any listeners
    def send_file(self):

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


    # setup a listening socket
    def set_up_listen_socket(self):

        # Set up a UDP socket - flags specifies IPv4,
        # datagram socket and UDP protocol in use.
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        # Some systems don't support SO_REUSEPORT
        except AttributeError:
            pass

        self.listen_socket.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 20)
        self.listen_socket.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_LOOP, 1)

        self.listen_socket.bind((self.MCAST_ADDRESS, self.MCAST_PORT))

        # interface provided by the local host name
        intf = socket.gethostbyname(socket.gethostname())
        self.listen_socket.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(intf))
        self.listen_socket.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(self.MCAST_ADDRESS) + socket.inet_aton(intf))
