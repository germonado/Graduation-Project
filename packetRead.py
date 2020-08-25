from pcapfile import savefile
import os
import datetime
import sys
import pyshark
import dpkt
import scapy.all as sc
from time import localtime, strftime
from pcapng import FileScanner

# class, CamelCase
# function, snake_case

d_file = './ble'

def get_file(dirpath):
	fileList = [s for s in os.listdir(dirpath)
		if os.path.isfile(os.path.join(dirpath, s))]
	fileList.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)), reverse=True)
	return fileList

def packet_read_scapy(filelist):
	for f in filelist:
		if os.path.splitext(d_file + '/' + f)[1] == '.pcap':
			a = sc.rdpcap(d_file + '/' + f)
			print(a[0])
			print(a.show())
		else:
			#cap = open(d_file + '/' + f, 'rb')

			cap = pyshark.FileCapture(d_file + '/' + f)
			#print("else" ,f)
			#print(cap[0])
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

def packet_read(filelist):
	for f in filelist:
		if os.path.splitext(d_file + '/' + f)[1] == '.pcap':
			print("split_success",f)
			cap = pyshark.FileCapture(d_file + '/' + f)
			print(cap[0])
			print(cap[0].layers)
		else:
			#cap = open(d_file + '/' + f, 'rb')

			cap = pyshark.FileCapture(d_file + '/' + f)
			#print("else" ,f)
			#print(cap[0])
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

packet_read_scapy(get_file(d_file))

"""
testcap = open('local.pcap', 'rb')
capfile = savefile.load_savefile(testcap, verbose=True)
print(capfile)
testcap = open('encrypted_tls_packet.pcap', 'rb')
capfile = savefile.load_savefile(testcap, verbose=True)
print(capfile)
"""