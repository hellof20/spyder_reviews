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
    print('scraperd appinfo')
    write_mysql(Arknights_AppStore_us.reviews(),'customer_reviews')
    write_mysql(Arknights_AppStore_jp.reviews(),'customer_reviews')
    write_mysql(Arknights_GooglePlay_us.reviews(),'customer_reviews')
    write_mysql(Arknights_GooglePlay_jp.reviews(),'customer_reviews')

    write_mysql(AzurLane_AppStore_us.reviews(),'customer_reviews')
    write_mysql(AzurLane_AppStore_jp.reviews(),'customer_reviews')
    write_mysql(AzurLane_GooglePlay_us.reviews(),'customer_reviews')
    write_mysql(AzurLane_GooglePlay_jp.reviews(),'customer_reviews')
    print('scraperd reviews')
    ##调用comprehend对评论数据进行处理
    comprehend = boto3.client('comprehend', region_name='us-east-1')
    sql_cmd = "select id,appname,country,platform,date,name,title,content,rating from customer_reviews where id not in (select id from customer_reviews_result);"
    df = pd.read_sql(sql=sql_cmd, con=connect)
    num = df.shape[0]
    for line_num in range(0,num):
        content = df.iloc[line_num,7]
        date = str(df.iloc[line_num,4])
        rating = str(df.iloc[line_num,8])
        if len(content) > 0:
            language_code = comprehend.detect_dominant_language(Text=content)
            code = language_code['Languages'][0]['LanguageCode']
            if code in ['hi', 'de', 'zh-TW', 'ko', 'pt', 'en', 'it', 'fr', 'zh', 'es', 'ar','ja']:
                sentiments = comprehend.detect_sentiment(Text=content, LanguageCode=code)
                phrases = comprehend.detect_key_phrases(Text=content, LanguageCode=code)
                entities = comprehend.detect_entities(Text=content, LanguageCode=code)
                entities_list = []
                keyword_list = []
                for i in phrases['KeyPhrases']:
                    keyword_list.append(i['Text'])
                for i in entities['Entities']:
                    entities_list.append(i['Text'])
                df.loc[line_num,"keyword_result"] = str(keyword_list)
                df.loc[line_num,"entity_result"] = str(entities_list)
                df.loc[line_num,"senti_result"] = str(sentiments['Sentiment'])
                df.loc[line_num,"date"] = date
                df.loc[line_num,"rating"] = rating
                line_dict = df.loc[line_num].to_dict()
                line_df = pd.DataFrame.from_dict(line_dict,orient='index').T
                line_df.to_sql('customer_reviews_result', connect, index=False, if_exists='append')
                print('processed %d rows' % (line_num + 1))
    print('processed %d rows, completed' % num)

if __name__ == '__main__':
    main()
