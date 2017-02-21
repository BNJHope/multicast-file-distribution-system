from FileTransferServer import FileTransferServer

def run_server():
    print("Starting server...")
    server = FileTransferServer()
    server.start_send_file("fileToSend")

run_server()
