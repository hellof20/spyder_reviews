CREATE DATABASE reviews DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

DROP TABLE IF EXISTS customer_ratings;
create table customer_ratings(
    appid VARCHAR(128),
    appname varchar(128),
    country varchar(16),
    platform varchar(16),
    date DATETIME,
    totalNumberOfReviews int,
    ratingAverage double,
    ratingCount int,
    1stars int,
    2stars int,
    3stars int,
    4starts int,
    5stars int)
    ENGINE=InnoDB  DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS customer_reviews_temp;
create table customer_reviews_temp(
    id VARCHAR(128),
    appid VARCHAR(128),
    appname VARCHAR(128),
    country VARCHAR(16),
    platform varchar(16),
    date DATETIME,
    name VARCHAR(128),
    title TEXT,
    content TEXT,
    rating smallint,
    PRIMARY KEY ( id )) 
    ENGINE=InnoDB  DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS customer_reviews;
create table customer_reviews(
    id VARCHAR(128),
    appid VARCHAR(128),    
    appname VARCHAR(128),
    country VARCHAR(16),
    platform varchar(16),
    date DATETIME,
    name VARCHAR(128),
    title TEXT,
    content TEXT,
    rating smallint,
    sentiment VARCHAR(500),
    keyword VARCHAR(1000),
    noun VARCHAR(500),
    adj VARCHAR(500),
    verb VARCHAR(500),
    entity VARCHAR(500),
    lang VARCHAR(16),
    content_cn TEXT,
    createtime DATETIME default CURRENT_TIMESTAMP,
    updatetime DATETIME default CURRENT_TIMESTAMP,
    PRIMARY KEY ( id ))
    ENGINE=InnoDB  DEFAULT CHARSET=utf8 ;