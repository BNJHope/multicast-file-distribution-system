class FileTransferAbstract :

    #name of the file that has contains all of the configuration
    #information for the transmission
    FILE_TRANSMISSION_CONFIG_FILENAME = "file_transmission_config"

    #address used for multicast
    MCAST_ADDRESS = "229.229.229.229"

	#port used for connections on multicast
    MCAST_PORT = 45678
    
	#initialises the 
    def setUpConfigFileValues(self) :

		#open the config file to read the details in from it
    	configFile = open(self.FILE_TRANSMISSION_CONFIG_FILENAME, 'r')

    	#read and assign values from the config file
    	addressLine = configFile.readline()
    	self.MCAST_ADDRESS = addressLine

    	portLine = configFile.readline()
    	self.MCAST_PORT = int(portLine)