import json
import sys
import datetime
import os

d_file = './exported_json/zigbee'
h_file = './exported_json/hub'


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


hubData = []

hub_db = []
transactions = []
packets = []
NG_packets = []


trans_idx = 0 # 트랜잭션 번호

hub_idx = 0
command_idx = 0
response_idx = 0 # default response 리스트의 패킷을 나타내는 index (<-)
        
colorReport_idx = 0 # color의 read 패킷 나타내는 index (->)
colorReportRes_idx = 0 # color의 read response를 위한 index (<-)
        
report_idx = 0 # report 패킷을 나타내기 위한 index (<-)
reportResToDevice_idx = 0 # report response 중 device 방향 index (->)
reportResToHub_idx = 0 # report response 중 허브 방향 index (<-)

on_time = 0.36
level_time = 0.85
color_time = 2.3

switch = '1'
level = ''
color = ''

cmdStr = ''
cmdVal = ''

command_key = ['zbee_zcl_general.onoff.cmd.srv_rx.id', 'zbee_zcl_general.level_control.cmd.srv_rx.id',
               'zbee_zcl_lighting.color_control.cmd.srv_rx.id']
command_value = ['zbee_zcl_general.level_control.level', 'zbee_zcl_lighting.color_control.color_temp']
attribute_list = ['zbee_zcl_general.onoff.attr_id', 'zbee_zcl_general.level_control.attr_id', 'zbee_zcl_lighting.color_control.attr_id']
attribute_values = ['zbee_zcl_general.onoff.attr.onoff', 'zbee_zcl_general.level_control.attr.current_level',
                    'zbee_zcl_lighting.color_control.attr.color_temperature']
key_list = ['zbee_zcl', 'zbee_zcl.cmd.tsn']


# 함수 정의 -----------------------------------------------------------------------------------------------------------------

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
def filtering_zigbee_zcl(file):
	
		print(file)
		if os.path.splitext(d_file + '/' + file)[1] == '.json':
			json_file = open(d_file + '/' + file, encoding="utf8")
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

			#filtering_based_by_command()				
			json_file.close()

# 동일한 sequence 번호를 갖는 중복 패킷 제거
def removeOverlap(json_list, keyList):
        i = 0
        
        while i < len(json_list) - 1:
                if json_list[i][keyList[0]][keyList[1]] == json_list[i+1][keyList[0]][keyList[1]]:
                        del json_list[i]
                        
                else:
                        i += 1


def readHubJson(fileName):
        json_file = open(h_file + '/' + fileName, encoding="utf8")
        json_read = json.load(json_file)
		
        for i in reversed(json_read):
                hubData.append(i)

    
def timedelta2float(td):
        res = td.microseconds/float(1000000) + (td.seconds + td.days * 24 * 3600)
        return res

        
