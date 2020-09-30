import json
import sys
import datetime
import os

d_file = './exported_json/zigbee'
h_file = './exported_json/hub'


#TODO: 리스트를 spec에 기반해서 만들어야 함

# 모든 list는 통신 모식도를 참고하였습니다.
# 실제로 Sender에서 보낸 3가지 종류의 전체 command
command_send = []

# On/Off, Level Control의 경우 Edge에서 오는 report attribute
report_attributes_from_edge = []

# Color Control의 경우 Sender에서 보내는 read attribute
read_attribute = []

# Color Control의 경우 Edge 에서 오는 read attribute response
read_attribute_response_from_edge = []

# On/Off, Level Control의 경우 Sender에서 보내는 default response
default_response = []

# 모든 command에 대해 항상 Edge에서 오는 default response
default_response_by_command_from_edge = []

# On/Off, Level Control의 경우 Edge에서 오는 default reponse
default_response_by_report_from_edge = []


def get_file(dirpath):
	fileList = [s for s in os.listdir(dirpath)
		if os.path.isfile(os.path.join(dirpath, s))]
	fileList.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)), reverse=True)
	return fileList


#최초 command가 실행되기 이전의 주고 받은 packet들은 다 initialization이므로 filtering
def filtering_based_by_command():
	for i in report_attributes_from_edge[:]:
		if i['frame']['frame.number'] < command_send[0]['frame']['frame.number']:
			del report_attributes_from_edge[report_attributes_from_edge.index(i)]

	for i in read_attribute[:]:
		if i['frame']['frame.number'] < command_send[0]['frame']['frame.number']:
			del read_attribute[read_attribute.index(i)]

	for i in read_attribute_response_from_edge[:]:
		if i['frame']['frame.number'] < command_send[0]['frame']['frame.number']:
			del read_attribute_response_from_edge[read_attribute_response_from_edge.index(i)]

	for i in default_response[:]:
		if i['frame']['frame.number'] < command_send[0]['frame']['frame.number']:
			del default_response[default_response.index(i)]

	for i in default_response_by_report_from_edge[:]:
		if i['frame']['frame.number'] < command_send[0]['frame']['frame.number']:
			del default_response_by_report_from_edge[default_response_by_report_from_edge.index(i)]

	for i in default_response_by_command_from_edge[:]:
		if i['frame']['frame.number'] < command_send[0]['frame']['frame.number']:
			del default_response_by_command_from_edge[default_response_by_command_from_edge.index(i)]


