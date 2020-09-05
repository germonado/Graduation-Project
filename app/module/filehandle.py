import json
import sys
import datetime
import os

class FileHandle:
	def remove_file_in_dir(dirpath):

	def get_file_time_order_in_dir(dirpath):
		fileList = [s for s in os.listdir(dirpath)
			if os.path.isfile(os.path.join(dirpath, s))]
		fileList.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)), reverse=True)
		return fileList