#기록할 정보 : command 종류, command 값, OK/NG/Warning, 트랜잭션 내의 패킷별 시간, warning이면 오류 생긴 트랜잭션 내의 위치
def makeTransaction(cmdKey, cmdvalueKey):

        # 사용하는 전역 변수
        global trans_idx
        global hub_idx, command_idx, response_idx
        global on_time, level_time, color_time
        global cmdVal, cmdStr
        global switch, color, level


        transaction = [] # 트랜잭션 번호, NG여부(Warning 포함), 커맨드, 커맨드값
        trans_idx += 1
        transaction.append(trans_idx)


        # 커맨드 패킷 리스트의 follow를 위한 변수
        cmdFrame = command_send[command_idx]['frame'] # 프레임 번호, 시간기록용
        cmdZcl = command_send[command_idx]['zbee_zcl'] # 커맨드, 커맨드 값 기록용
        cmdSeq = cmdZcl['zbee_zcl.cmd.tsn'] # 커맨드 sequence 번호
        cmdOK = False # 커맨드 패킷 존재 유무

        prevCmd = command_send[command_idx-1]['zbee_zcl']
                
        if command_idx < len(command_send)-1:
                nextCmd = command_send[command_idx+1]['zbee_zcl']
        else:
                nextCmd = dict()


        # 허브 리스트의 follow를 위한 변수
        hub = hubData[hub_idx]
        hubOK = False # 허브 기록 존재 유무

        prevHub = hubData[hub_idx-1]

        if hub_idx < len(hubData)-1:
                nextHub = hubData[hub_idx+1]
        else:
                nextHub = dict()

        
        #1 hub와 command 비교: 시간대를 보면서 더 이른 쪽에 인덱스 증가, 늦은 쪽은 인덱스 유지, 같은 명령어에 시간대 이내면 두 인덱스 증가
        hub_time = datetime.datetime.strptime(hub['date'].replace('오후', 'PM').replace('오전', 'AM'), '%Y-%m-%d %I:%M:%S.%f %p KST')
        cmd_time = datetime.datetime.strptime(cmdFrame['frame.time'], '%b %d, %Y %H:%M:%S.%f000 대한민국 표준시')
        diff = timedelta2float(hub_time - cmd_time)


        if hub['name'] == 'switch':

                if prevCmd.get(cmdKey[1]) and int(switch, 16) == 0 and hub['value'] == 'on' and prevHub['name'] == 'level':
                        hub_idx += 1
                        trans_idx -= 1
                        switch = '1'
                        return
                        
                if cmdZcl.get(cmdKey[0]) and diff < on_time and diff > 0: # 같은 커맨드, 시간차 내 존재여부 체크
                        cmdStr = 'On/Off'
                        cmdVal = hub['value']
                        hub_idx += 1
                        command_idx += 1
                        cmdOK = True
                        hubOK = True
                                
                elif hub_time < cmd_time: # 패킷 누락(허브 데이터만 존재)
                        hub_idx += 1
                        NG_packets.append([trans_idx, 1])
                        cmdStr = 'On/Off'
                        cmdVal = hub['value']
                        hubOK = True

                elif hub_time > cmd_time: # 허브 누락(패킷 데이터만 존재)
                        command_idx += 1
                        cmdStr = 'temp'
                        cmdOK = True


        elif hub['name'] == 'level':
                        
                if cmdZcl.get(cmdKey[1]) and diff < level_time and diff > 0:
                        cmdStr = 'level'
                        cmdVal = hub['value']
                        hub_idx += 1
                        command_idx += 1
                        cmdOK = True
                        hubOK = True
                                
                elif hub_time < cmd_time: # 패킷 누락(허브 데이터만 존재)
                        hub_idx += 1
                        NG_packets.append([trans_idx, 1])
                        cmdStr = 'level'
                        cmdVal = hub['value']
                        hubOK = True

                elif hub_time > cmd_time: # 허브 누락(패킷 데이터만 존재)
                        command_idx += 1
                        cmdStr = 'temp'
                        cmdOK = True


        elif hub['name'] == 'colorTemperature':

                if cmdZcl.get(cmdKey[2]) and diff < color_time and diff > 0:
                        cmdStr = 'color'
                        cmdVal = hub['value']
                        hub_idx += 1
                        command_idx += 1
                        cmdOK = True
                        hubOK = True
                                
                elif hub_time < cmd_time: # 패킷 누락(허브 데이터만 존재)
                        hub_idx += 1
                        NG_packets.append([trans_idx, 1])
                        cmdStr = 'color'
                        cmdVal = hub['value']
                        hubOK = True

                elif hub_time > cmd_time: # 허브 누락(패킷 데이터만 존재)
                        command_idx += 1
                        cmdStr = 'temp'
                        cmdOK = True
                                
                                
        transaction.append(cmdStr)

        if cmdStr == 'color': # 직전 커맨드 패킷이 on인지 확인하고, 아니면 1번 NG
                color = cmdVal

                if not prevCmd.get(cmdKey[0]):
                        NG_packets.append([trans_idx, 1])

                if packets[-1][0] != trans_idx or packets[-1][-1] != 2:
                        NG_packets.append([trans_idx, 2])
                        

        change = True
        
        # 커맨드 값을 따르게 함
        if cmdOK:
                if cmdZcl.get(cmdKey[0]):
                        cmdStr = 'On/Off'
                        if 'temp' in transaction:
                                transaction[transaction.index('temp')] = cmdStr
                                
                        transaction.append(cmdZcl[cmdKey[0]])
                        cmdVal = cmdZcl[cmdKey[0]]
                        
                        if switch == cmdVal:
                                change = False
                        
                        switch = cmdVal

                elif cmdZcl.get(cmdKey[1]):
                        cmdStr = 'level'
                        if 'temp' in transaction:
                                transaction[transaction.index('temp')] = cmdStr
                                
                        transaction.append(cmdZcl['Payload'][cmdvalueKey[0]]) # level값
                        cmdVal = cmdZcl['Payload'][cmdvalueKey[0]]

                        if level == cmdVal:
                                change = False
                        
                        level = cmdVal

                elif cmdZcl.get(cmdKey[2]):
                        cmdStr = 'color'
                        if 'temp' in transaction:
                                transaction[transaction.index('temp')] = cmdStr
                                
                        transaction.append(cmdZcl['Payload'][cmdvalueKey[1]]) # color값
                        cmdVal = cmdZcl['Payload'][cmdvalueKey[1]]

                        if color == cmdVal:
                                change = False
                                
                        color = cmdVal

                if cmdStr == 'color':
                        packets.append([trans_idx, cmdFrame['frame.number'], cmdStr, cmdVal, 'Hub', 'Edge', cmd_time, 3])

                else:
                        if cmdStr == 'On/Off' and (nextCmd.get(cmdKey[2]) or hub['name'] == 'color'):
                                packets.append([trans_idx, cmdFrame['frame.number'], 'color', cmdVal, 'Hub', 'Edge', cmd_time, 1])

                        else:
                                packets.append([trans_idx, cmdFrame['frame.number'], cmdStr, cmdVal, 'Hub', 'Edge', cmd_time, 1])

        else:
                transaction.append(cmdVal)
                        
                
        #2 OK/NG 체크: 허브나 패킷 둘다 있으면 OK, 둘 중 하나만 있으면 Warning, 둘 다 없으면 NG
        response = default_response_by_command_from_edge[response_idx]
        
        seqCompare = response['zbee_zcl']['zbee_zcl.cmd.tsn']
        response = response['frame']


        if hubOK and cmdOK:
                
                if int(switch, 16) == 0 and hub['name'] == 'level' and nextHub['name'] != 'switch':
                        transaction.append('OK(No Switch Log)')
                                
                else:
                        transaction.append('OK')

                while seqCompare < cmdSeq:
                        response_idx += 1
                        response = default_response_by_command_from_edge[response_idx]
                        seqCompare = response['zbee_zcl']['zbee_zcl.cmd.tsn']
                        response = response['frame']

                response_time = datetime.datetime.strptime(response['frame.time'], '%b %d, %Y %H:%M:%S.%f000 대한민국 표준시')

                if seqCompare == cmdSeq:
                        if cmdStr == 'color':
                                packets.append([trans_idx, response['frame.number'], cmdStr, cmdVal, 'Edge', 'Hub', response_time, 4])
                        else:
                                packets.append([trans_idx, response['frame.number'], cmdStr, cmdVal, 'Edge', 'Hub', response_time, 2])
                        response_idx += 1

                elif seqCompare > cmdSeq: # response 쪽 누락
                        transaction[transaction.index('OK')] = 'OK(Sniffing Error)'
                        NG_packets.append([trans_idx, 2])

                hub_db.append([trans_idx, hub['source'], cmdStr, hub['value'], hub_time])
                        
                        
        elif cmdOK:
                #cmd가 있어도 response 없으면 NG
                if seqCompare == cmdSeq: # response가 맞게 있는 경우
                        if change:
                                transaction.append('OK(No Hub Data)')
                        else:
                                transaction.append('OK')

                        response_time = datetime.datetime.strptime(response['frame.time'], '%b %d, %Y %H:%M:%S.%f000 대한민국 표준시')
                        
                        if cmdStr == 'color':
                                packets.append([trans_idx, response['frame.number'], cmdStr, cmdVal, 'Edge', 'Hub', response_time, 4])
                        elif cmdStr == 'On/Off' and (nextCmd.get(cmdKey[2]) or hub['name'] == 'color'):
                                packets.append([trans_idx, response['frame.number'], 'color', cmdVal, 'Edge', 'Hub', response_time, 2])
                                trans_idx -= 1
                                response_idx += 1
                                return
                        else:
                                packets.append([trans_idx, response['frame.number'], cmdStr, cmdVal, 'Edge', 'Hub', response_time, 2])
                        response_idx += 1

                elif seqCompare < cmdSeq: # 커맨드보다 seq가 작은 경우, 커맨드 누락 (커맨드 값 알수없음, 인덱스만 변경)
                        command_idx -= 1
                        response_idx += 1
                        return # 만들어진 트랜잭션 폐기

                elif seqCompare > cmdSeq: # response가 큰 경우, response 쪽 누락
                        transaction.append('NG')
                        NG_packets.append([trans_idx, 2])

                        
        elif hubOK: # 커맨드 누락 -> response 패킷 리스트 인덱스 맞춰줘야 함
                if seqCompare == cmdSeq:
                        transaction.append('OK(No Command Packet)')
                        # 현재 커맨드가 누락되었는데, seq가 같다면 temp의 seq가 1 큰 것 -> response도 누락
                        NG_packets.append([trans_idx, 2])

                elif seqCompare < cmdSeq: # 커맨드 하나만 누락, response는 있음
                        transaction.append('OK(Sniffing Error)')
                        response_idx += 1

                elif seqCompare > cmdSeq: # reponse 누락
                        transaction.append('OK(Sniffing Error)')
                        NG_packets.append([trans_idx, 2])

                hub_db.append([trans_idx, hub['source'], cmdStr, hub['value'], hub_time])
                                

        transactions.append(transaction)
        print(transaction)

        if cmdOK and change:
                return cmd_time
        
        elif hubOK:
                return hub_time

                

