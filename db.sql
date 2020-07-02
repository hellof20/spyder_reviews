DROP TABLE IF EXISTS customer_ratings;
create table customer_ratings(appid varchar(16),country varchar(16),platform varchar(16),date datetime,totalNumberOfReviews int,ratingAverage double,ratingCount int,1stars int,2stars int,3stars int,4starts int,5stars int);

DROP TABLE IF EXISTS customer_reviews;
create table customer_reviews(appid VARCHAR(16),country VARCHAR(16),platform varchar(16),date DATETIME,name VARCHAR(128),title TEXT,content TEXT,rating smallint);