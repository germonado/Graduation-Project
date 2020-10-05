create database ble;
use ble;

CREATE TABLE File_ble
( 
	file_number          integer  NOT NULL ,
	file_name            char(18)  NULL 
);

ALTER TABLE File_ble
	ADD CONSTRAINT XPKFile_BLE PRIMARY KEY  (file_number ASC);

CREATE TABLE NG_ble
( 
	file_number          integer  NOT NULL ,
	transaction_number   integer  NOT NULL ,
	location             integer  NULL 
);

ALTER TABLE NG_ble
	ADD CONSTRAINT XPKNG_BLE PRIMARY KEY  CLUSTERED (file_number ASC,transaction_number ASC);

CREATE TABLE Transaction_ble
( 
	file_number          integer  NOT NULL ,
	transaction_number   integer  NOT NULL ,
	command              varchar(20)  NULL ,
	phone_address        varchar(20)  NULL ,
	device_address       varchar(20)  NULL ,
	NG                   varchar(20)  NULL ,
	request_time         datetime  NULL ,
	response_time        datetime  NULL 
);

ALTER TABLE Transaction_ble
	ADD CONSTRAINT XPKTransaction_BLE PRIMARY KEY  CLUSTERED (file_number ASC,transaction_number ASC);


ALTER TABLE NG_ble
	ADD CONSTRAINT R_6 FOREIGN KEY (file_number,transaction_number) REFERENCES Transaction_ble(file_number,transaction_number)
		ON DELETE CASCADE
		ON UPDATE CASCADE;


ALTER TABLE Transaction_ble
	ADD CONSTRAINT R_1 FOREIGN KEY (file_number) REFERENCES File_ble(file_number)
		ON DELETE CASCADE
		ON UPDATE CASCADE;
