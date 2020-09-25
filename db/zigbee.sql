
CREATE TABLE File_Zigbee
( 
	file_number          integer  NOT NULL 
)
go

ALTER TABLE File_Zigbee
	ADD CONSTRAINT XPKFile_Zigbee PRIMARY KEY  CLUSTERED (file_number ASC)
go

CREATE TABLE Herb_Zigbee
( 
	source               varchar(20)  NULL ,
	file_number          integer  NOT NULL ,
	transaction_number   integer  NOT NULL ,
	attribute            varchar(20)  NULL ,
	value                integer  NULL ,
	time                 datetime  NULL 
)
go

ALTER TABLE Herb_Zigbee
	ADD CONSTRAINT XPKHerb_Zigbee PRIMARY KEY  CLUSTERED (file_number ASC,transaction_number ASC)
go

CREATE TABLE NG_Zigbee
( 
	file_number          integer  NOT NULL ,
	location             varchar(20)  NULL ,
	transaction_number   integer  NOT NULL 
)
go

ALTER TABLE NG_Zigbee
	ADD CONSTRAINT XPKNG_Zigbee PRIMARY KEY  CLUSTERED (file_number ASC,transaction_number ASC)
go

CREATE TABLE Packet_Zigbee
( 
	file_number          integer  NOT NULL ,
	transaction_number   integer  NOT NULL ,
	packet_number        integer  NOT NULL ,
	command              varchar(20)  NULL ,
	command_value        integer  NULL ,
	destination          varchar(20)  NULL ,
	source               varchar(20)  NULL ,
	time                 datetime  NULL 
)
go

ALTER TABLE Packet_Zigbee
	ADD CONSTRAINT XPKPacket_Zigbee PRIMARY KEY  CLUSTERED (file_number ASC,transaction_number ASC,packet_number ASC)
go

CREATE TABLE Transaction_Zigbee
( 
	file_number          integer  NOT NULL ,
	NG                   bit  NULL ,
	transaction_number   integer  NOT NULL ,
	command              varchar(20)  NULL ,
	command_value        integer  NULL 
)
go

ALTER TABLE Transaction_Zigbee
	ADD CONSTRAINT XPKTransaction_Zigbee PRIMARY KEY  CLUSTERED (file_number ASC,transaction_number ASC)
go


ALTER TABLE Herb_Zigbee
	ADD CONSTRAINT R_5 FOREIGN KEY (file_number,transaction_number) REFERENCES Transaction_Zigbee(file_number,transaction_number)
		ON DELETE NO ACTION
		ON UPDATE NO ACTION
go


ALTER TABLE NG_Zigbee
	ADD CONSTRAINT R_4 FOREIGN KEY (file_number,transaction_number) REFERENCES Transaction_Zigbee(file_number,transaction_number)
		ON DELETE NO ACTION
		ON UPDATE NO ACTION
go


ALTER TABLE Packet_Zigbee
	ADD CONSTRAINT R_3 FOREIGN KEY (file_number,transaction_number) REFERENCES Transaction_Zigbee(file_number,transaction_number)
		ON DELETE NO ACTION
		ON UPDATE NO ACTION
go


ALTER TABLE Transaction_Zigbee
	ADD CONSTRAINT R_1 FOREIGN KEY (file_number) REFERENCES File_Zigbee(file_number)
		ON DELETE NO ACTION
		ON UPDATE NO ACTION
go
