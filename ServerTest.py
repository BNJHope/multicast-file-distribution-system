from FileTransferServer import FileTransferServer

def run_server():
    print("Starting server...")
    server = FileTransferServer()
    server.send_file("fileToSend")

run_server()
