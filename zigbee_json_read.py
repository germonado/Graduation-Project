import json
import sys
import datetime
import os

d_file = './exported_json/zigbee'

command_send = []
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

#This function filters packets as follow zigbee protocols
def filtering_zigbee_zcl(filelist):
	for f in filelist:
		print(f)
		if os.path.splitext(d_file + '/' + f)[1] == '.json':
			json_file = open(d_file + '/' + 'zigbee30.json', encoding="utf8")
			json_read = json.load(json_file)
			for x in range(len(json_read)):
				if json_read[x]['_source']['layers'].get('zbee_zcl'):
					# This if statement distinguishes command packet by Cluster-specific 0x01
					if json_read[x]['_source']['layers']['zbee_zcl'].get('Frame Control Field: Cluster-specific (0x01)'):
						command_send.append(json_read[x]['_source']['layers'])
					# This elif statement distinguishes default reponse from edge by Profile-wide 0x18
					elif json_read[x]['_source']['layers']['zbee_zcl'].get('Frame Control Field: Profile-wide (0x18)'):
                                                # command에 대한 response
                                                
						if json_read[x]['_source']['layers']['zbee_zcl']['zbee_zcl.cmd.id'] == "11":
							default_response_from_edge.append(json_read[x]['_source']['layers'])
						elif json_read[x]['_source']['layers']['zbee_zcl']['zbee_zcl.cmd.id'] == "1":
							read_attribute_response_from_edge.append(json_read[x]['_source']['layers'])

					elif json_read[x]['_source']['layers']['zbee_zcl'].get('Frame Control Field: Profile-wide (0x00)'):
                                                # report에 대한 response
                                                
						if json_read[x]['_source']['layers']['zbee_zcl']['zbee_zcl.cmd.id'] == "11":
							default_response.append(json_read[x]['_source']['layers'])	
					elif json_read[x]['_source']['layers']['zbee_zcl'].get('zbee_zcl.cmd.id'):
						# This if statement distinguishes report_attribute from edge
						if json_read[x]['_source']['layers']['zbee_zcl']['zbee_zcl.cmd.id'] == "10":
							report_attributes_from_edge.append(json_read[x]['_source']['layers'])
						# This elif statement distinguishes send read_attribute 
						elif json_read[x]['_source']['layers']['zbee_zcl']['zbee_zcl.cmd.id'] == "0":
							read_attribute.append(json_read[x]['_source']['layers'])

			json_file.close()

