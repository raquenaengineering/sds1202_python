


from sds1202 import *


# GLOBAL VARIABLES #####################################################

remote_ip = "192.168.42.190"
sock_port = 5024

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


# MAIN FUNCTION ########################################################

if __name__ == "__main__":
	
	#user_manual_test()
	
	osc = sds1202(remote_ip, sock_port)			# try to implement a network search to find the oscilloscope (FUTURE GOALS, NOT NOW)
	osc.connect()
	osc.send_command(b'*IDN?')
	desc = osc.receive_command()
	print(desc)
	
	osc.send_command(b'BUZZ OFF')				# disables beeping, no response is expected
	
	osc.send_command(b'C1:WF? DAT2')			# gets data from channel 1 waveform ?? don't understand
	waveform_bytes = osc.receive_command()
	print(waveform_bytes)
		
	# create a file and store waveform data
	print("Trying to save onto a file")
	waveform = waveform_bytes.decode()
	wave_file = open("wave.txt",'w')
	wave_file.write(waveform)
	wave_file.close()




