create schema zigbee;
use zigbee;

CREATE TABLE File_Zigbee
( 
	file_number          integer  NOT NULL ,
	file_name			 varchar(30)  NULL
);

ALTER TABLE File_Zigbee
	ADD CONSTRAINT XPKFile_Zigbee PRIMARY KEY  (file_number ASC);

CREATE TABLE Hub_Zigbee
( 
	file_number          integer  NOT NULL ,
	transaction_number   integer  NOT NULL ,
	source               varchar(20)  NULL ,
	attribute            varchar(20)  NULL ,
	value                integer  NULL ,
	time                 datetime  NULL 
);

ALTER TABLE Hub_Zigbee
	ADD CONSTRAINT XPKHub_Zigbee PRIMARY KEY  CLUSTERED (file_number ASC,transaction_number ASC);

CREATE TABLE NG_Zigbee
( 
	file_number          integer  NOT NULL ,
	transaction_number   integer  NOT NULL ,
	location             integer  NOT NULL
);

ALTER TABLE NG_Zigbee
	ADD CONSTRAINT XPKNG_Zigbee PRIMARY KEY  CLUSTERED (file_number ASC,transaction_number ASC);

CREATE TABLE Packet_Zigbee
( 
	file_number          integer  NOT NULL ,
	transaction_number   integer  NOT NULL ,
	packet_number        integer  NOT NULL ,
	command              varchar(20)  NULL ,
	command_value        integer  NULL ,
	NG					 varchar(20)  NULL ,
	destination          varchar(20)  NULL ,
	source               varchar(20)  NULL ,
	time                 datetime  NULL,
	location			 integer  NOT NULL
);

ALTER TABLE Packet_Zigbee
	ADD CONSTRAINT XPKPacket_Zigbee PRIMARY KEY  CLUSTERED (file_number ASC,transaction_number ASC,packet_number ASC);

CREATE TABLE Transaction_Zigbee
( 
	file_number          integer  NOT NULL ,
	transaction_number   integer  NOT NULL ,
	command              varchar(20)  NULL ,
	command_value        integer  NULL ,
	NG                   varchar(30)  NULL
);

ALTER TABLE Transaction_Zigbee
	ADD CONSTRAINT XPKTransaction_Zigbee PRIMARY KEY  CLUSTERED (file_number ASC,transaction_number ASC);


ALTER TABLE Hub_Zigbee
	ADD CONSTRAINT R_5 FOREIGN KEY (file_number,transaction_number) REFERENCES Transaction_Zigbee(file_number,transaction_number)
		ON DELETE CASCADE
		ON UPDATE CASCADE;


ALTER TABLE NG_Zigbee
	ADD CONSTRAINT R_4 FOREIGN KEY (file_number,transaction_number) REFERENCES Transaction_Zigbee(file_number,transaction_number)
		ON DELETE CASCADE
		ON UPDATE CASCADE;


ALTER TABLE Packet_Zigbee
	ADD CONSTRAINT R_3 FOREIGN KEY (file_number,transaction_number) REFERENCES Transaction_Zigbee(file_number,transaction_number)
		ON DELETE CASCADE
		ON UPDATE CASCADE;


ALTER TABLE Transaction_Zigbee
	ADD CONSTRAINT R_1 FOREIGN KEY (file_number) REFERENCES File_Zigbee(file_number)
		ON DELETE CASCADE
		ON UPDATE CASCADE;
