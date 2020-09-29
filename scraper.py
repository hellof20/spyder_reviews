#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import pandas as pd
import sys, json, time
import pymysql
import boto3
import os
from sqlalchemy import create_engine
from warnings import filterwarnings
from google_play_scraper import Sort, reviews, app, reviews_all
from concurrent.futures import ThreadPoolExecutor
filterwarnings("ignore", category=pymysql.Warning)
import spacy

error_log = "error.log"

def main():
    class App(object):
        def __init__(self, appname, platform, country, appid):
            self.appname = appname
            self.platform = platform
            self.country = country
            self.appid = appid

        def appinfo(self):
            if self.platform == 'AppStore':
                headers = {
                    "User-Agent": "iTunes/11.0 (Windows; Microsoft Windows 7 Business Edition Service Pack 1 (Build 7601)) AppleWebKit/536.27.1"}
                ratingurl = 'https://itunes.apple.com/' + str(self.country) + '/customer-reviews/id' + str(
                    self.appid) + '?dataOnly=true&displayable-kind=11'
                ratingdata = {}
                ratingparams = urllib.parse.urlencode(ratingdata).encode(encoding='UTF8')
                ratingrequest = urllib.request.Request(ratingurl, ratingparams, headers)
                ratingresponse = urllib.request.urlopen(ratingrequest)
                ratingjson = json.loads(ratingresponse.read().decode())
                totalNumberOfReviews = ratingjson['totalNumberOfReviews']
                ratingname = ['appname', 'country', 'platform', 'date', 'totalNumberOfReviews', 'ratingAverage',
                              'ratingCount', '1stars', '2stars', '3stars', '4starts', '5stars']
                rating_result_list = []
                rating_result_list.append(
                    [self.appname, self.country, self.platform, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                     ratingjson['totalNumberOfReviews'], ratingjson['ratingAverage'], ratingjson['ratingCount'],
                     ratingjson['ratingCountList'][0], ratingjson['ratingCountList'][1],
                     ratingjson['ratingCountList'][2], ratingjson['ratingCountList'][3],
                     ratingjson['ratingCountList'][4]])
                ratingdf = pd.DataFrame(columns=ratingname, data=rating_result_list)
                return ratingdf
            if self.platform == 'GooglePlay':
                result = app(
                    self.appid,
                    country=self.country)
                totalNumberOfReviews = result['reviews']
                ratingname = ['appname', 'country', 'platform', 'date', 'totalNumberOfReviews', 'ratingAverage',
                              'ratingCount', '1stars', '2stars', '3stars', '4starts', '5stars']
                rating_result_list = []
                rating_result_list.append(
                    [self.appname, self.country, self.platform, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                     result['reviews'], result['score'], result['ratings'], result['histogram'][0],
                     result['histogram'][1], result['histogram'][2], result['histogram'][3], result['histogram'][4]])
                ratingdf = pd.DataFrame(columns=ratingname, data=rating_result_list)
                return ratingdf
            if self.platform == 'TapTap':
                pass

        def reviews(self):
            if self.platform == 'AppStore':
                headers = {
                    "User-Agent": "iTunes/11.0 (Windows; Microsoft Windows 7 Business Edition Service Pack 1 (Build 7601)) AppleWebKit/536.27.1"}
                url = 'https://itunes.apple.com/WebObjects/MZStore.woa/wa/userReviewsRow?cc=' + str(
                    self.country) + '&id=' + str(
                    self.appid) + '&displayable-kind=11&startIndex=0&endIndex=100000&sort=0&appVersion=all'
                data = {}
                params = urllib.parse.urlencode(data).encode(encoding='UTF8')
                request = urllib.request.Request(url, params, headers)
                response = urllib.request.urlopen(request)
                myjson = json.loads(response.read().decode())
                reviews = myjson['userReviewList']
                result_list = []
                # print("%s在%s总计%s行" % (self.appname, self.platform, len(reviews)))
                for i in range(len(reviews)):
                    values = reviews[i]
                    result_list.append(
                        [values['userReviewId'], self.appname, self.country, self.platform, values['date'],
                         values['name'], values['title'], values['body'], values['rating']])
                name = ['id', 'appname', 'country', 'platform', 'date', 'name', 'title', 'content', 'rating']
                reviews_df = pd.DataFrame(columns=name, data=result_list)
                return reviews_df

            if self.platform == 'GooglePlay':
                reviews_result = reviews_all(
                    self.appid,
                    country=self.country,
                    sort=Sort.MOST_RELEVANT)
                reviews_result_list = []
                reviews_name = ['id', 'appname', 'country', 'platform', 'date', 'name', 'title', 'content', 'rating']
                # print("%s在%s总计%d行" % (self.appname, self.platform, len(reviews_result)))
                for i in range(len(reviews_result)):
                    values = reviews_result[i]
                    reviews_result_list.append(
                        [values['reviewId'], self.appname, self.country, self.platform, values['at'],
                         values['userName'], '', values['content'], values['score']])
                reviews_df = pd.DataFrame(columns=reviews_name, data=reviews_result_list)
                return reviews_df

            if self.paltform == 'TapTap':
                pass

    def write_mysql(connect, dataframe, tablename):
        if tablename == 'customer_reviews_temp':
            dataframe.to_sql(tablename, connect, if_exists='replace', index=False)
        else:
            dataframe.to_sql(tablename, connect, if_exists='append', index=False)
    
    # logs为 list
    def logger_error(logs):
        write_logs = [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())]
        write_logs.extend(logs)
        f = open(error_log, 'a')
        f.write("\t".join(write_logs) + '\n')
        f.close()

    ennlp = spacy.load("en_core_web_sm")
    jpnlp = spacy.load("ja_core_news_sm")
    zhnlp = spacy.load("zh_core_web_sm")

    def do_spacy(df,line_num,nlp):
        content = df.iloc[line_num, 7]
        date = str(df.iloc[line_num, 4])
        rating = str(df.iloc[line_num, 8])
        if content == '':
            keyword_list = []
            nounphrases = []
            verbsphrases = []
            adjphrases = []
        else:
            doc = nlp(content)
            # nounphrases = [chunk.text for chunk in doc.noun_chunks]
            nounphrases = [token.lemma_ for token in doc if token.pos_ == "NOUN"]
            verbsphrases = [token.lemma_ for token in doc if token.pos_ == "VERB"]
            adjphrases = [token.lemma_ for token in doc if token.pos_ == "ADJ"]
            keyword_list = list(set(nounphrases + verbsphrases + adjphrases))
        df.loc[line_num, "noun"] = "|".join(nounphrases)
        df.loc[line_num, "verb"] = "|".join(verbsphrases)
        df.loc[line_num, "adj"] = "|".join(adjphrases)
        df.loc[line_num, "keyword"] = "|".join(keyword_list)        
        df.loc[line_num, "entity"] = ""
        df.loc[line_num, "sentiment"] = ""
        df.loc[line_num, "date"] = date
        df.loc[line_num, "rating"] = rating
        line_dict = df.loc[line_num].to_dict()
        line_df = pd.DataFrame.from_dict(line_dict, orient='index').T
        line_df.to_sql('customer_reviews', connect, index=False, if_exists='append')

    rdshost = os.environ.get('rdshost')
    rdsuser = os.environ.get('rdsuser')
    rdspassword = os.environ.get('rdspassword')
    database = os.environ.get('rdsdatabase')
    # connect = create_engine('mysql+pymysql://' + rdsuser + ':' + rdspassword + '@' + rdshost + ':3306/' + database + '?charset=utf8')
    connect = create_engine('mysql://' + rdsuser + ':' + rdspassword + '@' + rdshost + '?charset=utf8')
    
    #创建数据库和表
    dbs = connect.execute("show databases;")
    print(dbs)

    sql = """
CREATE DATABASE spyder DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
DROP TABLE IF EXISTS customer_ratings;
create table customer_ratings(
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
    createtime DATETIME default CURRENT_TIMESTAMP,
    updatetime DATETIME default CURRENT_TIMESTAMP,
    PRIMARY KEY ( id ))
    ENGINE=InnoDB  DEFAULT CHARSET=utf8 ;
"""

    #处理app.csv文件
    s3 = boto3.resource('s3')
    appbucket = os.environ.get('appbucket')
    appkey = os.environ.get('appkey')
    s3.meta.client.download_file(appbucket, appkey, 'app.csv')
    game_df = pd.read_csv('app.csv')
    game_num = game_df.shape[0]
    for i in range(0,game_num):
        # start_init = time.time()
        game = App(game_df.iloc[i,0],game_df.iloc[i,1],game_df.iloc[i,2],game_df.iloc[i,3])
        # end_init = time.time()
        # print("init spend %d ms" % int((end_init - start_init)*1000))
        start_write_rating = time.time()
        write_mysql(connect, game.appinfo(), 'customer_ratings')
        end_write_rating = time.time()
        print("write_rating spend %d ms" % int((end_write_rating - start_write_rating)*1000))
        start_write_reviews = time.time()
        write_mysql(connect, game.reviews(), 'customer_reviews_temp')
        end_write_reviews = time.time()
        print("write_reviews spend %d ms" % int((end_write_reviews - start_write_reviews)*1000))
        ##comprehend对评论数据进行处理部分
        sql_cmd = "select id,appname,country,platform,date,name,title,content,rating from customer_reviews_temp where id not in (select id from customer_reviews);"
        df = pd.read_sql(sql=sql_cmd, con=connect)
        num = df.shape[0]
        print("begin process ... ")
        if game_df.iloc[i,2] == 'us':
            for line_num in range(0, num):
                do_spacy(df, line_num, ennlp)
        if game_df.iloc[i,2] == 'jp':
            for line_num in range(0, num):
                do_spacy(df, line_num, jpnlp)
        if game_df.iloc[i,2] == 'cn':
            for line_num in range(0, num):
                do_spacy(df, line_num, zhnlp)
        print('num of %d reviews processed' % num)

if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
    spend = (end - start)
    print("spend %s s" % spend)