


from sds1202 import *

import config

# GLOBAL VARIABLES #####################################################

remote_ip = config.OSC_IP
port = config.OSC_PORT

# required by user_manual_test

def socket_connect():
	# creating the socket 
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)			# what does this mean??
	except socket.error:
		print("failed to create socket")
		sys.exit();
	print("socket created")
	# connecting to remote:
	try:
		s.connect((remote_ip,port))		# attention !!! socket takes a TUPLE as input parameter
	except socket.error:
		print("Failed to connect to ip " + remote_ip)
	print("socket connected")
	return s
	
def socket_query(sock,cmd):
	# send string
	try:
		sock.sendall(cmd)
		time.sleep(1)
	except socket.error:
		print("Failed to send")
		sys.exit()
	reply = sock.recv(4096)
	return(reply)
	
# this function implements the test included at the programming documentation
# from the user manual
# requires the two previous functions

def user_manual_test():
	
	import socket		# socket communication
	import sys			# exit
	import time			# sleep

	count = 0
	
	print("socket_connect function called")
	s = socket_connect()						# returns the connected socket
	print("query string function called")
	query_string = socket_query(s,b'*IDN?')		# returns queried string from oscilloscope
	
	s.sendall(b'STOP')
	
	print(query_string)



def test_get_save_wave():							# gets a wave from osc, processes it to the right format, and saves it to file
	
	# get information about the current 
	
	
	# osc.get_timebase()
	# osc.get_sample_rate()
	# osc.get_vdiv_ch1()
	# osc.get_offset_ch1()
	# osc.get_vdiv_ch2()
	# osc.get_offset_ch1()
	# osc.get_offset_ch2()
	# osc.get_parameter(b'TDIV?')
	

	osc.get_osc_current_config()

	osc.print_osc_config_params()
	
	
	osc.send_command(b'C1:WF? DAT2')			# gets data from channel 1 waveform ?? don't understand
	waveform_bytes = osc.receive_command()
	print(waveform_bytes)
	#
	# create a file and store waveform data
	print("Trying to save onto a file")
	waveform = waveform_bytes.decode()
	wave_file = open("wave.txt",'w')
	wave_file.write(waveform)
	wave_file.close()

def test_set_params():
	# TO USE SET_PARAMETER, IS NECESSARY TO DEFINE THE PARAMETER STRINGS
	#osc.reset()
	time.sleep(1)
	osc.set_parameter(osc.VDIV,0.001,osc.CHANNEL_A)
	osc.set_parameter(osc.VDIV,0.001,osc.CHANNEL_B)
	
	osc.enable_channel(osc.CHANNEL_B)
	osc.enable_channel(osc.CHANNEL_A)

	#time.sleep(1)
	osc.autoset()
	
	#osc.set_parameter(osc.VDIV,0.001,osc.CHANNEL_A);


def test_enable_collect_measures():
	
	# a maximum of 5 measures is allowed, if more, probably the old are replaced ???!!!
	
	osc.enable_measure(osc.CHANNEL_A, osc.PEAK_TO_PEAK)			# works
	osc.enable_measure(osc.CHANNEL_B, osc.PEAK_TO_PEAK)			# works 
	
	osc.enable_measure(osc.CHANNEL_A, osc.FREQUENCY)			# works
	osc.enable_measure(osc.CHANNEL_B, osc.FREQUENCY)			# works
	
	osc.enable_measure(osc.CHANNEL_A, osc.ALL)			# works
	
	peakval = osc.measure(osc.CHANNEL_B, osc.PEAK_TO_PEAK)		# !!! returns /0 as a first character, reading wrong ???
	print(peakval)
	peakval = osc.measure(osc.CHANNEL_B, osc.PEAK_TO_PEAK)		# !!! returns /0 as a first character, reading wrong ???
	print(peakval)
	
	freq = osc.measure(osc.CHANNEL_A, osc.FREQUENCY)		# answer starts with 'CC1', strange???
	freq = osc.measure(osc.CHANNEL_B, osc.FREQUENCY)		# same with 'CC2'

	osc.enable_measure(osc.CHANNEL_B, osc.ALL)			# works
	time.sleep(3)
	allparams = osc.measure(osc.CHANNEL_B, osc.ALL)		# strange extra random character at the beginning of the request.
	
	osc.enable_measure(osc.CHANNEL_A, osc.ALL)		# works, required before measuring all channels
	time.sleep(3)
	allparams = osc.measure(osc.CHANNEL_A, osc.ALL)		# works




	
