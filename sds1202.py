


# CLASS TO CONNECT TO AND MANAGE A
# SIGLENT SDS 1202X-E OSCILLOSCOPE.

import time 									# sleep, timetracking
import socket									# network connection 					


import logging 	# an attempt to make debuggin easier 
logging.basicConfig(level=logging.DEBUG)		# enable debug messages
separator = "---------------------------------------------------"	# to separate debugging messages


class sds1202():
	
	# class internal variables ##############
	
	sock = None;								# We need to create a socket to connect to the osc. via network
	dev_ip = None;								# ip of the oscilloscope
	sock_port = None;							# port in which the sds1202 will be listening for connections
	connected = False							# keep track if connection established
		
	
	
	volt_div_a = None;
	volt_div_b = None;

	sec_div = None;

	# class methods #########################
	
	def __init__(self,ip_address = None, port = None):
		logging.debug("__init__ method was called")
		
		self.dev_ip = ip_address							# if ip address is defined, save it to object.
		self.sock_port = port								# same for socket port, THIS PARAMETERS ARE REQUIRED TO START A CONNECTION.
		
		# creating the socket 
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)			# what does this mean??
		except socket.error:
			logging.warning("failed to create socket")
			sys.exit();
		logging.debug("socket created")


	def connect(self):
		logging.debug("connect method was called")
			
		# connecting to remote:
		try:
			self.sock.connect((self.dev_ip,self.sock_port))		# attention !!! socket takes a TUPLE as input parameter
			self.connected = True						# enable connected flag, used to keep track of connection 
		except socket.error:
			logging.warning("Failed to connect to ip " + remote_ip)
		logging.debug("socket connected")
		return self.connected

	def send_command(self,cmd):
		logging.debug("send_command method was called")
		try:
			self.sock.sendall(cmd)
			time.sleep(1)								# maybe not necessary??? check how to do this async.
		except socket.error:
			logging.error("Failed to send")
			logging.error("QUITTING")
			sys.exit()		

	def receive_command(self):
		logging.debug("receive_command method was called")
		reply = self.sock.recv(4096*128)
		return(reply)
	
	
		
	# def get_data(self,cmd):
		# logging.debug("get_data method was called")
		# # send string
		# try:
			# self.sock.sendall(cmd)
			# time.sleep(1)
		# except socket.error:
			# logging.error("Failed to send")
			# sys.exit()
		# reply = self.sock.recv(4096)
		# return(reply)	
		
		
		
			