#This function filters packets as follow zigbee protocols
def filtering_zigbee_zcl(filelist):
	for f in filelist:
		print(f)
		if os.path.splitext(d_file + '/' + f)[1] == '.json':
			json_file = open(d_file + '/' + 'zigbee30.json', encoding="utf8")
			json_read = json.load(json_file)
			
			for x in range(len(json_read)):
				if json_read[x]['_source']['layers'].get('zbee_zcl'):
					
					# Sender > Edge 로 보내는 Command
					# This if statement distinguishes command packet by Cluster-specific 0x01
					if json_read[x]['_source']['layers']['zbee_zcl'].get('Frame Control Field: Cluster-specific (0x01)'):
						# 각 명령어 별로 해당하는 3가지 종류의 command인지 확인 후 list append
						if json_read[x]['_source']['layers']['zbee_zcl'].get('zbee_zcl_general.level_control.cmd.srv_rx.id'):
							command_send.append(json_read[x]['_source']['layers'])
						elif json_read[x]['_source']['layers']['zbee_zcl'].get('zbee_zcl_general.onoff.cmd.srv_rx.id'):
							command_send.append(json_read[x]['_source']['layers'])
						elif json_read[x]['_source']['layers']['zbee_zcl'].get('zbee_zcl_lighting.color_control.cmd.srv_rx.id'):
							command_send.append(json_read[x]['_source']['layers'])
					
					# Edge > Sender 로 날아오는 packet 들		
					# This elif statement distinguishes default reponse from edge by Profile-wide 0x18
					elif json_read[x]['_source']['layers']['zbee_zcl'].get('Frame Control Field: Profile-wide (0x18)'):
                        
                        # This statement distinguishes default response by command or report                        
						if json_read[x]['_source']['layers']['zbee_zcl']['zbee_zcl.cmd.id'] == "11":
							
							# Response to Command 값이 0x0b 인경우는 Report Attribute에 의해서 만들어진 Default Response
							if json_read[x]['_source']['layers']['zbee_zcl']['zbee_zcl.cmd.id.rsp'] == "0x0000000b":
								default_response_by_report_from_edge.append(json_read[x]['_source']['layers'])
							
							# 그게 아닌 경우 command에 의한 Default Response
							else:
								default_response_by_command_from_edge.append(json_read[x]['_source']['layers'])

						# Color control에서 발생하는 read_attribute response				
						elif json_read[x]['_source']['layers']['zbee_zcl'].get('Status Record'):
							if json_read[x]['_source']['layers']['zbee_zcl']['Status Record'].get('zbee_zcl_lighting.color_control.attr_id'):
								if json_read[x]['_source']['layers']['zbee_zcl']['Status Record']['zbee_zcl_lighting.color_control.attr_id'] == "0x00000007":
									read_attribute_response_from_edge.append(json_read[x]['_source']['layers'])

					# Sender > Edge 로 가는 pakcet					
					elif json_read[x]['_source']['layers']['zbee_zcl'].get('Frame Control Field: Profile-wide (0x00)'):
                                        
                        # On/Off, Color Control에 대해 sender > edge default response                         
						if json_read[x]['_source']['layers']['zbee_zcl']['zbee_zcl.cmd.id'] == "11":
							default_response.append(json_read[x]['_source']['layers'])	
						
						# Color control에서 발생하는 read_attribute request(sender쪽)
						if json_read[x]['_source']['layers']['zbee_zcl'].get('zbee_zcl_lighting.color_control.attr_id'):
							if json_read[x]['_source']['layers']['zbee_zcl']['zbee_zcl_lighting.color_control.attr_id'] == "0x00000007":
								read_attribute.append(json_read[x]['_source']['layers'])
					
					# Edge에서 날아오는 Report attributes 
					elif json_read[x]['_source']['layers']['zbee_zcl'].get('Frame Control Field: Profile-wide (0x08)'):
						
						# This if statement distinguishes report_attribute from edge
						if json_read[x]['_source']['layers']['zbee_zcl']['zbee_zcl.cmd.id'] == "10":
							report_attributes_from_edge.append(json_read[x]['_source']['layers'])

			filtering_based_by_command()				
			json_file.close()

# 동일한 sequence 번호를 갖는 중복 패킷 제거
def removeOverlap(json_list, keyList):
        i = 0
        
        while i < len(json_list) - 1:
                if json_list[i][keyList[0]][keyList[1]] == json_list[i+1][keyList[0]][keyList[1]]:
                        del json_list[i]
                        
                else:
                        i += 1


filtering_zigbee_zcl(get_file(d_file))

key_list = ['zbee_zcl', 'zbee_zcl.cmd.tsn']

removeOverlap(command_send, key_list)
removeOverlap(report_attributes_from_edge, key_list)
removeOverlap(read_attribute, key_list)
removeOverlap(read_attribute_response_from_edge, key_list)
removeOverlap(default_response, key_list)
removeOverlap(default_response_by_command_from_edge, key_list)
removeOverlap(default_response_by_report_from_edge, key_list)


# 각 분류된 list 별로 packet 번호출력 및 구분, 디버깅용이므로 나중에 지울예정
print(len(command_send))
print("COMMAND================================")
for i in command_send:
        print(i['frame']['frame.number'])
        
print("================================")


print(len(default_response_by_command_from_edge))
print("default_response_by_command_from_edge================================")
for i in default_response_by_command_from_edge:
	print(i['frame']['frame.number'])
print("================================")


print(len(report_attributes_from_edge))
print("report_attributes_from_edge================================")
for i in report_attributes_from_edge:
	print(i['frame']['frame.number'])
print("================================")


print(len(default_response_by_report_from_edge))
print("default_response_by_report_from_edge================================")
for i in default_response_by_report_from_edge:
	print(i['frame']['frame.number'])
