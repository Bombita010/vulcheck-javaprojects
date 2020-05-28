create database vulnerable_apis;

use vulnerable_apis;

CREATE TABLE apis (
  cve_no varchar(900) NOT NULL,
  cve_level varchar(900) NOT NULL,
  jar_name varchar(900),
  git_repository varchar(900) NOT NULL,
  commitid varchar(900) NOT NULL,
  file_name varchar(900) NOT NULL,
  class_name varchar(900) NOT NULL,
  method_name varchar(900) NOT NULL,
  isPublic varchar(900) NOT NULL,
  vulnerable_line varchar(900) NOT NULL,
  file_longname varchar(900) NOT NULL,
  method_longname varchar(900) NOT NULL,
);

CREATE TABLE vuls (
  cve_name varchar(900) NOT NULL,
  cnnvd_no varchar(900) NOT NULL,
  cnnvd_level varchar(900) NOT NULL,
  cve_no varchar(900) NOT NULL,
  catag varchar(900) NOT NULL,
  threat_cata varchar(900) NOT NULL,
  reference varchar(900) NOT NULL,
  jar_name varchar(900) NOT NULL,
  git_repository varchar(900) NOT NULL,
);

select count(*) from apis;
