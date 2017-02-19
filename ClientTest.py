from FileTransferClient import FileTransferClient

def runClient():
    print("Starting client...")
    client = FileTransferClient()
    client.listen_to_server()

runClient()
    