import socket

class FileTransferClient :

    #address used for multicast
    MCAST_ADDRESS = "229.229.229.229"
    
    #port used for connections on multicast
    MCAST_PORT = 45678

    #Listens on the port and multicast address for data
    def receiveData(self) :

        #Set up a UDP socket - flags specifies IPv4, datagram socket and UDP protocol in use.
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        
        
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except AttributeError:
            pass # Some systems don't support SO_REUSEPORT

        sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 20)
        sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_LOOP, 1)
        
        sock.bind((self.MCAST_ADDRESS, self.MCAST_PORT))
        
        #interface provided by the local host name
        intf = socket.gethostbyname(socket.gethostname())
        sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(intf))
        sock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(self.MCAST_ADDRESS) + socket.inet_aton(intf))

        
        print("Socket bound")
        
        while True:
            data, addr = sock.recvfrom(1024)
            print(data)

