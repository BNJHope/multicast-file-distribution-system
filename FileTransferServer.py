import socket

class FileTransferServer :
    
    #address used for multicast
    MCAST_ADDRESS = "229.229.229.229"

	#port used for connections on multicast
    MCAST_PORT = 45678

    #broadcast a file over the MCAST port and address to any listeners
    def sendFile(self) :

    	#define the socket as a IPv4 datagram socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        #set extra multicast options
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 20)

        #send the numbers 0-99 to any listeners
        for x in range(0, 100) :
            print("Sending " + str(x))
            sock.sendto(str.encode(str(x)), (self.MCAST_ADDRESS, self.MCAST_PORT))
