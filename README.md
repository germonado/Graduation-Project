# Graduation-Project
- IoT 장치의 제어 신호를 스니핑하여 정상 작동여부를 확인하고 log 데이터로 남길 수 있도록 하는 GUI 기반의 모니터링 프로그램 제작
- IoT <-> 허브, IoT <-> Phone, Cloud <-> Phone, Cloud <-> HUB 간의 제어신호 송,수신 파악
- Bluetooth, Zigbee Protocol packet 분석

# Development Environment
- Windows10(64bit)
- Python3.6
- Flask 기반
- Source tree 기반 협업

# How To Use
1. 필수로 설치해야하는 라이브러리 > Flask 라이브러리
2. ./app/module/DB/dbinfo.json 파일에 자신의 디비계정, password등 정보입력
3. ./app/schema/ 경로의 ble, zigbee sql을 실행하여 bluetooth, zigbee를 분류한 데이터들을 넣기 위한 테이블을 만든다. (bluetooth, zigbee packet의 json 파일은 ./exported_json에 존재)
4. python Main.py를 실행한다.
5. 기본 ip 주소는 127.0.0.1(로컬), 8085(포트번호)로 세팅해두었음. 127.0.0.1/8085 로 접속
6. UI에서 bluetooth(default), zigbee command flow를 확인할 수 있고, log report 파일도 다운로드 받을 수 있다.

# Todo list
- .exe 파일로 UI 실행
- 스니핑한 신호를 바탕으로 로그 데이터 정제
- DB 스키마 구성 및 테이블 제작
- flask와 DB 연동
- Frontend에서 사용자 최적 데이터 표시

# Future Goal
- 사용자가 IoT 장치를 모니터링 하며 command flow와 작동여부를 체크할 수 있도록 하는 것
