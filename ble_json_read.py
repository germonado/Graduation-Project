import json
import sys
import datetime
import os

d_file = './exported_json/ble'
# list append performance 질문하기
# 크기를 정해놓고 담는 것이 나은지 아니면 append로도 충분한지
write_req = []
write_res = []
SERVICE_UUID128 = "3a:1f:25:93:d2:b6:4e:e0:af:9f:5f:c0:ad:d2:e1:55"
UUIDLIST = ["9f:50:a6:fa:d3:62:40:89:b7:78:25:7e:a0:97:37:69",
			"cc:97:79:39:dc:de:4e:6d:83:19:f2:5f:3f:96:f2:3c",
			"ed:8f:a6:8f:fa:c2:42:fc:9c:21:69:bf:d7:1b:e4:4b",
			"a4:49:64:32:4c:fd:40:9f:92:dd:a4:76:52:80:36:c4",
			"6c:b0:45:f5:b3:ec:4e:95:a5:a7:b9:10:ad:b7:c8:41"
			]
			
def get_file(dirpath):
	fileList = [s for s in os.listdir(dirpath)
		if os.path.isfile(os.path.join(dirpath, s))]
	fileList.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)), reverse=True)
	return fileList

def write_command_succeed_check():
	reqind = resind = 0
	resend = len(write_res)
	reqend = len(write_req)
	for reqind in range(reqend):
		chkfnum = write_req[reqind]['frame']['frame.number']
		for restmp in range(resind, resend):
			if write_res[restmp]['btatt']['btatt.request_in_frame'] == chkfnum:
				write_req[reqind]['response.succeed'] = True
				resind = restmp+1
				print(chkfnum, write_res[restmp]['btatt']['btatt.request_in_frame'])
				break
	return write_res, write_req

def write_command_uuid_check(dic):
	if dic['btatt.service_uuid128'] == SERVICE_UUID128:
		if dic['btatt.uuid128'] in UUIDLIST:
			return True
		else:
			return False

def write_command_extract(filelist):
	for f in filelist:
		if os.path.splitext(d_file + '/' + f)[1] == '.json':
			json_file = open(d_file + '/' + f, encoding="utf8")
			json_read = json.load(json_file)
			for x in range(len(json_read)):
				if json_read[x]['_source']['layers'].get('btatt'):
					tmp = json_read[x]['_source']['layers']['btatt']
					if tmp['btatt.opcode'] == '0x00000012':
						if write_command_uuid_check(tmp['btatt.handle_tree']):	
							write_req.append(json_read[x]['_source']['layers'])
					elif tmp['btatt.opcode'] == '0x00000013':
						if write_command_uuid_check(tmp['btatt.handle_tree']):	
							write_res.append(json_read[x]['_source']['layers'])
			json_file.close()
	write_command_succeed_check()
	print(write_req)
	print(write_res)



write_command_extract(get_file(d_file))
