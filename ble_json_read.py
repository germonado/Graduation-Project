import json
import sys
import datetime
import os

# For checking valid uuid
SERVICE_UUID128 = "3a:1f:25:93:d2:b6:4e:e0:af:9f:5f:c0:ad:d2:e1:55"

# For distinguishing transaction with uuid
UUIDDICT = {
			'9f:50:a6:fa:d3:62:40:89:b7:78:25:7e:a0:97:37:69':'OnOff',
			'cc:97:79:39:dc:de:4e:6d:83:19:f2:5f:3f:96:f2:3c':'Dim Level',
			'ed:8f:a6:8f:fa:c2:42:fc:9c:21:69:bf:d7:1b:e4:4b':'Color Temp',
			'a4:49:64:32:4c:fd:40:9f:92:dd:a4:76:52:80:36:c4':'Color X',
			'6c:b0:45:f5:b3:ec:4e:95:a5:a7:b9:10:ad:b7:c8:41':'Color Y'
}


class BluetoothCheck:
	

	def __init__(self):
		self.write_req = []
		self.write_res = []
		self.report_list = []
		self.cmd_statistics = []
		self.onoff_statistics = [0,0,0]
		self.dim_level_statistics = [0,0,0]
		self.color_temp_statistics = [0,0,0]
		self.d_file = './exported_json/ble'

	def initialize(self):

		self.write_req = []
		self.write_res = []
		self.report_list = []
		self.cmd_statistics = []
		self.onoff_statistics = [0,0,0]
		self.dim_level_statistics = [0,0,0]
		self.color_temp_statistics = [0,0,0]


	# This function draws file
	def get_file(self):
		
		dirpath = self.d_file
		fileList = [s for s in os.listdir(dirpath)
			if os.path.isfile(os.path.join(dirpath, s))]
		fileList.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)), reverse=True)
		
		for f in fileList:
			self.write_command_extract(f)
			break


	# This function distinguish command type and count for statistics
	def classify_command(self, str, cmd_success):
		
		if str == "OnOff":
			self.onoff_statistics[0] += 1
			if cmd_success == "Success":
				self.onoff_statistics[1] += 1
			else:
				self.onoff_statistics[2] += 1

		elif str == "Color Temp":
			self.color_temp_statistics[0] += 1;
			if cmd_success == "Success":
				self.color_temp_statistics[1] += 1
			else:
				self.color_temp_statistics[2] += 1

		elif str == "Dim Level":
			self.dim_level_statistics[0] += 1
			if cmd_success == "Success":
				self.dim_level_statistics[1] += 1
			else:
				self.dim_level_statistics[2] += 1


	# This function checks whether transaction packet succeeded or not
	def write_command_succeed_check(self):
		
		reqind = resind = 0
		transaction_number = 0
		ng_count = 0
		success_count = 0
		send_miss = 0
		resend = len(self.write_res)
		reqend = len(self.write_req)
		for reqind in range(reqend):
			# chkfnum has the frame number of write request packet, for checking write response
			chkfnum = self.write_req[reqind]['frame']['frame.number']
			transaction_number = transaction_number + 1;
			flag = 0
			for restmp in range(resind, resend):
				# if write response 
				if self.write_res[restmp]['btatt']['btatt.request_in_frame'] == chkfnum:
					flag = 1
					success_check = "Success"
					success_count = success_count + 1
					send_timeinfo = datetime.datetime.strptime(self.write_req[reqind]['frame']['frame.time'], '%b %d, %Y %H:%M:%S.%f000 대한민국 표준시')
					send_cmd = UUIDDICT[self.write_req[reqind]['btatt']['btatt.handle_tree']['btatt.uuid128']]
					receive_timeinfo = datetime.datetime.strptime(self.write_res[restmp]['frame']['frame.time'], '%b %d, %Y %H:%M:%S.%f000 대한민국 표준시')
					src = self.write_req[reqind]['btle']['btle.master_bd_addr']
					dst = self.write_req[reqind]['btle']['btle.slave_bd_addr']
					temp_item_send = [transaction_number, send_cmd, src, dst, success_check, send_timeinfo, receive_timeinfo]
					self.classify_command(send_cmd, success_check)
					self.report_list.append(temp_item_send)
					resind = restmp+1
					break

				elif self.write_res[restmp]['btatt']['btatt.request_in_frame'] < chkfnum:
					success_check = "NG"
					ng_count = ng_count + 1
					send_miss = send_miss + 1
					send_framenum = self.write_res[resind]['frame']['frame.number']
					send_timeinfo = datetime.datetime.strptime(self.write_res[resind]['frame']['frame.time'], '%b %d, %Y %H:%M:%S.%f000 대한민국 표준시')
					send_cmd = UUIDDICT[self.write_res[resind]['btatt']['btatt.handle_tree']['btatt.uuid128']]
					src = self.write_res[resind]['btle']['btle.master_bd_addr']
					dst = self.write_res[resind]['btle']['btle.slave_bd_addr']
					temp_item = [transaction_number, send_cmd, src, dst, success_check, send_timeinfo, "No Send Command"]
					self.classify_command(send_cmd, success_check)
					self.report_list.append(temp_item)
					print(self.write_res[restmp]['btatt']['btatt.request_in_frame'])
					break

			
			# 만약 transaction에 대한 response가 돌아오지 않았을때
			if flag == 0:
				success_check = "NG"
				ng_count = ng_count + 1
				send_framenum = self.write_req[reqind]['frame']['frame.number']
				send_timeinfo = datetime.datetime.strptime(self.write_req[reqind]['frame']['frame.time'], '%b %d, %Y %H:%M:%S.%f000 대한민국 표준시')
				print(send_framenum)
				send_cmd = UUIDDICT[self.write_req[reqind]['btatt']['btatt.handle_tree']['btatt.uuid128']]
				src = self.write_req[reqind]['btle']['btle.master_bd_addr']
				dst = self.write_req[reqind]['btle']['btle.slave_bd_addr']
				temp_item = [transaction_number, send_cmd, src, dst, success_check, send_timeinfo, "No Response Command"]
				self.classify_command(send_cmd, success_check)
				self.report_list.append(temp_item)

		print("============write_req====================")
		for i in self.write_req:
			print(i['frame']['frame.number'])
		print("============write_req====================")
		for i in self.write_res:
			print(i['frame']['frame.number'])
		for i in self.report_list:
			print(i)

		self.cmd_statistics = [self.onoff_statistics, self.color_temp_statistics, self.dim_level_statistics, ng_count, success_count , len(self.write_req)+send_miss]
		return self.report_list, self.cmd_statistics


	# This function checks if transaction packet is subset of valid service UUID
	def write_command_uuid_check(self, dic):
		
		# Checking the valid SERVICE_UUID of transaction packet
		if dic['btatt.service_uuid128'] == SERVICE_UUID128:
			if UUIDDICT.get(dic['btatt.uuid128']):
				return True
			else:
				return False


	# This function extracts only transaction packet from whole wireshark packet
	def write_command_extract(self, f):
		
		self.initialize()

		if os.path.splitext(self.d_file + '/' + f)[1] == '.json':
			json_file = open(self.d_file + '/' + f, encoding="utf8")
			json_read = json.load(json_file)
			for x in range(len(json_read)):
				if json_read[x]['_source']['layers'].get('btatt'):
					tmp = json_read[x]['_source']['layers']['btatt']
					# if btatt.opcode number is 12, then this packet is write request packet
					if tmp['btatt.opcode'] == '0x00000012':
						if self.write_command_uuid_check(tmp['btatt.handle_tree']):	
							self.write_req.append(json_read[x]['_source']['layers'])
					# if btatt.opcode number is 13, then this packet is write response packet
					elif tmp['btatt.opcode'] == '0x00000013':
						if self.write_command_uuid_check(tmp['btatt.handle_tree']):	
							self.write_res.append(json_read[x]['_source']['layers'])
			
			json_file.close()