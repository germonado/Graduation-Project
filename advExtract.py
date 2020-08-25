import json
import os,sys
import glob

def readBLE(js):
    with open(js, encoding='utf8') as file:
        i = json.load(file)

    bleDict = []
    
    for j in i:
        temp = j['_source']
        temp = temp['layers']
        
        if 'btle' in temp:
            bleDict.append(temp['btle'])
        
    return bleDict


def extractData(bleDict):
    #bleDict는 btle 정보가 담긴 리스트
    datas = []

    for e in bleDict:
        if 'btcommon.eir_ad.advertising_data' in e:
            data_tmp = e['btcommon.eir_ad.advertising_data']
            data_tmp = data_tmp['btcommon.eir_ad.entry']
            
            if 'btcommon.eir_ad.entry.data' in data_tmp:
                tempStr = data_tmp['btcommon.eir_ad.entry.data']
                
                if tempStr not in datas:
                    datas.append(tempStr)

    return datas


def parsingData(dataStr):
    i = dataStr.find('32:2f:')
    parsing = { }

    if i != -1:
        i += 6
        cnt_a = int(dataStr[i:i+2])
        i += 3
        
        for a in range(cnt_a):
            paramCnt = int(dataStr[i:i+2])
            
            i += 3
            func = ''

            for param in range(paramCnt):
                if (dataStr[i] == 'a'):
                    func = dataStr[i:i+2]
                    parsing[func] = []
                    
                    i += 3
                    
                else:
                    data = int(dataStr[i:i+2], 16)
                    data = hex(data)
                    parsing[func].append(data)

                    i += 3

    return parsing  


if __name__ == '__main__':
    jsonPaths = glob.glob('exported_json/*.json')

    for path in jsonPaths:
        
        ble = readBLE(path)
        advs = extractData(ble)

        for a in advs:
            print(a)
            print(parsingData(a))
            
        

