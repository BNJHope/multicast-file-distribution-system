import sys

from FileTransferServer import FileTransferServer

FILE_NAME_ARG_POS = 1

NUMBER_OF_CLIENTS_ARG_POS = 2

def run_server():
	print("Starting server...")
	server = FileTransferServer()
	if(len(sys.argv) == 3) :
		server.start_send_file(sys.argv[FILE_NAME_ARG_POS], int(sys.argv[NUMBER_OF_CLIENTS_ARG_POS]))
	else :
		server.start_send_file(sys.argv[FILE_NAME_ARG_POS])

run_server()
