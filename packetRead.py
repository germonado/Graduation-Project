from pcapfile import savefile
import os
import datetime
import sys
import pyshark
import dpkt
from time import localtime, strftime
from pcapng import FileScanner

# class, CamelCase
# function, snake_case

d_file = './packets'

def get_file(dirpath):
	fileList = [s for s in os.listdir(dirpath)
		if os.path.isfile(os.path.join(dirpath, s))]
	fileList.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)), reverse=True)
	return fileList

def packet_read(filelist):
	for f in filelist:
		if os.path.splitext(d_file + '/' + f)[1] == '.pcap':
			cap = pyshark.FileCapture(d_file + '/' + f)
			#print(cap[0])
		else:
			#cap = open(d_file + '/' + f, 'rb')

			cap = pyshark.FileCapture(d_file + '/' + f)
			print(cap[0])
			"""
			packet = dpkt.pcapng.Reader(cap)
			pcapng = packet.readpkts()
			print(pcapng)
			"""
	"""
	for f in filelist:
		tmp = pyshark.FileCapture(d_file + '/' + f)
		print(tmp[0])
	"""

packet_read(get_file(d_file))

"""
testcap = open('local.pcap', 'rb')
capfile = savefile.load_savefile(testcap, verbose=True)
print(capfile)
testcap = open('encrypted_tls_packet.pcap', 'rb')
capfile = savefile.load_savefile(testcap, verbose=True)
print(capfile)
"""