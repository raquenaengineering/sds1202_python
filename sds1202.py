


# CLASS TO CONNECT TO AND MANAGE A
# SIGLENT SDS 1202X-E OSCILLOSCOPE.

import time 									# sleep, timetracking
import socket									# network connection 					
import sys										# exit

import logging 	# an attempt to make debuggin easier 
logging.basicConfig(level=logging.DEBUG)		# enable debug messages
separator = "---------------------------------------------------"	# to separate debugging messages


class sds1202():
	
	# CONSTANTS ? ######################################################

	SOCKET_PORT = 5024													# even though currently used in config, this parameter can't be configured, so it belongs to the class

	IDN = b"Siglent Technologies,SDS1202X-E"								# ID, to confirm we're connecting to the right device.
	# IDN = "Siglent Technologies,SDS1202X-E,SDS1ECDD2R1137,1.3.26"


	# Common commands, they have no parameters.
	ID = b"*IDN?"
	COMPLETE = b"*OPC"
	RESET = b"*RST"
	# Specific oscilloscope commands, they have no parameters either
	AUTOSET = b"ASET"
	
	
	# Parameters that don't require a channel to set up
	
	TDIV = b'TDIV'
	
	DIGITAL_CHANNEL = b'DGCH'
	
	# Parameters which affect to a channel
	
	CHANNEL_A = b"C1"
	CHANNEL_B = b"C2"
	
	ATTENUATION = b'ATTENUATION'				# attenuation OF THE CONNECTED PROBE only changes the display scale
	BW_LIMIT = b'BWL'							# enables or disables low pass filter to limit the bandwidth (per channel)
	# all those are for coupling and coupling modes
	COUPLING = b'CPL'
	AC = b'A'
	DC = b'D'
	ONE_M = b'1M'								# sets input impedance to 1MOhm		# useful to model high input impedance systems??
	FIFTY_R = b'50'								# sets input impedance to 50Ohm		# useful to measure channels terminated with 50 Ohms impedances (coaxial?)
	
	OFFSET = b'OFFSET'							# set offset from 0V
	VDIV = b'VOLT_DIV'							# to set volts/division
	SKEW = b'SKEW'								# the measurement at different channels can be made non simultaneous, this means changing the skew

	TRACE = b'TRA'								# enables/disables trace for a certain channel
	UNIT = b'UNIT'								# changes units from a channel (1V, 1A 0.001V and so)

	# all related with cursor measure
	MEASURE = b'CURSOR_MEASURE'					# enables cursor measures OFF / ON / MANUAL/ TRACK
	MANUAL = b'MANUAL'							# fixed
	TRACK = b'TRACK'							# finds the relevant data?
	
	SET_CURSOR = b'CURSOR_SET'					# has too many options, implement later on
	CURSOR_TYPE = b'CURSOR_TYPE'				# too many options also, implement later on
	
	CURSOR_VAL = b'CURSOR_VALUE'				# this parameter can't be set but only get. 
	
	# DIGITAL COMMANDS ######################
	
	DIGITAL_CHANNEL = b'DIGITAL_CHANNEL'		# NOT IMPLEMENTED IN SDS1202X
	DIGITAL_STATE = b'DIGITAL_STATE'			# NOT IMPLEMENTED IN SDS1202X
	DIGITAL_THRESHOLD = b'DIGITAL_THR'			# NOT IMPLEMENTED IN SDS1202X
	
	
	DIGITAL = b'DI'								# supposedly a prefix to enable digital signaling
	SWITCH = b'SWITCH'							# switches something to on ?? what ??
	THRESHOLD_MODE = b'THRESHOLD_MODE'			# TTL, CMOS, LVCMOS33, LVCMOS25, CUSTOM
	CUSTOM = b'CUSTOM' 							# set the custom threshold (useful for LVDS or 1V8 signals)
	
	
	ON = b'ON'									# correct format for on and off commands
	OFF = b'OFF'
	
	# DISPLAY COMMANDS ######################
	
	DOT_JOIN = b'DOT_JOIN'					# joins lines between two measurement points
	DISPLAY_GRID = b'GRID_DISPLAY'			# options to display grid, FULL/HALF/OFF
	GRID_INTENSITY = b'INTENSITY'			# intensity of the grid, requires GRID/TRACE, 0 to 100. colon to separate parameters.
	MENU = b'MENU'							# turns menu on and off
	PERSIST_SETUP = b'PERSIST_SETUP'		# persistence of traces OFF/1/5/10/30/INFINITE
	
	
	# HISTORY COMMANDS ######################
	
	
	# MATH COMMANDS #########################
	
	DEFINE = b'DEFINE'							# used to define the kind of mathematical operation to be performed (FFT, +, -, *) # FORMAT IS AWFUL: osc.send_command(b"DEF EQN,'FFTC1'")
	INVERT = b'INVS'							# inverts the trace given as a paraneter, is ON OFF command (MATH also can be inverted) EX: MATH: INVS ON C1: INVS ON
	MATH_VERT_DIV = b'MATH_VERT_DIV'			# math plot vertical divisions, not useable for FFT operation
	MATH_VERT_POS = b'MATH_VERT_POS'			# position for the math plot in the vertical axis (probably also applies to fft)
	
	# fft subset from math ##################
	
	FFT_CENTER = b'FFT_CENTER'					# sets the center for the fft VERY COOL PARAMETER !!!
	FFT_FULLSCREEN = b'FFT_FULLSCREEN'			# fft takes fulls scree, requires parameter ON/OFF/EXCLU
	FFT_POSITION = b'FFT_POSITION'				# fft position (FFT_POSITION) SYNTAX NOT CLEAR, REVIEW THIS WITH DATASHEET !!!
	FFT_SCALE = b'FFT_SCALE'					# scales the fft, values depend on if its dbm or Vrms (0.1 to 20)(0.001 to 20) syntax unclear !!!
	FFT_TDIV = b'FFT_TDIV'						# ONLY QUERIES, NO WRITE !!!
	FFT_UNIT = b'FFT_UNIT'						# changes between dbm and vrms valid params: (VRMS, DBM, DBVRMS)
	FFT_VRMS = b'VRMS'
	FFT_VRMS = b'DBM'
	FFT_VRMS = b'DBVRMS'
	FFT_WINDOW = b'FFT_WINDOW'
	
	# window subset from fft ################
	
	FFT_WINDOW_RECT = b'RECT'					# useful for fast transient signals
	FFT_WINDOW_BLACKMAN = b'BLAC'				# useful for small signals, time resolution reduced
	FFT_WINDOW_HANNING = b'HANN'				# good for frequencies close together (good freq resolution)
	FFT_WINDOW_HAMMING = b'HAMM'				# ???
	FFT_WINDOW_FLATTOP = b'FLAT'				# best for accurate amplitude measurement in freq peaks
	
	
	# MEASURE COMMANDS ######################
	
	CYMOMETER = b'CYMOMETER'					# can only be queried!!! measures zero crosses, and returns the frequency counter(in E notation)
	
	MEASURE_DELAY = b'MEASURE_DELAY' 			#requires two channels to compare! to get the data requires query!!!
	# subest with possible delay modes
	PHASE_DIFFERENCE = b'PHA'
	FIRST_RISING_FIRST_RISING = b'FRR'			# maybe reduce syntax to RISING_RISING
	FIRST_RISING_FIRST_FALLING = b'FRF'
	FIRST_FALLING_FIRST_RISING = b'FFR'
	FIRST_FALLING_FIRST_FALLING = b'FFF'
	FIRST_RISING_LAST_RISING = b'LRR'
	FIRST_RISING_LAST_FALLING = b'LRF'
	FIRST_FALLING_LAST_RISING = b'LFR'
	FIRST_FALLING_LAST_FALLING = b'LFF'
	SKEW = b'SKEW'								# most relevant: two edges of the same type
	
	PARAMETER_CUSTOM = b'PACU'					# useful to measure plenty of parameters, see parameters below, value queried with PAVA?
	# subset with possible custom parameters
	PEAK_TO_PEAK = b'PKPK'
	MAX_VAL = b'MAX'
	MIN_VAL = b'MIN'
	AMPL = b'AMPL'
	TOP_VAL = b'TOP'
	BASE_VAL = b'BASE'
	CYCLE_MEAN = b'CMEAN'
	MEAN = b'MEAN'
	RMS = b'RMS'
	CRMS = b'CRMS'
	OVERSHOOT_FALLING = b'OVSN'
	PRESHOOT_FALLING = b'FPRE'
	OVERSHOOT_RISING = b'OVSP'
	PRESHOOT_RISING = b'RPRE'
	PERIOD = b'PER'								# start implementing this
	FREQUENCY = b'FREQ'							# implement this
	POSITIVE_PULSE_WIDTH = b'PWID'
	NEGATIVE_PULSE_WIDTH = b'NWID'
	RISE_TIME = b'RISE'
	FALL_TIME = b'FALL'
	BURST_WIDTH = b'WID'
	POSITIVE_DUTY = b'DUTY'
	NEGATIVE_DUTY = b'NDUTY'
	ALL = b'ALL'								# implement this
	
	

	# class methods #########################
	
	def __init__(self,ip_address = None, port = None):		# review constructor !!! if not possible to change port, no need for parameter.
		logging.debug("__init__ method was called")


		self.dev_ip = ip_address							# if ip address is defined, save it to object.
		self.sock_port = port								# same for socket port, THIS PARAMETERS ARE REQUIRED TO START A CONNECTION.

		# class internal variables ##############

		self.sock = None;  # We need to create a socket to connect to the osc. via network
		self.connected = False  # keep track if connection established

		# Variables which represent confuguration data into the osc: (copies of the internal osc variables)

		self.volt_div_a = None;  # volts per division, for each channel
		self.volt_div_b = None;  # float numbers

		self.voffs_a = None;  # offsets NOTE: offset values are relative to volts per divission !!!
		self.voffs_b = None;  # float numbers

		self.timebase = None;  # time base of our measurements, common to both channels

		self.sample_rate = None;  # sample rate, common to both channels

		self.sec_div = None;

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
		logging.debug(cmd)
		try:
			self.sock.sendall(cmd)
			time.sleep(0.5)								# FASTER THAN 0.5 GIVS PROBLEMS WITH SOME COMMANDS !!! # maybe not necessary??? check how to do this async.
		except socket.error:
			logging.error("Failed to send")
			logging.error("QUITTING")
			sys.exit()

	def receive_command(self):
		logging.debug("receive_command method was called")
		reply = self.sock.recv(4096)					# ATTENTION !!! DATA SIZE IS LIMITED HERE, THIS WON'T WORK WITH BIG WAVEWFORMS !!!
		return(reply)
	
	def receive_data(self):											# can be used only with commands which return data, like WF
		logging.debug("receive_data method was called")
		receive_command()											# receiving data is the same as command, adding processing of the data.

	def get_id(self):
		self.send_command(self.ID)
		idn = self.receive_command()
		return(idn)

	def confirm_id(self):
		idn = self.get_id()
		print("received ID")
		print(idn)
		print("expected ID")
		print(self.IDN)

		if self.IDN in idn:
			print("IDN is correct, identity confirmed")



	def measure_all(self, channel):									# gets all measurement parameters from a channel (ampl, minval, maxval, freq, and so on)
		pass
	def measure(self, channel, param):						# gets a certain parameter from a channel.
		logging.debug("measure_param method was called")
		cmd = b''							# cmd is an empty bytestring
		cmd = cmd + channel 				# first of all this requires the channel to request
		cmd = cmd + b':'					# required between channel an parameter request
		cmd = cmd + b'PAVA?'				# asks for parameter value
		cmd = cmd + b' '					# required before the parameter to request
		cmd = cmd + param					# add requested parameter
		self.send_command(cmd)				# make a request
		measure = self.receive_command()
		print(measure)
		return(measure)
		
	def enable_measure(self, channel, param):				# enables the measurement of certain parameter (it shows at the osc screen)
		cmd = b''
		cmd = cmd + self.PARAMETER_CUSTOM			# not clear about this !!!
		cmd = cmd + b' '
		cmd = cmd + param
		cmd = cmd + b','
		cmd = cmd + channel
		self.send_command(cmd)
		measure = self.receive_command()
		print(measure)
		return(measure)		
	
	
	def enable_channel(self, channel):
		logging.debug("enable_channel method was called")
		self.set_parameter(self.TRACE,self.ON,channel)
	
	def disable_channel(self, channel):
		logging.debug("disable_channel method was called")
		self.set_parameter(self.TRACE,self.OFF,channel)	


		
	def set_parameter(self,param,value = None,channel = None):			# channel is optional
		logging.debug("set_parameter method was called")
		
		# cmd should be a bytestring containing the parameter to address and the value (and maybe extra flags)
		cmd = b''
		if(channel != None):
			cmd = cmd + channel										# add channel parameter only if required for the given command
			cmd = cmd +b':'
		
		cmd = cmd + param
		
		if(value != None):
			print("This is the cmd type" + str(type(cmd)))
			if(isinstance(value,bytes) == True):		# some parameters are given as a string, not as a number, so no need to convert
				cmd = cmd + b' '
				cmd = cmd + value
			else:
				cmd = cmd + b' '
				val_str = str(value)
				val_bytes = val_str.encode()
				cmd = cmd + val_bytes
		
		logging.debug("This is the full CMD string")
		logging.debug(cmd)
		
		
		self.send_command(cmd)	

	def reset(self):
		self.send_command(self.RESET)

	def autoset(self):
		self.send_command(self.AUTOSET)


	
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
		
		return(param)
		
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
	
	
	def get_sample_rate(self):
			sample_rate = self.get_parameter(b'SARA?')
			self.sample_rate = sample_rate
			return(sample_rate)
	
	def get_timebase(self):								#keep in mind most of this process is common to most of the parameters!!! (waveforms different)		
			timebase = self.get_parameter(b'TDIV?')
			self.timebase = timebase
			return(timebase)						# maybe better to return ok and thats all



	#*NOTE: The real voltage value is calculated as follows: V = code value*(vdiv/25)-voffset
	# from this we deduct:
	# - we need the vdiv value, and there is a command to query it
	# - we need the voffset value, and there is a command to get it.			
	def get_vdiv_ch1(self):
			vdiv = self.get_parameter(b'C1:VDIV?')
			self.volt_div_a = vdiv
			return(vdiv)						# maybe better to return ok and thats all
	
	def get_vdiv_ch2(self):
			vdiv = self.get_parameter(b'C2:VDIV?')
			self.volt_div_b = vdiv
			return(vdiv)	

	def get_offset_ch1(self):
			voffs = self.get_parameter(b'C1:OFST?')
			voffs = voffs*self.volt_div_a
			self.voffs_a = voffs
			return(voffs)						# maybe better to return ok and thats all

	def get_offset_ch2(self):
			voffs = self.get_parameter(b'C2:OFST?')
			voffs = voffs*self.volt_div_b			# this is not very clear !!!
			self.voffs_b = voffs
			return(voffs)						# maybe better to return ok and thats all

		
		# THIS IS THE OLD IMPLEMENTATION keep in mind
		# IF: check could still be used to determine if receiving the rigth message
		
		# self.send_command(b'TDIV?')
		# timebase_bytes = self.receive_command()
		# logging.debug("timebase byte array:")
		# logging.debug(timebase_bytes)
		# # divide between header and data 
		# timebase_array = timebase_bytes.split(b' ')
		# logging.debug("Timebase after split")
		# logging.debug(timebase_array)
		# # here comes the check if the received message is what was expected:
		# if(timebase_array[0] == b'TTDIV'):
			# logging.debug("Response seems to be right")
			# timebase_val = timebase_array[1]
			# timebase_val = timebase_val.split(b'E')
			# logging.debug("Timebase_val after split")
			# logging.debug(timebase_val)	
			# timebase_mantissa_bytes = timebase_val[0]
			# timebase_mantissa_str = timebase_mantissa_bytes.decode()
			# logging.debug("Timebase_mantissa_str: "+ timebase_mantissa_str)
			# timebase_mantissa = float(timebase_mantissa_str)
			# logging.debug("Timebase_mantissa: ")
			# logging.debug(timebase_mantissa)
			# timebase_exp_bytes = timebase_val[1]			
			# timebase_exp_bytes = timebase_exp_bytes[0:3]	# exponent has fix size, on this way we get rid of everything else			
			# logging.debug(timebase_exp_bytes)
			# timebase_exp_str = timebase_exp_bytes.decode()
			# logging.debug("Timebase_exp_str: "+ timebase_exp_str)			
			# timebase_exp = int(timebase_exp_str)
			# logging.debug("Timebase_exp:")
			# logging.debug(timebase_exp)
			
			# timebase = timebase_mantissa*10**timebase_exp
			
			# # THIS WAY DOESN'T SEEM TO WORK, BUT WOULD BE CONVENIENT, IT REQUIRES LESS OPERATIONS #
			
			# timebase_val = timebase_array[1]
			# timebase_val = timebase_val[0:8]				# only 7 significant numbers, 3 for mantissa,1 separator, 3 for exp
			# timebase_val = timebase_val.decode()
			# #timebase_val.replace('E','e')
			# timebase_val = float(timebase_val)
			
			# logging.debug("TIMEBASE_VAL")
			# logging.debug(timebase_val)
	
				
			
			
			
			
			#logging.debug("Timebase_mantissa_str: "+ timebase_exp_bytes)
			#timebase_mantissa = float(timebase_mantissa_str)			
		
	def get_osc_current_config(self):							# queries all current configuration parameters of the oscilloscope	
																# and stores them into the mirror values at the python object, for its use.	
		self.get_timebase()
		self.get_sample_rate()
		self.get_vdiv_ch1()
		self.get_offset_ch1()
		self.get_vdiv_ch2()
		self.get_offset_ch1()
		self.get_offset_ch2()
		
		
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
		print(self.volt_div_b)
		print("Voffset. Channel A: ")
		print(self.voffs_a)
		print("Voffset. Channel B: ")
		print(self.voffs_b)

		print("Time Base: ")
		print(self.timebase)
		print("Sample Rate: ")
		print(self.sample_rate)



if __name__ == "__main__":

	osc = sds1202(ip_address = "192.168.0.201", port = 5024)
	osc.connect()
	osc.confirm_id()
	osc.get_osc_current_config()
	osc.print_osc_config_params()

