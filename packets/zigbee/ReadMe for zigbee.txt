[환경] 
Windows 10 64bit i7-10U / Wireshark 3.2.4

[복호화 단계]
1. Ctrl + Shift + P
2. Protocol 탭의 ZigBee 선택
3. Pre-configured Keys 'Edit...' 선택
4. '+' 버튼 선택하여 key 2개 추가
 - 5A:69:67:42:65:65:41:6C:6C:69:61:6E:63:65:30:39 / Normal / ZigbeeAlliance09
 - ac:30:0f:57:c3:75:14:7b:e3:b4:2f:8d:85:fb:5a:1e / Normal / 아무이름
5. 'OK' 선택

----- 이건 필요한 단계인지 잘 모르겠음 -----
6. Protocol 탭의 IEEE 802.15.4 선택
7. Decryption Keys 'Edit...' 선택
8. 00112233445566778899aabbccddeeff / 0 / Thread hash 추가
9. 'OK' 선택

https://github.com/NordicSemiconductor/nRF-Sniffer-for-802.15.4

[참고사항]
ZLC OnOff : LED 켜고 끌 때
ZLC Level Control : LED 밝기 조절
ZLC Color Control : LED 색 조절

안되면 카톡 주세용~