
CREATE TABLE Beacon_ble
( 
	source               varchar(20)  NULL ,
	file_number          integer  NOT NULL ,
	transaction_number   integer  NOT NULL ,
	attribute            varchar(20)  NULL ,
	value                integer  NULL ,
	time                 datetime  NULL 
)
go

ALTER TABLE Beacon_ble
	ADD CONSTRAINT XPKHerb_Zigbee PRIMARY KEY  CLUSTERED (file_number ASC,transaction_number ASC)
go

CREATE TABLE File_ble
( 
	file_number          integer  NOT NULL ,
	file_name            char(18)  NULL 
)
go

ALTER TABLE File_ble
	ADD CONSTRAINT XPKFile_Zigbee PRIMARY KEY  CLUSTERED (file_number ASC)
go

CREATE TABLE Packet_ble
( 
	file_number          integer  NOT NULL ,
	transaction_number   integer  NOT NULL ,
	packet_number        integer  NOT NULL ,
	command              varchar(20)  NULL ,
	destination          varchar(20)  NULL ,
	source               varchar(20)  NULL ,
	time                 datetime  NULL 
)
go

ALTER TABLE Packet_ble
	ADD CONSTRAINT XPKPacket_Zigbee PRIMARY KEY  CLUSTERED (file_number ASC,transaction_number ASC,packet_number ASC)
go

CREATE TABLE Transaction_ble
( 
	file_number          integer  NOT NULL ,
	NG                   bit  NULL ,
	transaction_number   integer  NOT NULL ,
	command              varchar(20)  NULL 
)
go

ALTER TABLE Transaction_ble
	ADD CONSTRAINT XPKTransaction_Zigbee PRIMARY KEY  CLUSTERED (file_number ASC,transaction_number ASC)
go


ALTER TABLE Beacon_ble
	ADD CONSTRAINT R_5 FOREIGN KEY (file_number,transaction_number) REFERENCES Transaction_ble(file_number,transaction_number)
		ON DELETE NO ACTION
		ON UPDATE NO ACTION
go


ALTER TABLE Packet_ble
	ADD CONSTRAINT R_3 FOREIGN KEY (file_number,transaction_number) REFERENCES Transaction_ble(file_number,transaction_number)
		ON DELETE NO ACTION
		ON UPDATE NO ACTION
go


ALTER TABLE Transaction_ble
	ADD CONSTRAINT R_1 FOREIGN KEY (file_number) REFERENCES File_ble(file_number)
		ON DELETE NO ACTION
		ON UPDATE NO ACTION
go
