


# CLASS TO CONNECT TO AND MANAGE A
# SIGLENT SDS 1202X-E OSCILLOSCOPE.

import time 									# sleep, timetracking
import socket									# network connection 					
import sys										# exit

import logging 	# an attempt to make debuggin easier 
logging.basicConfig(level=logging.DEBUG)		# enable debug messages
separator = "---------------------------------------------------"	# to separate debugging messages


class sds1202():
	
	# CONSTANTS ? ###########################
	
	CHANNEL_A = "C1"
	CHANNEL_B = "C2"
	
	
	# class internal variables ##############
	
	sock = None;								# We need to create a socket to connect to the osc. via network
	dev_ip = None;								# ip of the oscilloscope
	sock_port = None;							# port in which the sds1202 will be listening for connections
	connected = False							# keep track if connection established
		
	
	# Variables which represent confuguration data into the osc: (copies of the internal osc variables)
	
	volt_div_a = None;							# volts per division, for each channel
	volt_div_b = None;							# float numbers
	
	voffs_a = None;								# offsets 
	voffs_b = None;								# float numbers
	
	timebase = None;							# time base of our measurements, common to both channels
	
	sample_rate = None;							# sample rate, common to both channels
	
	
	

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
			logging.warning("Failed to connect to ip " + self.dev_ip)
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
		reply = self.sock.recv(4096)					# ATTENTION !!! DATA SIZE IS LIMITED HERE, THIS WON'T WORK WITH BIG WAVEWFORMS !!!
		return(reply)
	
	def receive_data(self):								# can be used only with commands which return data, like WF
		logging.debug("receive_data method was called")
		receive_command()								# receiving data is the same as command, adding processing of the data.
		
		
		
		#*NOTE: The real voltage value is calculated as follows: V = code value*(vdiv/25)-voffset
		# from this we deduct:
		# - we need the vdiv value, and there is a command to query it
		# - we need the voffset value, and there is a command to get it.
	
	def get_parameter(self,param):						# generic get parameter stuff, dealing with processing part of the data, can be used for timebase, sara
		logging.debug("get_parameter method was called")
		
		self.send_command(param)
		param_bytes = self.receive_command()
		logging.debug("param byte array:")
		logging.debug(param_bytes)
		# divide between header and data 
		param_array = param_bytes.split(b' ')		# space seems to be the separator between header and actual data value
		param_header = param_array[0]
		param_bytes = param_array[1]
		logging.debug(param_bytes)
		param_bytes = param_bytes[0:8]				# only 7 significant numbers, 3 for mantissa,1 separator, 3 for exp
		
		param = float(param_bytes)
		
		logging.debug("PARAM")
		logging.debug(param)
		
		# param_val = param_bytes.split(b'E')
		# param_mantissa = param_val[0]
		# param_mantissa = param_mantissa.decode()
		# param_mantissa = float(param_mantissa)
		# param_exp = param_val[1]
		# logging.debug(param_exp)
		# param_exp = param_exp.decode()
		# param_exp = int(param_exp)

		# logging.debug("Param Mantissa:")
		# logging.debug(param_mantissa)
		# logging.debug("param_exp")
		# logging.debug(param_exp)

		# param = param_mantissa*10**param_exp
	
	def get_timebase(self):								#keep in mind most of this process is common to most of the parameters!!! (waveforms different)
		self.send_command(b'TDIV?')
		timebase_bytes = self.receive_command()
		logging.debug("timebase byte array:")
		logging.debug(timebase_bytes)
		# divide between header and data 
		timebase_array = timebase_bytes.split(b' ')
		logging.debug("Timebase after split")
		logging.debug(timebase_array)
		# here comes the check if the received message is what was expected:
		if(timebase_array[0] == b'TTDIV'):
			logging.debug("Response seems to be right")
			timebase_val = timebase_array[1]
			timebase_val = timebase_val.split(b'E')
			logging.debug("Timebase_val after split")
			logging.debug(timebase_val)	
			timebase_mantissa_bytes = timebase_val[0]
			timebase_mantissa_str = timebase_mantissa_bytes.decode()
			logging.debug("Timebase_mantissa_str: "+ timebase_mantissa_str)
			timebase_mantissa = float(timebase_mantissa_str)
			logging.debug("Timebase_mantissa: ")
			logging.debug(timebase_mantissa)
			timebase_exp_bytes = timebase_val[1]			
			timebase_exp_bytes = timebase_exp_bytes[0:3]	# exponent has fix size, on this way we get rid of everything else			
			logging.debug(timebase_exp_bytes)
			timebase_exp_str = timebase_exp_bytes.decode()
			logging.debug("Timebase_exp_str: "+ timebase_exp_str)			
			timebase_exp = int(timebase_exp_str)
			logging.debug("Timebase_exp:")
			logging.debug(timebase_exp)
			
			timebase = timebase_mantissa*10**timebase_exp
			
			# THIS WAY DOESN'T SEEM TO WORK, BUT WOULD BE CONVENIENT, IT REQUIRES LESS OPERATIONS #
			
			timebase_val = timebase_array[1]
			timebase_val = timebase_val[0:8]				# only 7 significant numbers, 3 for mantissa,1 separator, 3 for exp
			timebase_val = timebase_val.decode()
			#timebase_val.replace('E','e')
			timebase_val = float(timebase_val)
			
			logging.debug("TIMEBASE_VAL")
			logging.debug(timebase_val)
			
				
			self.timebase = timebase	
				
			return timebase
			
			
			
			#logging.debug("Timebase_mantissa_str: "+ timebase_exp_bytes)
			#timebase_mantissa = float(timebase_mantissa_str)			
		
	def get_osc_current_config(self):							# queries all current configuration parameters of the oscilloscope	
														# and stores them into the mirror values at the python object, for its use.
		pass
		# get_timebase			# TDIV?
		# get_sampling_rate		# SARA?
		# get_voltsdiv_a		# C1:VDIV?
		# get_voltsdiv_b
		# get_voffset_a			# C1:OFST?
		# get_voffset_b
		
		
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
		
	def print_osc_config_params(self):		# maybe add flags to get only cannel a or b instead?, create functions for only a channel ???
		logging.debug("print_osc_config_params method was called")
		
		print("LATEST QUERIED OSCILLOSCOPE CONFIGURATION:")				# important to note, this prints the local values, if you want current, QUERY THEM FIRST !!!
		
		print("Volts/Div Channel A: ")
		print(self.volt_div_a)
		print("Volts/Div Channel B: ")
		print(self.volt_div_a)
		print("Voffset. Channel A: ")
		print(self.voffs_a)
		print("Voffset. Channel B: ")
		print(self.voffs_b)

		print("Time Base: ")
		print(self.timebase)
		print("Sample Rate: ")
		print(self.sample_rate)
