CREATE DATABASE spyder DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

DROP TABLE IF EXISTS customer_ratings;
create table customer_ratings(
    appname varchar(128),
    country varchar(16),
    platform varchar(16),
    date datetime,
    totalNumberOfReviews int,
    ratingAverage double,
    ratingCount int,
    1stars int,
    2stars int,
    3stars int,
    4starts int,
    5stars int)
    ENGINE=InnoDB  DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS customer_reviews;
create table customer_reviews(
    id VARCHAR(128),
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

DROP TABLE IF EXISTS customer_reviews_result;
create table customer_reviews_result(
    id VARCHAR(128),
    appname VARCHAR(128),
    country VARCHAR(16),
    platform varchar(16),
    date DATETIME,
    name VARCHAR(128),
    title TEXT,
    content TEXT,
    rating smallint,
    typeof VARCHAR(500),
    senti_result VARCHAR(500),
    keyword VARCHAR(1000),
    entity VARCHAR(500),
    entity_result VARCHAR(500),
    keyword_result VARCHAR(500),
    positive VARCHAR(500),
    negative VARCHAR(500),
    PRIMARY KEY ( id ))
    ENGINE=InnoDB  DEFAULT CHARSET=utf8 ;