print("================================")


print(len(read_attribute))
print("read_attribute================================")
for i in read_attribute:
	print(i['frame']['frame.number'])
print("================================")


print(len(read_attribute_response_from_edge))
print("read_attribute_response================================")
for i in read_attribute_response_from_edge:
	print(i['frame']['frame.number'])
print("================================")


print(len(default_response))
print("default_response================================")
for i in default_response:
	print(i['frame']['frame.number'])
print("================================")


hubData = []

def readHubJson(filelist):
        for f in filelist:
                json_file = open(h_file + '/' + f, encoding="utf8")
                json_read = json.load(json_file)
		
                for i in reversed(json_read):
                        hubData.append(i)


readHubJson(get_file(h_file))        

transactions = []
packets = []
NG_packets = []

def timedelta2float(td):
        res = td.microseconds/float(1000000) + (td.seconds + td.days * 24 * 3600)
        return res

        
#기록할 정보 : command 종류, command 값, OK/NG/Warning, 트랜잭션 내의 패킷별 시간, warning이면 오류 생긴 트랜잭션 내의 위치
def makeTransaction(cmdKey, cmdvalueKey):

        trans_idx = 0 # 트랜잭션 번호
        
        hub_idx = 0
        command_idx = 0
        response_idx = 0 # default response 리스트의 패킷을 나타내는 index (<-)
        
        colorReport_idx = 0 # color의 read 패킷 나타내는 index (->)
        colorReportRes_idx = 0 # color의 read response를 위한 index (<-)
        
        report_idx = 0 # report 패킷을 나타내기 위한 index (<-)
        reportResToDevice_idx = 0 # report response 중 device 방향 index (->)
        reportResToHub_idx = 0 # report response 중 허브 방향 index (<-)

        on_time = 0.35
        level_time = 0.85
        color_time = 2.3

        cmdVal = 0
        
        switch = ''
        color = ''
        level = ''


        while hub_idx < len(hubData) or command_idx < len(command_send):
                
                # hub에 있거나 command가 있으면 트랜잭션 생성
                
                transaction = [] # 트랜잭션 로깅 : (파일 번호), 트랜잭션 번호, NG여부(Warning 포함), 커맨드, 커맨드값
                trans_idx += 1

                command = command_send[command_idx]['frame'] # 프레임 번호, 시간기록용
                cmd = command_send[command_idx]['zbee_zcl'] # 커맨드, 커맨드 값 기록용
                cmdOK = False # 커맨드 패킷 존재 유무

                prevCmd = command_send[command_idx-1]['zbee_zcl']
                
                if command_idx < len(command_send)-1:
                        nextCmd = command_send[command_idx+1]['zbee_zcl']
                else:
                        nextCmd = dict()
                
                hub = hubData[hub_idx] # 허브 데이터 접근용
                hubOK = False # 허브 기록 존재 유무

                prevHub = hubData[hub_idx-1]

                if hub_idx < len(hubData)-1:
                        nextHub = hubData[hub_idx+1]
                else:
                        nextHub = dict()
                
                cmdStr = '' # 현재 트랜잭션의 커맨드
                seq = cmd['zbee_zcl.cmd.tsn'] # 커맨드 response 확인용
                transaction.append(trans_idx)


                #1 hub와 command 비교
                hub_time = datetime.datetime.strptime(hub['date'].replace('오후', 'PM').replace('오전', 'AM'), '%Y-%m-%d %I:%M:%S.%f %p KST')
                cmd_time = datetime.datetime.strptime(command['frame.time'], '%b %d, %Y %H:%M:%S.%f000 대한민국 표준시')
                diff = timedelta2float(hub_time - cmd_time)
                print(diff)

                if hub['name'] == 'switch':

                        if prevCmd.get(cmdKey[1]) and switch == 'off' and hub['value'] == 'on' and hubData[hub_idx-1]['name'] == 'level':
                                hub_idx += 1
                                trans_idx -= 1
                                continue
                        
                        if cmd.get(cmdKey[0]) and diff < on_time and diff > 0: # 같은 커맨드, 시간차 내 존재여부 체크
                                cmdStr = 'On/Off' #TODO: 허브 데이터 DB에 저장하는 것
                                cmdVal = hub['value']
                                hub_idx += 1
                                command_idx += 1
                                cmdOK = True
                                hubOK = True
                                packets.append([trans_idx, command['frame.number'], cmdStr, cmdVal, 'Hub', 'Edge', command['frame.time']])
                                
                        elif hub_time < cmd_time: # 패킷 누락(허브 데이터만 존재)
                                hub_idx += 1
                                NG_packets.append([trans_idx, 0])
                                cmdStr = 'On/Off'
                                cmdVal = hub['value']
                                hubOK = True

                        elif hub_time > cmd_time: # 허브 누락(패킷 데이터만 존재)
                                command_idx += 1
                                cmdStr = 'temp'
                                cmdOK = True


                elif hub['name'] == 'level':
                        
                        if cmd.get(cmdKey[1]) and diff < level_time and diff > 0:
                                cmdStr = 'level'
                                cmdVal = hub['value']
                                hub_idx += 1
                                command_idx += 1
                                cmdOK = True
                                hubOK = True
                                packets.append([trans_idx, command['frame.number'], cmdStr, cmdVal, 'Hub', 'Edge', command['frame.time']])
                                
                        elif hub_time < cmd_time: # 패킷 누락(허브 데이터만 존재)
                                hub_idx += 1
                                NG_packets.append([trans_idx, 0])
                                cmdStr = 'level'
                                cmdVal = hub['value']
                                hubOK = True

                        elif hub_time > cmd_time: # 허브 누락(패킷 데이터만 존재)
                                command_idx += 1
                                cmdStr = 'temp'
                                cmdOK = True


                elif hub['name'] == 'colorTemperature':
                        if cmd.get(cmdKey[2]) and diff < color_time and diff > 0:
                                cmdStr = 'color'
                                cmdVal = hub['value']
                                hub_idx += 1
                                command_idx += 1
                                cmdOK = True
                                hubOK = True
                                packets.append([trans_idx, command['frame.number'], cmdStr, cmdVal, 'Hub', 'Edge', command['frame.time']])
                                
                        elif hub_time < cmd_time: # 패킷 누락(허브 데이터만 존재)
                                hub_idx += 1
                                NG_packets.append([trans_idx, 0])
                                cmdStr = 'color'
                                cmdVal = hub['value']
                                hubOK = True

                        elif hub_time > cmd_time: # 허브 누락(패킷 데이터만 존재)
                                command_idx += 1
                                cmdStr = 'temp'
                                cmdOK = True
                                
                                
                transaction.append(cmdStr)
                
                # 허브 누락 시, command를 따름
                if not hubOK:
                        if cmd.get(cmdKey[0]):
                                cmdStr = 'On/Off'
                                transaction[transaction.index('temp')] = cmdStr
                                transaction.append(cmd[cmdKey[0]])
                                cmdVal = cmd[cmdKey[0]]

                        elif cmd.get(cmdKey[1]):
                                cmdStr = 'level'
                                transaction[transaction.index('temp')] = cmdStr
                                transaction.append(cmd['Payload'][cmdvalueKey[0]]) # level값
                                cmdVal = cmd['Payload'][cmdvalueKey[0]]

                        elif cmd.get(cmdKey[2]):
                                cmdStr = 'color'
                                transaction[transaction.index('temp')] = cmdStr
                                transaction.append(cmd['Payload'][cmdvalueKey[1]]) # color값
                                cmdVal = cmd['Payload'][cmdvalueKey[1]]

                        packets.append([trans_idx, command['frame.number'], cmdStr, cmdVal, 'Hub', 'Edge', command['frame.time'], 0])

                else:
                        transaction.append(cmdVal)


                # 커맨드 값으로 현재 상태 업데이트
                if cmdStr == 'On/Off':
                        switch = cmdVal

                elif cmdStr == 'level':
                        level = cmdVal

                elif cmdStr == 'color':
                        color = cmdVal
                        
                
                #2 OK/NG 체크: 허브나 패킷 둘다 있으면 OK, 둘 중 하나만 있으면 Warning, 둘 다 없으면 NG
                temp = default_response_by_command_from_edge[response_idx]
                seqCompare = temp['zbee_zcl']['zbee_zcl.cmd.tsn']
                
                if hubOK and cmdOK:
                        
                        transaction.append('OK')

                        if seqCompare == seq:
                                if cmdStr == 'On/Off' and nextCmd.get(cmdKey[2]):
                                        trans_idx -= 1
                                        hub_idx -= 1
                                        response_idx += 1
                                        continue
                                
                                packets.append([trans_idx, temp['frame']['frame.number'], cmdStr, cmdVal, 'Edge', 'Hub', temp['frame']['frame.number'], 1])
                                response_idx += 1

                        elif seqCompare < seq: # 허브랑 커맨드가 있는데, response를 중간에 빠트림 -> 다시 처음으로 돌아가서 체크
                                command_idx -= 1
                                hub_idx -= 1
                                response_idx += 1
                                continue

                        elif seqCompare > seq: # response 쪽 누락
                                transaction[transaction.index('OK')] = 'OK(Sniffing Error)'
                                NG_packets.append([trans_idx, 1])
                        
                        
                elif cmdOK:
                        #cmd가 있어도 response 없으면 NG
                        if seqCompare == seq: # response가 맞게 있는 경우

                                # cmd가 on/off이면 다음 명령어가 color인지 체크해야 함, color인데 누락일 때에만 다음 transaction
                                if cmdStr == 'On/Off' and (nextCmd.get(cmdKey[2]) or nextHub['name'] == 'color'):
                                        print('here')
                                        trans_idx -= 1
                                        response_idx += 1
                                        continue
                                
                                transaction.append('OK(No Hub Data)')
                                packets.append([trans_idx, temp['frame']['frame.number'], cmdStr, cmdVal, 'Edge', 'Hub', temp['frame']['frame.number'], 1])
                                response_idx += 1

                        elif seqCompare < seq: # 커맨드보다 seq가 작은 경우, 커맨드 누락 (커맨드 값 알수없음, 인덱스만 변경)
                                command_idx -= 1
                                response_idx += 1
                                continue # 만들어진 트랜잭션 폐기

                        elif seqCompare > seq: # response가 큰 경우, response 쪽 누락
                                transaction.append('NG')
                                NG_packets.append([trans_idx, 1])

                        
                elif hubOK: # 커맨드 누락 -> response 패킷 리스트 인덱스 맞춰줘야 함
                        if seqCompare == seq:
                                transaction.append('OK(No Command Packet)')
                                # 현재 커맨드가 누락되었는데, seq가 같다면 temp의 seq가 1 큰 것 -> response도 누락
                                NG_packets.append([trans_idx, 1])

                        elif seqCompare < seq: # 커맨드 하나만 누락, response는 있음
                                transaction.append('OK(Sniffing Error)')
                                response_idx += 1

                        elif seqCompare > seq: # reponse 누락
                                transaction.append('OK(Sniffing Error)')
                                NG_packets.append([trans_idx, 1])
                                

                print(transaction)
                print()

                '''
                #3 Report 체크 (warning 체크) + 커맨드에 맞게 상태 업데이트가 되었는지 체크
                if cmdStr == 'On/Off' or cmdStr == 'Level':
                        temp = report_attributes_from_edge[report_idx] # report 패킷

                        # 해당 report가 명령어에 맞는 report인가 체크
                        if temp['zbee_zcl']['Attribute Field'].get('zbee_zcl_general.level_control.attr_id'):
                                if cmdStr == 'On/Off':
                                        transaction[3] += '(No Hub Data)'
                                                
                                        transaction.append(times)
                                        
                                        for i in range(3, 6):
                                                errors.append(i)
                                        transaction.append(errors)

                                        transactions.append(transaction)
                                        continue
                                
                                else: # 여기서 펌웨어 검증
                                        print(temp['zbee_zcl']['Attribute Field'])
                                        print(level)
                                        if level != temp['zbee_zcl']['Attribute Field']['zbee_zcl_general.level_control.attr.current_level']:
                                                transaction[3] = 'NG(Level FW)'
                                        
                                        times.append(temp['frame']['frame.time'])
                                        report_idx += 1
                                
                        elif temp['zbee_zcl']['Attribute Field'].get('zbee_zcl_general.onoff.attr_id'):
                                if cmdStr == 'Level':
                                        transaction[3] += '(No Hub Data)'
                                        transaction.append(times)
                                        
                                        for i in range(3, 6):
                                                errors.append(i)
                                        transaction.append(errors)

                                        transactions.append(transaction)
                                        continue

                                else:
                                        if on != temp['zbee_zcl']['Attribute Field']['zbee_zcl_general.onoff.attr.onoff']:
                                                transaction[3] = 'NG(On/Off FW)'
                                                
                                        times.append(temp['frame']['frame.time'])
                                        report_idx += 1

                        
                        # report 이후의 response들이 제대로 왔는지 체크
                        seq = temp['zbee_zcl']['zbee_zcl.cmd.tsn'] # report 패킷의 seq
                        temp2 = default_response[reportResToDevice_idx] # report response 패킷
                        

                        if seq != temp2['zbee_zcl']['zbee_zcl.cmd.tsn']: # report에 대한 response가 없는 경우
                                if transaction[3] == 'OK':
                                        transaction[3] += '(Warning)'
                                errors.append(4)
                                errors.append(5)

                                transaction.append(times)
                                transaction.append(errors)

                                transactions.append(transaction)
                                continue
                                
                        else:
                                times.append(temp2['frame']['frame.time'])
                                temp2 = default_response_by_report_from_edge[reportResToHub_idx]
                                reportResToDevice_idx += 1
                                
                        
                        if seq != temp2['zbee_zcl']['zbee_zcl.cmd.tsn']: # 마지막 response 누락인 경우
                                if transaction[3] == 'OK':
                                        transaction[3] += '(Warning)'
                                errors.append(5)
                                
                        else:
                                times.append(temp2['frame']['frame.time'])
                                reportResToHub_idx += 1

                        transaction.append(times)
                        transaction.append(errors)
                        transactions.append(transaction)


                elif cmdStr == 'Color':

                        #1 해당 report가 명령어 직후의 report인지 체크 (시간 간격으로 체크)
                        temp = read_attribute[colorReport_idx]

                        if float(temp['frame']['frame.time_relative']) - float(command['frame']['frame.time_relative']) > color_time:
                                # 시간 이내 아닌 경우
                                transaction[3] += '(No Hub Data)'

                                errors.append(3)
                                errors.append(4)
                                
                                transaction.append(times)
                                transaction.append(errors)

                                transactions.append(transaction)
                                continue
                        
                        else:
                                times.append(temp['frame']['frame.time'])
                                colorReport_idx += 1
                                

                        #2 report 이후의 response가 왔는지 체크
                        seq = temp['zbee_zcl']['zbee_zcl.cmd.tsn']
                        temp2 = read_attribute_response_from_edge[colorReportRes_idx]

                        if seq != temp2['zbee_zcl']['zbee_zcl.cmd.tsn']: # report에 대한 response 없음
                                if transaction[3] == 'OK':
                                        transaction[3] += '(Warning)'
                                errors.append(4)
                                
                        else: # 시간 이내이면 FW 검증
                                if temp2['zbee_zcl'].get('Status Record'):
                                        if color != temp2['zbee_zcl']['Status Record']['zbee_zcl_lighting.color_control.attr.color_temperature']:
                                                transaction[3] = 'NG(Color FW)'
                                
                                times.append(temp2['frame']['frame.time'])
                                colorReportRes_idx += 1

                        transaction.append(times)
                        transaction.append(errors)
                        transactions.append(transaction)
                '''
                        

command_key = ['zbee_zcl_general.onoff.cmd.srv_rx.id', 'zbee_zcl_general.level_control.cmd.srv_rx.id', 'zbee_zcl_lighting.color_control.cmd.srv_rx.id']
command_value = ['zbee_zcl_general.level_control.level', 'zbee_zcl_lighting.color_control.color_temp']

makeTransaction(command_key, command_value)

