#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import pandas as pd 
import json,time
import pymysql
from sqlalchemy import create_engine
from warnings import filterwarnings
from google_play_scraper import Sort, reviews, app, reviews_all
filterwarnings("ignore",category=pymysql.Warning)
import boto3


def main():
    class App(object):
        def __init__(self, appname, platform, country, appid):
            self.appname = appname
            self.platform = platform
            self.country = country
            self.appid = appid

        def appinfo(self):
            if self.platform == 'AppStore':
                headers = {"User-Agent": "iTunes/11.0 (Windows; Microsoft Windows 7 Business Edition Service Pack 1 (Build 7601)) AppleWebKit/536.27.1"}
                ratingurl = 'https://itunes.apple.com/'+ str(self.country) +'/customer-reviews/id'+ str(self.appid) +'?dataOnly=true&displayable-kind=11'
                ratingdata = {}
                ratingparams = urllib.parse.urlencode(ratingdata).encode(encoding='UTF8') 
                ratingrequest = urllib.request.Request(ratingurl,ratingparams,headers)
                ratingresponse = urllib.request.urlopen(ratingrequest)
                ratingjson = json.loads(ratingresponse.read().decode())
                totalNumberOfReviews = ratingjson['totalNumberOfReviews']
                ratingname = ['appname','country','platform','date','totalNumberOfReviews','ratingAverage','ratingCount','1stars','2stars','3stars','4starts','5stars']
                rating_result_list = []
                rating_result_list.append( [ self.appname,self.country,self.platform,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), ratingjson['totalNumberOfReviews'],ratingjson['ratingAverage'],ratingjson['ratingCount'],ratingjson['ratingCountList'][0],ratingjson['ratingCountList'][1],ratingjson['ratingCountList'][2],ratingjson['ratingCountList'][3],ratingjson['ratingCountList'][4] ])
                ratingdf = pd.DataFrame(columns=ratingname, data=rating_result_list)
                return ratingdf
            if self.platform == 'GooglePlay':
                result = app(
                    self.appid,
                    country=self.country)
                totalNumberOfReviews = result['reviews']
                ratingname = ['appname','country','platform','date','totalNumberOfReviews','ratingAverage','ratingCount','1stars','2stars','3stars','4starts','5stars']
                rating_result_list = []
                rating_result_list.append( [ self.appname,self.country,self.platform,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), result['reviews'],result['score'],result['ratings'],result['histogram'][0],result['histogram'][1],result['histogram'][2],result['histogram'][3],result['histogram'][4] ])
                ratingdf = pd.DataFrame(columns=ratingname, data=rating_result_list)
                return ratingdf

        def reviews(self):
            if self.platform == 'AppStore':
                headers = {"User-Agent": "iTunes/11.0 (Windows; Microsoft Windows 7 Business Edition Service Pack 1 (Build 7601)) AppleWebKit/536.27.1"}
                url = 'https://itunes.apple.com/WebObjects/MZStore.woa/wa/userReviewsRow?cc=' + str(self.country) + '&id=' + str(self.appid) + '&displayable-kind=11&startIndex=0&endIndex=100000&sort=0&appVersion=all'
                data = {}
                params = urllib.parse.urlencode(data).encode(encoding='UTF8')
                request = urllib.request.Request(url,params,headers)
                response = urllib.request.urlopen(request)
                myjson = json.loads(response.read().decode())
                reviews = myjson['userReviewList']
                result_list = []
                for i in range(len(reviews)):
                    values = reviews[i]
                    result_list.append([ values['userReviewId'],self.appname, self.country, self.platform, values['date'], values['name'], values['title'], values['body'], values['rating'] ])
                name = ['id','appname','country','platform','date', 'name', 'title', 'content', 'rating']
                reviews_df = pd.DataFrame(columns=name, data=result_list)
                return reviews_df

            if self.platform == 'GooglePlay':
                reviews_result = reviews_all(
                    self.appid,
                    country=self.country,
                    sort=Sort.MOST_RELEVANT)
                reviews_result_list = []
                reviews_name = ['id','appname','country','platform','date', 'name', 'title', 'content', 'rating']
                for i in range(len(reviews_result)):
                    values = reviews_result[i]
                    reviews_result_list.append([ values['reviewId'],self.appname, self.country, self.platform, values['at'], values['userName'], '', values['content'], values['score'] ])
                reviews_df = pd.DataFrame(columns=reviews_name, data=reviews_result_list)
                return reviews_df

    rdshost = 'spyder-customer-reviews.cdagscjv6mu0.ap-southeast-1.rds.amazonaws.com'
    rdsuser = 'admin'
    rdspassword = 'Pjy#0618'
    database = 'spyder'
    Arknights_AppStore_us = App('Arknights','AppStore','us','1464872022')
    Arknights_AppStore_jp = App('Arknights','AppStore','jp','1478990007')
    AzurLane_AppStore_us = App('AzurLane','AppStore','us','1411126549')
    AzurLane_AppStore_jp = App('AzurLane','AppStore','jp','1242186587')
    Arknights_GooglePlay_jp = App('Arknights','GooglePlay','jp','com.YoStarJP.Arknights')
    Arknights_GooglePlay_us = App('Arknights','GooglePlay','us','com.YoStarEN.Arknights')
    AzurLane_GooglePlay_jp = App('AzurLane','GooglePlay','jp','com.YoStarJP.AzurLane')
    AzurLane_GooglePlay_us = App('AzurLane','GooglePlay','us','com.YoStarEN.AzurLane')

    def truncate_reviews():
        conn = pymysql.connect(host=rdshost,user=rdsuser,password=rdspassword,database=database,charset="utf8")
        cursor = conn.cursor()
        cursor.execute('truncate table customer_reviews')
        conn.commit()

    connect = create_engine('mysql+pymysql://'+ rdsuser +':'+ rdspassword +'@' + rdshost +':3306/'+ database +'?charset=utf8')

    def write_mysql(dataframe,tablename):
        dataframe.to_sql(tablename, connect, if_exists='append', index=False)

    truncate_reviews()

    write_mysql(Arknights_AppStore_us.appinfo(),'customer_ratings')
    write_mysql(Arknights_AppStore_jp.appinfo(),'customer_ratings')
    write_mysql(Arknights_GooglePlay_jp.appinfo(),'customer_ratings')
    write_mysql(Arknights_GooglePlay_us.appinfo(),'customer_ratings')
    
    write_mysql(AzurLane_AppStore_us.appinfo(),'customer_ratings')
    write_mysql(AzurLane_AppStore_jp.appinfo(),'customer_ratings')
    write_mysql(AzurLane_GooglePlay_jp.appinfo(),'customer_ratings')
    write_mysql(AzurLane_GooglePlay_us.appinfo(),'customer_ratings')

    write_mysql(Arknights_AppStore_us.reviews(),'customer_reviews')
    write_mysql(Arknights_AppStore_jp.reviews(),'customer_reviews')
    write_mysql(Arknights_GooglePlay_us.reviews(),'customer_reviews')
    write_mysql(Arknights_GooglePlay_jp.reviews(),'customer_reviews')

    write_mysql(AzurLane_AppStore_us.reviews(),'customer_reviews')
    write_mysql(AzurLane_AppStore_jp.reviews(),'customer_reviews')
    write_mysql(AzurLane_GooglePlay_us.reviews(),'customer_reviews')
    write_mysql(AzurLane_GooglePlay_jp.reviews(),'customer_reviews')

    ##调用comprehend对评论数据进行处理
    comprehend = boto3.client('comprehend', region_name='us-east-1')
    sql_cmd = "select id,appname,country,platform,date,name,title,content,rating from customer_reviews where id not in (select id from customer_reviews_result) limit 10;"
    df = pd.read_sql(sql=sql_cmd, con=connect)
    num = df.shape[0]
    print(num)
    result = pd.DataFrame(columns=['id','appname','country','platform','date','name','title','content','rating','typeof','senti_result','keyword','entity','entity_result','keyword_result','positive','negative'])
    for lines in range(0,num):
        try:
            txt = df.iloc[lines,0]
            appname=df.iloc[lines,1]
            country =df.iloc[lines,2]
            platform=df.iloc[lines,3]
            if len(txt)==0:
                pass
            else:
                language_code = comprehend.detect_dominant_language(Text=txt)
                code = language_code['Languages'][0]['LanguageCode']
                if code in ['hi', 'de', 'zh-TW', 'ko', 'pt', 'en', 'it', 'fr', 'zh', 'es', 'ar','ja']:
                    sentiments = comprehend.detect_sentiment(Text=txt, LanguageCode=code)
                    neutral = sentiments ['SentimentScore']["Neutral"]
                    positive = sentiments["SentimentScore"]["Positive"]
                    negative = sentiments["SentimentScore"]["Negative"]
                    data_dict = {'Neutral': neutral, 'Positive': positive, 'Negative': negative}
                    typeof = max(data_dict, key=data_dict.get)
                    result.loc[lines,"senti_result"] = str(sentiments)
                    result.loc[lines,"positive"] = str(positive)
                    result.loc[lines,"negative"] = str(negative)
                    result.loc[lines,"content"] =txt
                    result.loc[lines,"appname"] =appname
                    result.loc[lines,"country"] =country
                    result.loc[lines,"platform"] =platform
                    phrases = comprehend.detect_key_phrases(Text=txt, LanguageCode=code)
                    splited=str(phrases['KeyPhrases']).decode('unicode_escape')
                    keylist=phrases['KeyPhrases']
                    keyword_result_list=[]
                    entity_result_list=[]
                    for key in keylist:
                        the_key_word=key['Text']
                        keyword_result_list.append(the_key_word)
                    result.loc[lines,"keyword_result"] = str(keyword_result_list).decode('unicode_escape')
                    keyword=splited
                    result.loc[lines,"keyword"] = str(keyword)
                    entities = comprehend.detect_entities(Text=txt, LanguageCode=code)
                    entity="entity:"+ str(entities['Entities']).decode('unicode_escape')   
                    entitylist=entities['Entities']
                    for entity in entitylist:
                        the_entity_word=key['Text']
                        entity_result_list.append(the_entity_word)
                    result.loc[lines,"entity_result"] = str(entity_result_list).decode('unicode_escape')
                    result.loc[lines,"entity"] = str(entity)

                    if data_dict[typeof] <0.56:
                        typeof_str='slightly'+typeof+" "+str(data_dict[typeof])
                        result.loc[lines,"typeof"] = typeof_str

                    if data_dict[typeof] >0.71:
                        typeof_str='strong'+typeof+" "+str(data_dict[typeof])
                        result.loc[lines,"typeof"] = typeof_str
                    else:
                        typeof_str="middle"+typeof+" "+str(data_dict[typeof])
                        result.loc[lines,"typeof"] = typeof_str
        except Exception as e:
            pass
        continue
print("completed")
result.to_sql('comprehend_result', engine, index=False, if_exists='append')
print("inserted")


if __name__ == '__main__':
    main()
