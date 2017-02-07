from FileTransferClient import FileTransferClient

def runClient():
    print("Starting client...")
    client = FileTransferClient()
    client.receiveData()

runClient()
    