# MAIN FUNCTION ########################################################

if __name__ == "__main__":
	
	#user_manual_test()
	
	osc = sds1202(remote_ip, port)			# try to implement a network search to find the oscilloscope (FUTURE GOALS, NOT NOW)
	osc.connect()
	osc.send_command(b'*IDN?')					# asks for device description
	desc = osc.receive_command()
	print(desc)
	
	osc.measure(osc.CHANNEL_A,osc.CUSTOM)
	
	# osc.send_command(b'GRDS HALF')
	# osc.send_command(b'INTS TRACE,100')
	# osc.send_command(b"DEF EQN,'FFTC1'")	
	# osc.send_command(b'MTVP 100')			# 
	# osc.send_command(b'FFTC 500')			#
	# osc.send_command(b'FFTF ON')			#
	# osc.send_command(b'FFT_UNIT VRMS')		# sets fft to measure in vrms USEFUL !!!
	# #osc.send_command(b'FFT_UNIT DBM')		# sets fft to measure in dbm
	# #osc.send_command(b'FFT_UNIT DBVRMS')	# sets fft to measure in dbvrms
	
	# osc.send_command(b'MEAD SKEW,C1-C2')	# measures skew between channels 1 and 2
	# #osc.send_command(b'C1-C2:MEAD? SKEW')	# ERROR!!! BUG!!! THIS COMMAND MAKES OSCILLOSCOPE UNRSEPONSIVE!!!
	
	test_enable_collect_measures()			# for methods and variables to do with measures
	
	

	
	
	#osc.send_command(b'PACU ALL,C2')
	#osc.send_command(b'PACU ALL,C1')
	
	#print(osc.get_parameter(b'C2:PAVA? RISE'))

	
	
	#print(osc.get_parameter(b'FFT_POSITION?'))

	# osc.send_command(b'DI:SWITCH OFF')
	# time.sleep(1)
	# osc.send_command(b'DI:SWITCH ON')
	# time.sleep(1)
	# osc.send_command(b'DI:SWITCH OFF')
	# time.sleep(1)
	# osc.send_command(b'DI:SWITCH ON')
	
	# osc.send_command(b'D2:TRACE ON')

	# osc.set_parameter(osc.SWITCH, osc.ON);
	# time.sleep(1)
	# osc.set_parameter(osc.SWITCH, osc.OFF);
	# time.sleep(1)
	# osc.set_parameter(osc.SWITCH, osc.ON);
	# time.sleep(1)
	# osc.set_parameter(osc.SWITCH, osc.OFF);
	# time.sleep(1)
	# osc.set_parameter(osc.SWITCH, osc.ON);
	# time.sleep(1)
	# osc.set_parameter(osc.SWITCH, osc.OFF);
	# time.sleep(1)
	#test_set_params()

	#test_get_save_wave()







	# osc.send_command(b'*OPC?')					# are all operations complete ?? (useful to block until done with config, or sending signal)
	# desc = osc.receive_command()
	# print(desc)

	# osc.send_command(b'*RST')					# resetting the osc
	
	# osc.send_command(b'BUZZ OFF')				# disables beeping, no response is expected
	
	# osc.send_command(b'CHDR?')					# disables beeping, no response is expected
	# desc = osc.receive_command()
	# print(desc)
	
	# osc.send_command(b'C1:VDIV 1.00E-04')				# disables beeping, no response is expected
	
	# # for i in range(1,10):
		# # osc.send_command(b'ARM')
		# # time.sleep(0.5)
		# # osc.send_command(b'STOP')
		# # time.sleep(0.5)
	

	
	
	# osc.send_command(b'WFSU?')					# ask for current waveform setup
	# waveform_setup = osc.receive_command()
	# print(waveform_setup)

	# osc.send_command(b'WFSU SP,32,NP,1024,FP,0')	
	
	# osc.send_command(b'WFSU?')					# ask for current waveform setup
	# waveform_setup = osc.receive_command()
	# print(waveform_setup)
	
	# osc.send_command(b'FFTT?')					# ask for current waveform setup
	# fft_opt = osc.receive_command()
	# print(fft_opt)
	
	# osc.send_command(b'FFTT 5.00E4')			# try to set thee FFT to acertain frequency range

	# osc.send_command(b'FFTT?')					# ask for current waveform setup
	# fft_opt = osc.receive_command()
	# print(fft_opt)

	
	
	
	
	
	
	



