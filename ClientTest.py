from FileTransferClient import FileTransferClient

def runClient():
    print("Starting client...")
    client = FileTransferClient()
    client.receive_data()

runClient()
    