<<<<<<< HEAD
filtering_zigbee_zcl(get_file(d_file))
#print(command_send)
print(command_receive_from_edge)
#print(report_attributes_from_edge)
#print(read_attribute)
#print(read_attribute_response_from_edge)
#print(default_response)
#print(default_response_from_edge)
=======

        
#기록할 정보 : command 종류, command 값, OK/NG/Warning, 트랜잭션 내의 패킷별 시간, warning이면 오류 생긴 트랜잭션 내의 위치
def makeTransaction():
        trans_idx = 1
        
        response_idx = 0
        
        colorReport_idx = 0
        colorReportRes_idx = 0
        
        report_idx = 0 # level control에서 report 패킷을 나타내기 위한 index
        reportResToHub_idx = 0 # level control할 때, 마지막으로 돌아오는 response를 위한 index
        

        for command in command_send:
                transaction = []
                times = []
                cmd = command['zbee_zcl']
                cmdStr = ""
                seq = cmd['zbee_zcl.cmd.tsn']
                transaction.append(trans_idx) # 트랜잭션 번호를 맨 앞에 기록
                trans_idx += 1

                if cmd.get('zbee_zcl_general.onoff.cmd.srv_rx.id'):
                        cmdStr = 'On/Off'
                        transaction.append(cmdStr)
                        transaction.append(cmd['zbee_zcl_general.onoff.cmd.srv_rx.id']) # 1이면 on, 0이면 off
                        
                elif cmd.get('zbee_zcl_general.level_control.cmd.srv_rx.id'):
                        cmdStr = 'Level'
                        transaction.append(cmdStr)
                        transaction.append(cmd['Payload']['zbee_zcl_general.level_control.level']) # level값
                        
                elif cmd.get('zbee_zcl_lighting.color_control.cmd.srv_rx.id'):
                        cmdStr = 'Color'
                        transaction.append(cmdStr)
                        transaction.append(cmd['Payload']['zbee_zcl_lighting.color_control.color_temp']) # color값


                #1 OK/NG 체크
                temp = default_response[response_idx]

                if (temp['zbee_zcl']['zbee_zcl.cmd.tsn'] == seq):
                        transaction.append('OK')
                else:
                        transaction.append('NG')
                        
                response_idx += 1


                #2 Report 체크 (warning 체크) + 커맨드에 맞게 상태 업데이트가 되었는지 체크
                if cmdStr == ('On/Off' or 'Level'):
                        #hub 기록 체크, report_idx, res_idx, hub_idx 전부 옮기면서 그 때의 seq 체크
                        temp = report_attributes_from_edge[report_idx]

                        # 해당 report가 명령어에 맞는 report인가 체크
                        if temp['zbee_zcl']['Attribute Field'].get('zbee_zcl_general.level_control.attr_id'):
                                if cmdStr == 'On/Off':
                                        transaction[2] = 'Warning(No Hub Data)'
                                        report_idx += 1
                                        break
                                
                        elif temp['zbee_zcl']['Attribute Field'].get('zbee_zcl_general.onoff.attr_id'):
                                if cmdStr == 'Level':
                                        transaction[2] = 'Warning(No Hub Data)'
                                        report_idx += 1
                                        break

                                
                        # report 이후의 response들이 제대로 왔는지 체크
                        seq = temp['zbee_zcl']['zbee_zcl.cmd.tsn']
                        temp2 = default_response[response_idx]['zbee_zcl']
>>>>>>> master

                        if seq != temp2['zbee_zcl.cmd.tsn']: # report에 대한 response가 없는 경우
                                transaction[2] = 'Warning'
                                temp2 = default_response_from_edge[reportResToHub_idx]['zbee_zcl']
                                #TODO: 오류 생긴 트랜잭션 위치 기록 (4번 패킷 오류)
                        else:
                                #TODO: 값 비교 후 이전 value와 일치하는지 체크 -> 안 변했으면 펌웨어 문제
                                transaction[2] = 'NG(FW)'
                                

                        if seq != temp2['zbee_zcl.cmd.tsn']: # 마지막 response 누락인 경우
                                transaction[2] = 'Warning'
                                #TODO: 오류 생긴 트랜잭션 위치 기록 (5번 패킷 오류)

                        response_idx += 1
                        reportResToHub_idx += 1

                                                
                elif cmdStr == 'Color':
                        # hub 기록 체크 및 값 변경 체크
                        temp = read_attribute[colorReport_idx]

                        #TODO: 해당 report가 명령어에 맞는 report인가 체크 -> 시간으로?, 일단 보류, 없으면 Warning(No Hub Data)

                        # report 이후의 response가 왔는지 체크
                        seq = temp['zbee_zcl']['zbee_zcl.cmd.tsn']
                        print('ok', colorReportRes_idx)
                        print(read_attribute_response_from_edge)
                        temp2 = read_attribute_response_from_edge[colorReportRes_idx]['zbee_zcl']

                        if seq != temp2['zbee_zcl.cmd.tsn']: # report에 대한 response 없음
                                transaction[2] = 'Warning'
                                #TODO: 오류 생긴 트랜잭션 위치 기록 (4번 패킷 오류)

                        colorReport_idx += 1
                        colorReportRes_idx += 1
                        


filtering_zigbee_zcl(get_file(d_file))
makeTransaction()
