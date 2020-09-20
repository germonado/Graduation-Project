import json
import sys
import datetime
import os

d_file = './exported_json/ble'

write_req = []
write_res = []
report_list = []
SERVICE_UUID128 = "3a:1f:25:93:d2:b6:4e:e0:af:9f:5f:c0:ad:d2:e1:55"
UUIDLIST = ["9f:50:a6:fa:d3:62:40:89:b7:78:25:7e:a0:97:37:69",
			"cc:97:79:39:dc:de:4e:6d:83:19:f2:5f:3f:96:f2:3c",
			"ed:8f:a6:8f:fa:c2:42:fc:9c:21:69:bf:d7:1b:e4:4b",
			"a4:49:64:32:4c:fd:40:9f:92:dd:a4:76:52:80:36:c4",
			"6c:b0:45:f5:b3:ec:4e:95:a5:a7:b9:10:ad:b7:c8:41"
			]

# For distinguishing command with uuid
UUIDDICT = {
			'9f:50:a6:fa:d3:62:40:89:b7:78:25:7e:a0:97:37:69':'OnOff',
			'cc:97:79:39:dc:de:4e:6d:83:19:f2:5f:3f:96:f2:3c':'Dim Level',
			'ed:8f:a6:8f:fa:c2:42:fc:9c:21:69:bf:d7:1b:e4:4b':'Color Temp',
			'a4:49:64:32:4c:fd:40:9f:92:dd:a4:76:52:80:36:c4':'Color X',
			'6c:b0:45:f5:b3:ec:4e:95:a5:a7:b9:10:ad:b7:c8:41':'Color Y'
}

# This function draws file
def get_file(dirpath):
	fileList = [s for s in os.listdir(dirpath)
		if os.path.isfile(os.path.join(dirpath, s))]
	fileList.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)), reverse=True)
	return fileList

# This function checks whether command packet succeeded or not
def write_command_succeed_check():
	reqind = resind = 0
	resend = len(write_res)
	reqend = len(write_req)
	for reqind in range(reqend):
		# chkfnum has the frame number of write request packet, for checking write response
		chkfnum = write_req[reqind]['frame']['frame.number']
		flag = 0
		for restmp in range(resind, resend):
			# if write response 
			if write_res[restmp]['btatt']['btatt.request_in_frame'] == chkfnum:
				flag =1
				write_req[reqind]['response.succeed'] = True
				send_timeinfo = write_req[reqind]['frame']['frame.time']
				send_cmd = UUIDDICT[write_req[reqind]['btatt']['btatt.handle_tree']['btatt.uuid128']]
				receive_timeinfo = write_res[restmp]['frame']['frame.time']

				print(cmd)
				#report_list.append([[write]])
				resind = restmp+1
				print(chkfnum, write_res[restmp]['btatt']['btatt.request_in_frame'])
				break
		if flag == 0:
			command_success = False

	return write_res, write_req

# This function checks if command packet is subset of valid service UUID
def write_command_uuid_check(dic):
	# Checking the valid SERVICE_UUID of command packet
	if dic['btatt.service_uuid128'] == SERVICE_UUID128:
		if UUIDDICT.get(dic['btatt.uuid128']):
			return True
		else:
			return False

# This function extracts only command packet from whole wireshark packet
def write_command_extract(filelist):
	for f in filelist:
		if os.path.splitext(d_file + '/' + f)[1] == '.json':
			json_file = open(d_file + '/' + f, encoding="utf8")
			json_read = json.load(json_file)
			for x in range(len(json_read)):
				if json_read[x]['_source']['layers'].get('btatt'):
					tmp = json_read[x]['_source']['layers']['btatt']
					# if btatt.opcode number is 12, then this packet is write request packet
					if tmp['btatt.opcode'] == '0x00000012':
						if write_command_uuid_check(tmp['btatt.handle_tree']):	
							write_req.append(json_read[x]['_source']['layers'])
					# if btatt.opcode number is 13, then this packet is write response packet
					elif tmp['btatt.opcode'] == '0x00000013':
						if write_command_uuid_check(tmp['btatt.handle_tree']):	
							write_res.append(json_read[x]['_source']['layers'])
			json_file.close()
	write_command_succeed_check()
	#print(write_res)



write_command_extract(get_file(d_file))
