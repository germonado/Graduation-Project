import json
import sys
import datetime
import os

d_file = './exported_json/zigbee'

command_send = []
command_receive_from_edge = []
report_attributes_from_edge = []
read_attribute = []
read_attribute_response_from_edge = []
default_response = []
default_response_from_edge = []

def get_file(dirpath):
	fileList = [s for s in os.listdir(dirpath)
		if os.path.isfile(os.path.join(dirpath, s))]
	fileList.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)), reverse=True)
	return fileList

def filtering_zigbee_zcl(filelist):
	for f in filelist:
		print(f)
		if os.path.splitext(d_file + '/' + f)[1] == '.json':
			json_file = open(d_file + '/' + 'zigbee30.json', encoding="utf8")
			json_read = json.load(json_file)
			for x in range(len(json_read)):
				if json_read[x]['_source']['layers'].get('zbee_zcl'):
					if json_read[x]['_source']['layers']['zbee_zcl'].get('Frame Control Field: Cluster-specific (0x01)'):
						command_send.append(json_read[x]['_source']['layers'])
					elif json_read[x]['_source']['layers']['zbee_zcl'].get('Frame Control Field: Profile-wide (0x18)'):
						if json_read[x]['_source']['layers']['zbee_zcl']['zbee_zcl.cmd.id'] == "11":
							default_response_from_edge.append(json_read[x]['_source']['layers'])
					elif json_read[x]['_source']['layers']['zbee_zcl'].get('Frame Control Field: Profile-wide (0x00)'):
						if json_read[x]['_source']['layers']['zbee_zcl']['zbee_zcl.cmd.id'] == "11":
							default_response.append(json_read[x]['_source']['layers'])	
					elif json_read[x]['_source']['layers']['zbee_zcl'].get('zbee_zcl.cmd.id'):
						if json_read[x]['_source']['layers']['zbee_zcl']['zbee_zcl.cmd.id'] == "10":
							report_attributes_from_edge.append(json_read[x]['_source']['layers'])
						elif json_read[x]['_source']['layers']['zbee_zcl']['zbee_zcl.cmd.id'] == "0":
							read_attribute.append(json_read[x]['_source']['layers'])
						elif json_read[x]['_source']['layers']['zbee_zcl']['zbee_zcl.cmd.id'] == "1":
							read_attribute_response_from_edge.append(json_read[x]['_source']['layers'])
			json_file.close()

filtering_zigbee_zcl(get_file(d_file))



