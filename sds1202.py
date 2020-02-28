


# CLASS TO CONNECT TO AND MANAGE A
# SIGLENT SDS 1202X-E OSCILLOSCOPE.

import time 									# sleep, timetracking
import socket									# network connection 					


import logging 	# an attempt to make debuggin easier 
logging.basicConfig(level=logging.DEBUG)		# enable debug messages
separator = "---------------------------------------------------"	# to separate debugging messages


class sds1202():
	
	# class internal variables ##############
	
	socket = None;								# We need to create a socket to connect to the osc. via network
	dev_ip = None;								# ip of the oscilloscope
	socket_port = None;							# port in which the sds1202 will be listening for connections
	
	
	volt_div_a = None;
	volt_div_b = None;

	sec_div = None;

	# class methods #########################
	
	def __init__(self,ip_address = None, port = None):
		pass


	def connect(self):
		sock = socket.socket()