def attributeCheck(command_time, cmdStr, attributes, attrValues):

        # 해당 transaction에 해당하는 패킷 에러들 로깅
        
        # 사용하는 전역 변수
        
        global colorReport_idx # color의 read 패킷 나타내는 index (->)
        global colorReportRes_idx # color의 read response를 위한 index (<-)
                        
        global report_idx # report 패킷을 나타내기 위한 index (<-)
        global reportResToDevice_idx # report response 중 device 방향 index (->)
        global reportResToHub_idx # report response 중 허브 방향 index (<-)

        if cmdStr == 'color':
                attr = read_attribute[colorReport_idx]
                resTime = 2
        else:
                attr = report_attributes_from_edge[report_idx]

                if cmdStr == 'On/Off':
                        resTime = 0.3
                else:
                        resTime = 0.8
                
        
        prevAttr = report_attributes_from_edge[report_idx-1]['zbee_zcl']
        attr_time = datetime.datetime.strptime(attr['frame']['frame.time'], '%b %d, %Y %H:%M:%S.%f000 대한민국 표준시')
        diff = timedelta2float(attr_time - command_time)

        while attr_time < command_time and abs(diff) > resTime:
                if cmdStr != 'color':
                        report_idx += 1
                        attr = report_attributes_from_edge[report_idx]
                        attr_time = datetime.datetime.strptime(attr['frame']['frame.time'], '%b %d, %Y %H:%M:%S.%f000 대한민국 표준시')
                else:
                        colorReport_idx += 1
                        attr = read_attribute[colorReport_idx]
                        attr_time = datetime.datetime.strptime(attr['frame']['frame.time'], '%b %d, %Y %H:%M:%S.%f000 대한민국 표준시')

                diff = timedelta2float(attr_time - command_time)
                
                print(diff)

        attrFrame = attr['frame']
        attrZcl = attr['zbee_zcl']
        attrSeq = attrZcl['zbee_zcl.cmd.tsn']

                        
        if cmdStr == 'On/Off':

                # 패킷 추가할 때 cmdStr 부분을 level로 해줘야 함
                
                #1 Report 패킷 체크
                if attrZcl['Attribute Field'].get(attributes[0]) and abs(diff) < resTime:
                        attrVal = attrZcl['Attribute Field'][attrValues[0]]

                        if not ((attrVal == switch) or (int(attrVal, 16) == 0 and switch == 'off') or (int(attrVal, 16) == 1 and switch == 'on')): # 상태가 맞게 변한 경우
                                if transactions[-1][1] != 'level':
                                        transactions[-1][3] = 'NG(FW)'
                                        print('On/OFF', attrVal, switch)

                                
                        if transactions[-1][1] == 'level':
                                packets.append([trans_idx, attrFrame['frame.number'], 'level', cmdVal, 'Edge', 'Hub', attr_time, 6])

                        else:
                                packets.append([trans_idx, attrFrame['frame.number'], cmdStr, cmdVal, 'Edge', 'Hub', attr_time, 3])
                        report_idx += 1
                                

                elif attr_time > command_time: # report 패킷 누락
                        NG_packets.append([trans_idx, 3])
                        attrSeq = str(int(attrSeq)-1)

                
                #2 Report response 패킷 체크 -> seq 번호로
                response = default_response[reportResToDevice_idx]
                seqCompare = response['zbee_zcl']['zbee_zcl.cmd.tsn']
                response = response['frame']

                while seqCompare < attrSeq:
                        reportResToDevice_idx += 1
                        response = default_response[reportResToDevice_idx]
                        seqCompare = response['zbee_zcl']['zbee_zcl.cmd.tsn']
                        response = response['frame']
                        

                if seqCompare == attrSeq:
                        response_time = datetime.datetime.strptime(response['frame.time'], '%b %d, %Y %H:%M:%S.%f000 대한민국 표준시')
                        
                        if transactions[-1][1] == 'level':
                                packets.append([trans_idx, response['frame.number'], 'level', cmdVal, 'Hub', 'Edge', response_time, 7])
                                
                        else:
                                packets.append([trans_idx, response['frame.number'], cmdStr, cmdVal, 'Hub', 'Edge', response_time, 4])
                        reportResToDevice_idx += 1

                elif seqCompare > attrSeq: # response 쪽 누락
                        NG_packets.append([trans_idx, 4])


                response = default_response_by_report_from_edge[reportResToHub_idx]
                seqCompare = response['zbee_zcl']['zbee_zcl.cmd.tsn']
                response = response['frame']

                while seqCompare < attrSeq:
                        reportResToHub_idx += 1
                        response = default_response_by_report_from_edge[reportResToHub_idx]
                        seqCompare = response['zbee_zcl']['zbee_zcl.cmd.tsn']
                        response = response['frame']
                        
        
                if seqCompare == attrSeq:
                        response_time = datetime.datetime.strptime(response['frame.time'], '%b %d, %Y %H:%M:%S.%f000 대한민국 표준시')

                        if transactions[-1][1] == 'level':
                                packets.append([trans_idx, response['frame.number'], 'level', cmdVal, 'Edge', 'Hub', response_time, 8])
                                
                        else:
                                packets.append([trans_idx, response['frame.number'], cmdStr, cmdVal, 'Edge', 'Hub', response_time, 5])
                        reportResToHub_idx += 1

                elif seqCompare > attrSeq: # response 쪽 누락
                        NG_packets.append([trans_idx, 5])
                        


        elif cmdStr == 'level':
                if attrZcl['Attribute Field'].get(attributes[1]) and abs(diff) < resTime:
                        attrVal = attrZcl['Attribute Field'][attrValues[1]]

                        if not ((attrVal == level) or False): # TODO: level 값 맞춰주는 부분 추가할 것(False 대신)
                                transactions[-1][3] = 'NG(FW)'
                                print('level', attrVal, level)
                                
                        packets.append([trans_idx, attrFrame['frame.number'], cmdStr, cmdVal, 'Edge', 'Hub', attr_time, 3])
                        report_idx += 1

                elif attr_time > command_time: # report 패킷 누락
                        NG_packets.append([trans_idx, 3])
                        attrSeq = str(int(attrSeq)-1)


                #2 Report response 패킷 체크 -> seq 번호로
                
                response = default_response[reportResToDevice_idx]
                seqCompare = response['zbee_zcl']['zbee_zcl.cmd.tsn']
                response = response['frame']

                while seqCompare < attrSeq:
                        reportResToDevice_idx += 1
                        response = default_response[reportResToDevice_idx]
                        seqCompare = response['zbee_zcl']['zbee_zcl.cmd.tsn']
                        response = response['frame']
                        
                if seqCompare == attrSeq:
                        response_time = datetime.datetime.strptime(response['frame.time'], '%b %d, %Y %H:%M:%S.%f000 대한민국 표준시')
                        packets.append([trans_idx, response['frame.number'], cmdStr, cmdVal, 'Hub', 'Edge', response_time, 4])
                        reportResToDevice_idx += 1

                elif seqCompare > attrSeq: # response 쪽 누락
                        NG_packets.append([trans_idx, 4])
                        attrSeq = str(int(attrSeq)-1)


                response = default_response_by_report_from_edge[reportResToHub_idx]
                seqCompare = response['zbee_zcl']['zbee_zcl.cmd.tsn']
                response = response['frame']

                while seqCompare < attrSeq:
                        reportResToHub_idx += 1
                        response = default_response_by_report_from_edge[reportResToHub_idx]
                        seqCompare = response['zbee_zcl']['zbee_zcl.cmd.tsn']
                        response = response['frame']
                        
        
                if seqCompare == attrSeq:
                        response_time = datetime.datetime.strptime(response['frame.time'], '%b %d, %Y %H:%M:%S.%f000 대한민국 표준시')
                        packets.append([trans_idx, response['frame.number'], cmdStr, cmdVal, 'Edge', 'Hub', response_time, 5])
                        reportResToHub_idx += 1

                elif seqCompare > attrSeq: # response 쪽 누락
                        NG_packets.append([trans_idx, 5])


                # 현재 상태가 off이면 다음에 hub에 on이 와야 함-> report attribute 검사하기
                if switch == 'off' or int(switch, 16) == 0:
                        attributeCheck(command_time, 'On/Off', attributes, attrValues)
                        return


        elif cmdStr == 'color':

                #1 Read report 패킷 체크
                if attrZcl.get(attributes[2]) and abs(diff) < resTime:
                        packets.append([trans_idx, attrFrame['frame.number'], cmdStr, cmdVal, 'Hub', 'Edge', attr_time, 5])
                        colorReport_idx += 1

                elif attr_time > command_time: # report 패킷 누락
                        NG_packets.append([trans_idx, 5])
                        attrSeq = str(int(attrSeq)-1)

                
                #2 Read report response 패킷 체크 -> seq 번호로
                response = read_attribute_response_from_edge[colorReportRes_idx]
                seqCompare = response['zbee_zcl']['zbee_zcl.cmd.tsn']
                resValue = response['zbee_zcl']['Status Record'][attrValues[2]]
                response = response['frame']

                while seqCompare < attrSeq:
                        colorReportRes_idx += 1
                        response = read_attribute_response_from_edge[colorReportRes_idx]
                        seqCompare = response['zbee_zcl']['zbee_zcl.cmd.tsn']
                        resValue = response['zbee_zcl']['Status Record'][attrValues[2]]
                        response = response['frame']
                        
                
                if seqCompare == attrSeq:
                        response_time = datetime.datetime.strptime(response['frame.time'], '%b %d, %Y %H:%M:%S.%f000 대한민국 표준시')
                        packets.append([trans_idx, response['frame.number'], cmdStr, cmdVal, 'Edge', 'Hub', response_time, 6])
                        colorReportRes_idx += 1

                        if not (color == resValue or False): #TODO: color값이 허브값 가져오면 맞춰줘야 함
                                transactions[-1][3] = 'NG(FW)'
                                print('color', color, resValue)

                elif seqCompare > attrSeq: # response 쪽 누락
                        NG_packets.append([trans_idx, 6])
                


