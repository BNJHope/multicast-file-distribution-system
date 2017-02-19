from file_transmission_config import FileTransmissionConfig

class FileTransferAbstract() :

    #address used for multicast
    MCAST_ADDRESS = ""

	#port used for connections on multicast
    MCAST_PORT = 0
    
    # port over which TCP control messages will be sent between client and server
    CONTROL_PORT = 0

	#initialises the 
    def set_up_config_file_values(self) :

        #get common config values from the config class
        self.MCAST_ADDRESS = FileTransmissionConfig.MCAST_ADDRESS

        self.MCAST_PORT = FileTransmissionConfig.MCAST_PORT

        self.CONTROL_PORT = FileTransmissionConfig.CONTROL_PORT