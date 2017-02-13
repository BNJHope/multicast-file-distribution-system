import threading
import time

class FileTransferServerThread(Thread) :

	# ip address of the client
	client_ip = ""

	# port with which interactions are being made with the client
	client_port = 0

	#name of the file which this server 
	filename = ""

	def __init__(self, client_ip, client_port, filename):
		threading.Thread.__init__(self)
		self.client_ip = client_ip
		self.client_port = client_port
		self.filename = filename

	def run(self):
	      self.transferFile()

  	def transferFile(self) :
  		self.sendMetaBlock()
  		self.sendFileContents()

	def sendMetaBlock(self) :
		print("sending meta")

	def sendFileContents(self) :
		print("sending file")