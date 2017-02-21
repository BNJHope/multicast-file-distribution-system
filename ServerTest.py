from FileTransferServer import FileTransferServer

def run_server():
    print("Starting server...")
    server = FileTransferServer()
    server.start_send_file("Files for replication experiments/pg44823.txt")

run_server()
