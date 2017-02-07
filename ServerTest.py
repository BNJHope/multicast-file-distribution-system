from FileTransferServer import FileTransferServer

def runServer():
    print("Starting server...")
    server = FileTransferServer()
    server.sendFile()

runServer()
