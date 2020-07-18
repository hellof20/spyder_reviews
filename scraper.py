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
                    self.appname,
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
                    result_list.append([ self.appname, self.country, self.platform, values['date'], values['name'], values['title'], values['body'], values['rating'] ])
                name = ['appname','country','platform','date', 'name', 'title', 'content', 'rating']
                reviews_df = pd.DataFrame(columns=name, data=result_list)
                return reviews_df

            if self.platform == 'GooglePlay':
                reviews_result = reviews_all(
                    self.appname,
                    country=self.country,
                    sort=Sort.MOST_RELEVANT)
                reviews_result_list = []
                reviews_name = ['appname','country','platform','date', 'name', 'title', 'content', 'rating']
                for i in range(len(reviews_result)):
                    values = reviews_result[i]
                    reviews_result_list.append([ self.appname, self.country, self.platform, values['at'], values['userName'], '', values['content'], values['score'] ])
                reviews_df = pd.DataFrame(columns=reviews_name, data=reviews_result_list)
                return reviews_df


    Arknights_AppStore_us = App('Arknights','AppStore','us','1464872022')
    Arknights_AppStore_jp = App('Arknights','AppStore','jp','1478990007')
    AzurLane_AppStore_us = App('AzurLane','AppStore','us','1411126549')
    AzurLane_AppStore_jp = App('AzurLane','AppStore','jp','1242186587')
    Arknights_GooglePlay_jp = App('com.YoStarJP.Arknights','GooglePlay','jp','')
    Arknights_GooglePlay_us = App('com.YoStarEN.Arknights','GooglePlay','us','')
    AzurLane_GooglePlay_jp = App('com.YoStarJP.AzurLane','GooglePlay','jp','')
    AzurLane_GooglePlay_us = App('com.YoStarEN.AzurLane','GooglePlay','us','')

    def truncate_reviews():
        conn = pymysql.connect(host="spyder-customer-reviews.cdagscjv6mu0.ap-southeast-1.rds.amazonaws.com",user="admin",password="Pjy#0618",database="spyder",charset="utf8")
        cursor = conn.cursor()
        cursor.execute('truncate table customer_reviews')

    def write_mysql(dataframe,tablename):
        connect = create_engine('mysql+pymysql://admin:Pjy#0618@spyder-customer-reviews.cdagscjv6mu0.ap-southeast-1.rds.amazonaws.com:3306/spyder?charset=utf8')
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

if __name__ == '__main__':
    main()