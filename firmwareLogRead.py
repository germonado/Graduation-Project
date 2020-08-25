import json
import sys
import datetime
import os

d_file = './Firmware_logs'

def get_file(dirpath):
	fileList = [s for s in os.listdir(dirpath)
		if os.path.isfile(os.path.join(dirpath, s))]
	fileList.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)), reverse=True)
	return fileList

def json_data_handling(json_data):
	clstr = json_data['CLuster']
	cmd = json_data['Command']
	if clstr != "ON_OFF":
		ret = int(json_data['return value'])
	else:
		ret = json_data['return value']
	err = False
	if clstr == "LVL_CTRL":
		if ret < 2 and ret > 254:
			err = True
	elif clstr == "ON_OFF":
		if cmd == "OFF" and ret != "False":
			err = True
		elif cmd == "ON" and ret != "True":
			err = True
	elif clstr == "COLOR_CTRL":
		if ret < 240 and ret > 370:
			err = True
	print(err)

def firmware_log_read(filelist):
	for f in filelist:
		if os.path.splitext(d_file + '/' + f)[1] == '.json':
			json_file = open(d_file + '/' + f)
			json_read = json.load(json_file)
			json_data_handling(json_read)
			json_file.close()

firmware_log_read(get_file(d_file))