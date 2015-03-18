-- Create schema and user
CREATE SCHEMA `ngavatar` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;
CREATE USER `ng`@`%` IDENTIFIED BY 'F6r3QTq4nB';
GRANT INSERT, DELETE, UPDATE, SELECT ON `ngavatar`.* TO `ng`@`%`;
USE `ngavatar`;


-- Create account table
CREATE TABLE `account` (
  `uid` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'user id',
  `username` char(45) NOT NULL COMMENT 'username to login with',
  `passwd_hash` char(40) NOT NULL COMMENT 'sha1 hash of the password and salt',
  `salt` char(5) NOT NULL COMMENT 'random string for generating password hash',
  `register_time` datetime NOT NULL COMMENT 'time of creating this account',
  `login_time` datetime DEFAULT NULL COMMENT 'time of latest login',
  `state` tinyint(4) unsigned NOT NULL DEFAULT '0' COMMENT 'state of this account, 0 - normal, 1 - banned, 2 - frozen, 3 - not verified',
  PRIMARY KEY (`uid`),
  UNIQUE KEY `username_UNIQUE` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;


-- Create avatar table
CREATE TABLE `avatar` (
  `aid` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'id of this avatar',
  `owner_uid` bigint(20) unsigned NOT NULL COMMENT 'id of owner of this avatar',
  `file_path` varchar(255) NOT NULL COMMENT 'path to the file',
  `add_time` varchar(45) NOT NULL COMMENT 'time of adding this avatar',
  PRIMARY KEY (`aid`),
  UNIQUE KEY `file_path_UNIQUE` (`file_path`),
  KEY `fk_avatar_owner_uid_idx` (`owner_uid`),
  CONSTRAINT `fk_avatar_owner_uid` FOREIGN KEY (`owner_uid`) REFERENCES `account` (`uid`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;


-- Create email table
CREATE TABLE `email` (
  `emid` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'id of email',
  `email` varchar(45) NOT NULL COMMENT 'email address',
  `owner_uid` bigint(20) unsigned NOT NULL COMMENT 'id of owner of this email address',
  `email_hash` char(40) NOT NULL COMMENT 'sha1 hash of the email address',
  `avatar_id` bigint(20) unsigned DEFAULT NULL COMMENT 'id of avatar that this email is bound with',
  `add_time` datetime NOT NULL COMMENT 'time of adding this email',
  PRIMARY KEY (`emid`),
  UNIQUE KEY `email_UNIQUE` (`email`),
  UNIQUE KEY `email_hash_UNIQUE` (`email_hash`),
  KEY `fk_email_owner_uid_idx` (`owner_uid`),
  KEY `fk_email_avatar_id_idx` (`avatar_id`),
  CONSTRAINT `fk_email_avatar_id` FOREIGN KEY (`avatar_id`) REFERENCES `avatar` (`aid`) ON DELETE SET NULL ON UPDATE NO ACTION,
  CONSTRAINT `fk_email_owner_uid` FOREIGN KEY (`owner_uid`) REFERENCES `account` (`uid`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;


-- Create session table
CREATE TABLE `session` (
  `sid` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'id of this session',
  `session_key` varchar(255) NOT NULL COMMENT 'key of the session',
  `data` text NOT NULL COMMENT 'data of the session',
  `expire_time` datetime NOT NULL COMMENT 'expiring time of this session',
  `creator_ip` varchar(45) NOT NULL COMMENT 'ip of the client that creates this session',
  PRIMARY KEY (`sid`),
  UNIQUE KEY `session_key_UNIQUE` (`session_key`)
) ENGINE=InnoDB AUTO_INCREMENT=58 DEFAULT CHARSET=utf8;
