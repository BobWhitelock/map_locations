 # Downloaded  and adapted from http://forum.geonames.org/gforum/posts/list/6703.page (27/06/14)
 # Inserts all tables which is overkill as dont think I need, can adapt and remove some later when decide what do need

# Updates:
#	- change locations files read from
#	- change many updates to make empty string values NULL instead of 0 or similar
#	- added alternate_name index to alternate_names table

 # Will import the following files from download.geonames.org/export/dump
 # admin1CodesASCII.txt
 # admin2Codes.txt
 # allCountries.zip
 # alternateNames.zip
 # countryInfo.txt
 # featureCodes_bg.txt
 # featureCodes_en.txt
 # featureCodes_nb.txt
 # featureCodes_nn.txt
 # featureCodes_no.txt
 # featureCodes_ru.txt
 # featureCodes_sv.txt
 # hierarchy.zip
 # iso-languagecodes.txt
 # no-country.zip
 # timeZones.txt
 #
 # Postal Codes are loaded from download.geonames.org/export/zip
 # allCountries.zip
 #
 # Script will by default load the txt files from /media/Storage/geonames_data/. Postal codes loaded from /media/Storage/geonames_data/postalcodes. Unpack any zip files.
 #
 # countryInfo.txt has a large number of commented out lines as the header. This script
 # is coded to ignore 51 lines at the start of the text file. You will want to verify
 # that this number is still correct.
 
 DROP SCHEMA IF EXISTS geonames_import;
 DROP SCHEMA IF EXISTS geonames;
 CREATE SCHEMA geonames_import DEFAULT CHARACTER SET utf8mb4;
 CREATE SCHEMA geonames DEFAULT CHARACTER SET utf8mb4;
 
 USE geonames_import;
 
 CREATE TABLE alternate_names (
   alternateNameId varchar(10) NOT NULL,
   geonameid varchar(10) NULL,
   isolanguage VARCHAR(7) NULL,
   alternate_name VARCHAR(200) NULL,
   isPreferredName varchar(1) NULL,
   isShortName varchar(1) NULL,
   isColloquial varchar(1) NULL,
   isHistoric varchar(1) NULL
 )
 ENGINE = InnoDB
 COLLATE = utf8mb4_unicode_ci;
 
 LOAD DATA INFILE '/media/Storage/geonames_data/alternateNames.txt' INTO TABLE alternate_names CHARACTER SET utf8mb4;
 UPDATE alternate_names SET isPreferredName=0 WHERE isPreferredName='';
 UPDATE alternate_names SET isShortName=0 WHERE isShortName='';
 UPDATE alternate_names SET isColloquial=0 WHERE isColloquial='';
 UPDATE alternate_names SET isHistoric=0 WHERE isHistoric='';
 
 
 CREATE TABLE countryinfo (
   iso char(2),
   iso3 char(3),
   iso_numeric int(11),
   fips varchar(3),
   name varchar(200),
   capital varchar(200),
   areainsqkm varchar(15),
   population bigint,
   continent char(2),
   tld char(3),
   currencycode char(3),
   currencyname varchar(20),
   phone varchar(20),
   postalcodeformat varchar(100),
   postalcoderegex varchar(255),
   languages varchar(200),
   geonameid varchar(10),
   neighbours varchar(100),
   equivalentfipscode varchar(10)
 ) ENGINE=InnoDB
 COLLATE = utf8mb4_unicode_ci;
 
 
 LOAD DATA INFILE '/media/Storage/geonames_data/countryInfo.txt' INTO TABLE countryinfo CHARACTER SET utf8mb4 IGNORE 51 LINES;
 UPDATE countryinfo SET areainsqkm=NULL WHERE areainsqkm='';
 UPDATE countryinfo SET geonameid=NULL WHERE geonameid='';
 
 
 CREATE TABLE featurecodes (
   language char(2) DEFAULT 'bg',
   featurecode varchar(10) DEFAULT NULL,
   desc1 varchar(100) DEFAULT NULL,
   desc2 varchar(500) DEFAULT NULL
 ) ENGINE=InnoDB
 COLLATE = utf8mb4_unicode_ci;
 
 LOAD DATA INFILE '/media/Storage/geonames_data/featureCodes_bg.txt' INTO TABLE featurecodes CHARACTER SET utf8mb4 (featurecode,desc1,desc2);
 ALTER TABLE geonames_import.featurecodes CHANGE COLUMN language language CHAR(2) NULL DEFAULT 'en';
 LOAD DATA INFILE '/media/Storage/geonames_data/featureCodes_en.txt' INTO TABLE featurecodes CHARACTER SET utf8mb4 (featurecode,desc1,desc2);
 ALTER TABLE geonames_import.featurecodes CHANGE COLUMN language language CHAR(2) NULL DEFAULT 'en';
 LOAD DATA INFILE '/media/Storage/geonames_data/featureCodes_en.txt' INTO TABLE featurecodes CHARACTER SET utf8mb4 (featurecode,desc1,desc2);
 ALTER TABLE geonames_import.featurecodes CHANGE COLUMN language language CHAR(2) NULL DEFAULT 'nb';
 LOAD DATA INFILE '/media/Storage/geonames_data/featureCodes_nb.txt' INTO TABLE featurecodes CHARACTER SET utf8mb4 (featurecode,desc1,desc2);
 ALTER TABLE geonames_import.featurecodes CHANGE COLUMN language language CHAR(2) NULL DEFAULT 'nn';
 LOAD DATA INFILE '/media/Storage/geonames_data/featureCodes_nn.txt' INTO TABLE featurecodes CHARACTER SET utf8mb4 (featurecode,desc1,desc2);
 ALTER TABLE geonames_import.featurecodes CHANGE COLUMN language language CHAR(2) NULL DEFAULT 'no';
 LOAD DATA INFILE '/media/Storage/geonames_data/featureCodes_no.txt' INTO TABLE featurecodes CHARACTER SET utf8mb4 (featurecode,desc1,desc2);
 ALTER TABLE geonames_import.featurecodes CHANGE COLUMN language language CHAR(2) NULL DEFAULT 'ru';
 LOAD DATA INFILE '/media/Storage/geonames_data/featureCodes_ru.txt' INTO TABLE featurecodes CHARACTER SET utf8mb4 (featurecode,desc1,desc2);
 ALTER TABLE geonames_import.featurecodes CHANGE COLUMN language language CHAR(2) NULL DEFAULT 'sv';
 LOAD DATA INFILE '/media/Storage/geonames_data/featureCodes_sv.txt' INTO TABLE featurecodes CHARACTER SET utf8mb4 (featurecode,desc1,desc2);
 ALTER TABLE geonames_import.featurecodes CHANGE COLUMN language language CHAR(2) NULL;
 DELETE FROM featurecodes WHERE featurecode='null';
 
 
 CREATE TABLE geoname (
   geonameid varchar(15) NOT NULL,
   name varchar(200) NULL,
   asciiname varchar(200) NULL,
   alternatenames TEXT NULL,
   latitude decimal(7,5) NULL,
   longitude decimal(8,5) NULL,
   feature_class varchar(1) NULL,
   feature_code varchar(10) NULL,
   country_code char(2) NULL,
   cc2 varchar(60) NULL,
   admin1_code varchar(60) NULL,
   admin2_code varchar(80) NULL,
   admin3_code varchar(20) NULL,
   admin4_code varchar(20) NULL,
   population bigint NULL,
   elevation varchar(15) NULL,
   dem varchar(15) NULL,
   timezone varchar(40) NULL,
   modification_date date NULL
 )
 ENGINE = InnoDB
 COLLATE = utf8mb4_unicode_ci;
 
 LOAD DATA INFILE '/media/Storage/geonames_data/allCountries.txt' INTO TABLE geoname CHARACTER SET utf8mb4;
 LOAD DATA INFILE '/media/Storage/geonames_data/null.txt' INTO TABLE geoname CHARACTER SET utf8mb4;
 
 UPDATE geoname SET elevation=NULL WHERE elevation='';
 
 
 CREATE TABLE iso_languagecodes (
   iso_639_3 char(3) DEFAULT NULL,
   iso_639_2 char(10) DEFAULT NULL,
   iso_639_1 char(2) DEFAULT NULL,
   language_name varchar(100) DEFAULT NULL
 ) ENGINE=InnoDB
 COLLATE = utf8mb4_unicode_ci;
 
 LOAD DATA INFILE '/media/Storage/geonames_data/iso-languagecodes.txt' INTO TABLE iso_languagecodes CHARACTER SET utf8mb4 IGNORE 1 LINES;
 
 UPDATE iso_languagecodes SET iso_639_2=NULL WHERE iso_639_2='          ';
 UPDATE iso_languagecodes SET iso_639_1=NULL WHERE iso_639_1='  ';
 
 drop table if exists postalcodes;
 CREATE TABLE postalcodes (
   country_code char(2) DEFAULT NULL,
   postal_code varchar(20) DEFAULT NULL,
   place_name varchar(720) DEFAULT NULL,
   admin_name1 varchar(400) DEFAULT NULL,
   admin_code1 varchar(80) DEFAULT NULL,
   admin_name2 varchar(400) DEFAULT NULL,
   admin_code2 varchar(80) DEFAULT NULL,
   admin_name3 varchar(400) DEFAULT NULL,
   admin_code3 varchar(80) DEFAULT NULL,
   latitude varchar(8) DEFAULT NULL,
   longitude varchar(9) DEFAULT NULL,
   accuracy varchar(1) DEFAULT NULL
 ) ENGINE=InnoDB
 COLLATE = utf8mb4_unicode_ci;
 
 LOAD DATA INFILE '/media/Storage/geonames_data/postalcodes/allCountries.txt' INTO TABLE postalcodes CHARACTER SET utf8mb4;
 
 UPDATE postalcodes SET latitude=NULL where latitude='';
 UPDATE postalcodes SET longitude=NULL where longitude='';
 UPDATE postalcodes SET accuracy=NULL where accuracy='';
 
 
 
 
 
 
 
 
 
 USE geonames;
 
 CREATE TABLE admin1codesascii (
   code varchar(15) NULL,
   name varchar(400),
   nameascii varchar(100),
   geonameid int NULL,
   KEY code (code)
 ) ENGINE = InnoDB
 COLLATE = utf8mb4_unicode_ci;
 
 CREATE TABLE admin2codes (
   code varchar(30) NULL,
   name varchar(400),
   nameascii varchar(100),
   geonameid int(11) NULL,
   KEY code (code)
 ) ENGINE = InnoDB
 COLLATE = utf8mb4_unicode_ci;
 
 LOAD DATA INFILE '/media/Storage/geonames_data/admin1CodesASCII.txt' INTO TABLE admin1codesascii CHARACTER SET utf8mb4;
 LOAD DATA INFILE '/media/Storage/geonames_data/admin2Codes.txt' INTO TABLE admin2codes CHARACTER SET utf8mb4;
 
 
 CREATE TABLE hierarchy (
   parentid int(11) NOT NULL,
   childid int(11) NOT NULL,
   type varchar(50) DEFAULT NULL
 ) ENGINE=InnoDB
 COLLATE = utf8mb4_unicode_ci;
 
 LOAD DATA INFILE '/media/Storage/geonames_data/hierarchy.txt' INTO TABLE hierarchy CHARACTER SET utf8mb4;
 
 
 CREATE TABLE timezones (
   country_code char(2) NULL,
   timezoneid varchar(200) NULL,
   gmt_offset decimal(4,2) NULL,
   dst_offset decimal(4,2) NULL,
   raw_offset decimal(4,2) NULL
 ) ENGINE=InnoDB
 COLLATE = utf8mb4_unicode_ci;
 
 LOAD DATA INFILE '/media/Storage/geonames_data/timeZones.txt' INTO TABLE timezones CHARACTER SET utf8mb4 IGNORE 1 LINES;
 
 
 CREATE TABLE alternate_names (
   alternateNameId INT NOT NULL,
   geonameid INT NULL,
   isolanguage VARCHAR(7) NULL,
   alternate_name VARCHAR(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
   isPreferredName TINYINT NULL,
   isShortName TINYINT NULL,
   isColloquial TINYINT NULL,
   isHistoric TINYINT NULL
 )
 ENGINE = InnoDB
 COLLATE = utf8mb4_unicode_ci;
 INSERT INTO alternate_names SELECT * FROM geonames_import.alternate_names;
 
 
 CREATE TABLE geoname (
   geonameid int NOT NULL,
   name varchar(200) NULL,
   asciiname varchar(200) NULL,
   alternatenames TEXT NULL,
   latitude decimal(7,5) NULL,
   longitude decimal(8,5) NULL,
   feature_class varchar(1) NULL,
   feature_code varchar(10) NULL,
   country_code char(2) NULL,
   cc2 varchar(60) NULL,
   admin1_code varchar(60) NULL,
   admin2_code varchar(80) NULL,
   admin3_code varchar(20) NULL,
   admin4_code varchar(20) NULL,
   population bigint(20) NULL,
   elevation int(11) NULL,
   dem int(11) NULL,
   timezone varchar(40) NULL,
   modification_date date NULL
 )
 ENGINE = InnoDB
 COLLATE = utf8mb4_unicode_ci;
 INSERT INTO geoname SELECT * FROM geonames_import.geoname;
 
 
 CREATE TABLE countryinfo (
   iso char(2) DEFAULT NULL,
   iso3 char(3) DEFAULT NULL,
   iso_numeric int(11) DEFAULT NULL,
   fips varchar(3) DEFAULT NULL,
   name varchar(200) DEFAULT NULL,
   capital varchar(200) DEFAULT NULL,
   areainsqkm bigint(20) DEFAULT NULL,
   population bigint(20) DEFAULT NULL,
   continent char(2) DEFAULT NULL,
   tld char(3) DEFAULT NULL,
   currencycode char(3) DEFAULT NULL,
   currencyname char(20) DEFAULT NULL,
   phone char(20) DEFAULT NULL,
   postalcodeformat varchar(100) DEFAULT NULL,
   postalcoderegex varchar(255) DEFAULT NULL,
   languages varchar(200) DEFAULT NULL,
   geonameid int(11) DEFAULT NULL,
   neighbours varchar(100) DEFAULT NULL,
   equivalentfipscode varchar(10) DEFAULT NULL
 ) ENGINE=InnoDB
 COLLATE = utf8mb4_unicode_ci;
 INSERT INTO countryinfo SELECT * FROM geonames_import.countryinfo;
 
 
 CREATE TABLE iso_languagecodes (
   iso_639_3 char(3) DEFAULT NULL,
   iso_639_2 char(10) DEFAULT NULL,
   iso_639_1 char(2) DEFAULT NULL,
   language_name varchar(100) DEFAULT NULL
 ) ENGINE=InnoDB
 COLLATE = utf8mb4_unicode_ci;
 INSERT INTO iso_languagecodes SELECT * FROM geonames_import.iso_languagecodes;
 
 
 CREATE TABLE featurecodes (
   language char(2) DEFAULT 'bg',
   featurecode varchar(10) DEFAULT NULL,
   desc1 varchar(100) DEFAULT NULL,
   desc2 varchar(500) DEFAULT NULL
 ) ENGINE=InnoDB
 COLLATE = utf8mb4_unicode_ci;
 INSERT INTO featurecodes SELECT * FROM geonames_import.featurecodes;
 
 
 CREATE TABLE postalcodes (
   country_code char(2) DEFAULT NULL,
   postal_code varchar(20) DEFAULT NULL,
   place_name varchar(720) DEFAULT NULL,
   admin_name1 varchar(400) DEFAULT NULL,
   admin_code1 varchar(80) DEFAULT NULL,
   admin_name2 varchar(400) DEFAULT NULL,
   admin_code2 varchar(80) DEFAULT NULL,
   admin_name3 varchar(400) DEFAULT NULL,
   admin_code3 varchar(80) DEFAULT NULL,
   latitude decimal(7,4) DEFAULT NULL,
   longitude decimal(8,4) DEFAULT NULL,
   accuracy tinyint(4) DEFAULT NULL
 ) ENGINE=InnoDB
 COLLATE = utf8mb4_unicode_ci;
 INSERT INTO postalcodes SELECT * FROM geonames_import.postalcodes;
 
 
 DROP DATABASE geonames_import;
 
 
 ALTER TABLE alternate_names
 ADD INDEX PK (alternateNameId ASC),
 ADD INDEX ix_geonameid (geonameid ASC),
 ADD INDEX ix_isolanguage (isolanguage ASC);
 ADD INDEX ix_alternate_name (alternate_name(190) ASC); # need to reduce index to use only part of column values as in InnoDB max index size is 767 bytes (and 190 chars * 4 bytes = 760 bytes)
 
 ALTER TABLE countryinfo 
 ADD INDEX ix_iso (iso ASC),
 ADD INDEX ix_iso3 (iso3 ASC),
 ADD INDEX ix_iso_numeric (iso_numeric ASC),
 ADD INDEX ix_fips (fips ASC),
 ADD INDEX ix_name (name(80) ASC);
 
 ALTER TABLE featurecodes 
 ADD INDEX ix_language (language ASC),
 ADD INDEX ix_featurecode (featurecode ASC);
 
 ALTER TABLE geoname 
 ADD INDEX PK (geonameid ASC),
 ADD INDEX ix_name (name(80) ASC),
 ADD INDEX ix_asciiname (asciiname(80) ASC),
 ADD INDEX ix_feature_class (feature_class ASC),
 ADD INDEX ix_feature_code (feature_code ASC),
 ADD INDEX ix_country_code (country_code ASC);
 
 ALTER TABLE hierarchy 
 ADD INDEX ix_parentid (parentid ASC),
 ADD INDEX ix_childid (childid ASC);
 
 ALTER TABLE iso_languagecodes 
 ADD INDEX ix_iso_639_3 (iso_639_3 ASC),
 ADD INDEX ix_iso_639_2 (iso_639_2 ASC),
 ADD INDEX ix_iso_639_1 (iso_639_1 ASC);
 
 ALTER TABLE timezones 
 ADD INDEX ix_country_code (country_code ASC);
 
 ALTER TABLE postalcodes 
 ADD INDEX ix_country_code (country_code ASC),
 ADD INDEX ix_postal_code (postal_code ASC);
