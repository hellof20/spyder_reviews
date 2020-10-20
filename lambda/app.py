import sys
import logging
import os
import pymysql
import cfn_resource

helper = cfn_resource.Resource()


rds_host  = os.environ['db_endpoint']
name = os.environ['db_username']
password = os.environ['db_password']
db_name = os.environ['db_name']
logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
except pymysql.MySQLError as e:
    logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
    logger.error(e)
    sys.exit()

logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

@helper.create
def handler(event, context):
    with conn.cursor() as cur:
        cur.execute("create table customer_ratings(appname varchar(128),country varchar(16),platform varchar(16),date DATETIME,totalNumberOfReviews int,ratingAverage double,ratingCount int,1stars int,2stars int,3stars int,4starts int,5stars int) ENGINE=InnoDB  DEFAULT CHARSET=utf8;")
        cur.execute("create table customer_reviews_temp(id VARCHAR(128),appname VARCHAR(128),country VARCHAR(16),platform varchar(16),date DATETIME,name VARCHAR(128),title TEXT,content TEXT,rating smallint,PRIMARY KEY ( id )) ENGINE=InnoDB  DEFAULT CHARSET=utf8;")
        cur.execute("create table customer_reviews(id VARCHAR(128),appname VARCHAR(128),country VARCHAR(16),platform varchar(16),date DATETIME,name VARCHAR(128),title TEXT,content TEXT,rating smallint,sentiment VARCHAR(500),keyword VARCHAR(1000),noun VARCHAR(500),adj VARCHAR(500),verb VARCHAR(500),entity VARCHAR(500),createtime DATETIME default CURRENT_TIMESTAMP,updatetime DATETIME default CURRENT_TIMESTAMP,PRIMARY KEY ( id ))ENGINE=InnoDB  DEFAULT CHARSET=utf8 ;")
        conn.commit()
    conn.commit()

    print("Added MySQL tables")
    return {"PhysicalResourceId": "arn:aws:fake:myID"}
