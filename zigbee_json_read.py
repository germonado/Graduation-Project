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

transactions = []


# Device의 초기 상태 저장, 이후 펌웨어 검증 시 사용
on = 0
color = 0
level = 0


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


filtering_zigbee_zcl(get_file(d_file))
print(len(command_send))
print(len(report_attributes_from_edge))
print(len(read_attribute))
print(len(read_attribute_response_from_edge))
print(len(default_response))
print(len(default_response_from_edge))


        
#기록할 정보 : command 종류, command 값, OK/NG/Warning, 트랜잭션 내의 패킷별 시간, warning이면 오류 생긴 트랜잭션 내의 위치
def makeTransaction():

        # 패킷 리스트 스캔을 위한 iterator
        trans_idx = 1 # 트랜잭션 번호
        
        response_idx = 0 # default response 리스트의 패킷을 나타내는 index (<-)
        
        colorReport_idx = 0 # color의 read 패킷 나타내는 index (->)
        colorReportRes_idx = 0 # color의 read response를 위한 index (<-)
        
        report_idx = 0 # level control에서 report 패킷을 나타내기 위한 index (<-)
        reportResToDevice_idx = 0 # level control할 때, device 방향으로의 response를 위한 index (->)

        
        for command in command_send:
                
                # 트랜잭션을 command 하나당 생성
                transaction = []
                times = []
                errors = []
                cmd = command['zbee_zcl']
                cmdStr = ""
                seq = cmd['zbee_zcl.cmd.tsn']
                transaction.append(trans_idx)
                trans_idx += 1


                #1 command 분류 + 현재 command 전송 시간
                if cmd.get('zbee_zcl_general.onoff.cmd.srv_rx.id'):
                        cmdStr = 'On/Off'
                        transaction.append(cmdStr)
                        transaction.append(cmd['zbee_zcl_general.onoff.cmd.srv_rx.id']) # 1이면 on, 0이면 off
                        
                        on = cmd['zbee_zcl_general.onoff.cmd.srv_rx.id']
                        
                elif cmd.get('zbee_zcl_general.level_control.cmd.srv_rx.id'):
                        cmdStr = 'Level'
                        transaction.append(cmdStr)
                        transaction.append(cmd['Payload']['zbee_zcl_general.level_control.level']) # level값

                        level = cmd['Payload']['zbee_zcl_general.level_control.level']
                        
                elif cmd.get('zbee_zcl_lighting.color_control.cmd.srv_rx.id'):
                        cmdStr = 'Color'
                        transaction.append(cmdStr)
                        transaction.append(cmd['Payload']['zbee_zcl_lighting.color_control.color_temp']) # color값

                        color = cmd['Payload']['zbee_zcl_lighting.color_control.color_temp']

                times.append(command['frame']['frame.time'])


                #2 OK/NG 체크
                temp = default_response_from_edge[response_idx]

                if (temp['zbee_zcl']['zbee_zcl.cmd.tsn'] == seq):
                        transaction.append('OK')
                        times.append(temp['frame']['frame.time'])
                        response_idx += 1
                        
                elif (temp['zbee_zcl']['zbee_zcl.cmd.tsn'] != seq): # command seq가 다른 경우, response가 누락된 것 (2번 위치 에러)
                        transaction.append('NG')
                        errors.append(2)
                        
                        if int(temp['zbee_zcl']['zbee_zcl.cmd.tsn']) == int(seq)+1:
                                transaction.append(times)
                                transaction.append(errors)

                                transactions.append(transaction)
                                continue


                #3 Report 체크 (warning 체크) + 커맨드에 맞게 상태 업데이트가 되었는지 체크
                if cmdStr == ('On/Off' or 'Level'):
                        temp = report_attributes_from_edge[report_idx] # report 패킷

                        # 해당 report가 명령어에 맞는 report인가 체크
                        if temp['zbee_zcl']['Attribute Field'].get('zbee_zcl_general.level_control.attr_id'):
                                if cmdStr == 'On/Off':
                                        transaction[2] += '(No Hub Data)'
                                                
                                        transaction.append(times)
                                        
                                        for i in range(3, 6):
                                                errors.append(i)
                                        transaction.append(errors)

                                        transactions.append(transaction)
                                        continue
                                
                                else: # 여기서 펌웨어 검증
                                        if level != temp['zbee_zcl']['Attribute Field']['zbee_zcl_general.level_control.attr.current_level']:
                                                transaction[2] = 'NG(Level FW)'
                                        
                                        times.append(temp['frame']['frame.time'])
                                        report_idx += 1
                                
                        elif temp['zbee_zcl']['Attribute Field'].get('zbee_zcl_general.onoff.attr_id'):
                                if cmdStr == 'Level':
                                        transaction[2] += '(No Hub Data)'
                                        transaction.append(times)
                                        
                                        for i in range(3, 6):
                                                errors.append(i)
                                        transaction.append(errors)

                                        transactions.append(transaction)
                                        continue

                                else:
                                        if on != temp['zbee_zcl']['Attribute Field']['zbee_zcl_general.onoff.attr.onoff']:
                                                transaction[2] = 'NG(On/Off FW)'
                                                
                                        times.append(temp['frame']['frame.time'])
                                        report_idx += 1

                                
                        # report 이후의 response들이 제대로 왔는지 체크
                        seq = temp['zbee_zcl']['zbee_zcl.cmd.tsn'] # report 패킷의 seq
                        temp2 = default_response[reportResToDevice_idx] # report response 패킷
                        

                        if seq != temp2['zbee_zcl']['zbee_zcl.cmd.tsn']: # report에 대한 response가 없는 경우
                                if transaction[2] == 'OK':
                                        transaction[2] += '(Warning)'
                                errors.append(4)
                                errors.append(5)

                                transaction.append(times)
                                transaction.append(errors)

                                transactions.append(transaction)
                                continue
                                
                        else:
                                times.append(temp2['frame']['frame.time'])
                                temp2 = default_response_from_edge[response_idx]
                                reportResToDevice_idx += 1
                                
                        
                        if seq != temp2['zbee_zcl']['zbee_zcl.cmd.tsn']: # 마지막 response 누락인 경우
                                if transaction[2] == 'OK':
                                        transaction[2] += '(Warning)'
                                errors.append(5)
                                
                        else:
                                times.append(temp2['frame']['frame.time'])
                                response_idx += 1

                        transaction.append(times)
                        transaction.append(errors)
                        transactions.append(transaction)


                elif cmdStr == 'Color':

                        #1 해당 report가 명령어 직후의 report인지 체크 (시간 간격으로 체크)
                        temp = read_attribute[colorReport_idx]

                        if float(temp['frame']['frame.time_relative']) - float(command['frame']['frame.time_relative']) > 2.0:
                                # 시간 이내 아닌 경우
                                transaction[2] += '(No Hub Data)'

                                errors.append(3)
                                errors.append(4)
                                
                                transaction.append(times)
                                transaction.append(errors)

                                transactions.append(transaction)
                                continue
                        
                        else: # 시간 이내이면 FW 검증
                                if temp['zbee_zcl'].get('Attribute Field'):
                                        if color != temp['zbee_zcl']['Attribute Field']['zbee_zcl_lighting.color_control.attr.color_temperature']:
                                                transaction[2] = 'NG(Color FW)'
                                                
                                times.append(temp['frame']['frame.time'])
                                colorReport_idx += 1
                                

                        #2 report 이후의 response가 왔는지 체크
                        seq = temp['zbee_zcl']['zbee_zcl.cmd.tsn']
                        temp2 = read_attribute_response_from_edge[colorReportRes_idx]

                        if seq != temp2['zbee_zcl']['zbee_zcl.cmd.tsn']: # report에 대한 response 없음
                                if transaction[2] == 'OK':
                                        transaction[2] += '(Warning)'
                                errors.append(4)
                                
                        else:
                                times.append(temp2['frame']['frame.time'])
                                colorReportRes_idx += 1

                        transaction.append(times)
                        transaction.append(errors)
                        transactions.append(transaction)
                        


filtering_zigbee_zcl(get_file(d_file))
makeTransaction()
