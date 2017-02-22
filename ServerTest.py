from FileTransferServer import FileTransferServer

def run_server():
    print("Starting server...")
    server = FileTransferServer()
    server.start_send_file("Files for replication experiments/TheFastandtheFuriousJohnIreland1954goofyrip_512kb.mp4")

run_server()