def errorCheck():
        
        while hub_idx < len(hubData) and command_idx < len(command_send):

                time = makeTransaction(command_key, command_value)
                # check할 필요가 없는 경우 존재함 -> 허브 데이터가 없어도 될 때
                # color 앞의 on, 값이 이전과 다르지 않은 커맨드 날라올 때
                
                if time != None:
                        attributeCheck(time, cmdStr, attribute_list, attribute_values)

                # 시간이 return될 때, None인 경우는 on-color의 on, level 다음 on



def addSniffingError():
        global transactions

        for NG in NG_packets:
              if transactions[NG[0]-1][-1] == 'OK':
                      transactions[NG[0]-1][-1] = 'OK(Sniffing Error)'


def exportLogList(zbee_file, hub_file):
        filtering_zigbee_zcl(zbee_file)

        removeOverlap(command_send, key_list)
        removeOverlap(report_attributes_from_edge, key_list)
        removeOverlap(read_attribute, key_list)
        removeOverlap(read_attribute_response_from_edge, key_list)
        removeOverlap(default_response, key_list)
        removeOverlap(default_response_by_command_from_edge, key_list)
        removeOverlap(default_response_by_report_from_edge, key_list)

        readHubJson(hub_file)

        errorCheck()
        addSniffingError()
                
        return hub_db, transactions, packets, NG_packets


# 디버깅용 출력 함수 ----------------------------------------------------------------------------

# 각 분류된 list 별로 packet 번호출력 및 구분, 디버깅용이므로 나중에 지울예정
def debugging():
        
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

        print('hub ==========================================================')
        for i in hub_db:
                print(i)

        print('transactions =================================================')
        for i in transactions:
                print(i)

        print('packets ======================================================')
        for e in packets:
                print(e)

        print('NG ===========================================================')
        print(NG_packets)



exportLogList('20200603.json', 'hublog.json')
debugging()
