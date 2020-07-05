#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import pandas as pd 
import json,time
import pymysql
from sqlalchemy import create_engine
from warnings import filterwarnings
filterwarnings("ignore",category=pymysql.Warning)

def main():
    #appid = input("请输入应用id号：")
    #reviews_num = input("获取评论数量：")
    #country = input("国家代号：")
    appname = 'AzurLane'
    platform = 'ios'
    appid = '1242186587'
    country = 'jp'

    connect = create_engine('mysql+pymysql://admin:Pjy#0618@spyder-customer-reviews.cdagscjv6mu0.ap-southeast-1.rds.amazonaws.com:3306/spyder?charset=utf8')
    previousReviews = connect.execute('select max(totalNumberOfReviews) from customer_ratings where appid ="'+ appid +'"')
    previousReviewsNum = previousReviews.fetchall()[0][0]
    if previousReviewsNum is None:
        previousReviewsNum = 0

    headers = {"User-Agent": "iTunes/11.0 (Windows; Microsoft Windows 7 Business Edition Service Pack 1 (Build 7601)) AppleWebKit/536.27.1"}
    ratingurl = 'https://itunes.apple.com/'+ str(country) +'/customer-reviews/id'+ str(appid) +'?dataOnly=true&displayable-kind=11'
    ratingdata = {}
    ratingparams = urllib.parse.urlencode(ratingdata).encode(encoding='UTF8') 
    ratingrequest = urllib.request.Request(ratingurl,ratingparams,headers)
    ratingresponse = urllib.request.urlopen(ratingrequest)
    ratingjson = json.loads(ratingresponse.read().decode())
    totalNumberOfReviews = ratingjson['totalNumberOfReviews']
    ratingname = ['appname','country','platform','date','totalNumberOfReviews','ratingAverage','ratingCount','1stars','2stars','3stars','4starts','5stars']
    rating_result_list = []
    rating_result_list.append( [ appname,country,platform,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), ratingjson['totalNumberOfReviews'],ratingjson['ratingAverage'],ratingjson['ratingCount'],ratingjson['ratingCountList'][0],ratingjson['ratingCountList'][1],ratingjson['ratingCountList'][2],ratingjson['ratingCountList'][3],ratingjson['ratingCountList'][4] ])
    ratingdf = pd.DataFrame(columns=ratingname, data=rating_result_list)
    
    result_list = []
    reviews_num = ratingjson['totalNumberOfReviews']
    if reviews_num > previousReviewsNum:
        print('new customer reviews:',str(reviews_num-previousReviewsNum))
        print('begin download reviews ...')
        url = 'https://itunes.apple.com/WebObjects/MZStore.woa/wa/userReviewsRow?cc=' + str(country) + '&id=' + str(appid) + '&displayable-kind=11&startIndex='+ str(previousReviewsNum) +'&endIndex=' + str(reviews_num) + '&sort=0&appVersion=all'
        print(url)
        data = {}
        params = urllib.parse.urlencode(data).encode(encoding='UTF8')
        request = urllib.request.Request(url,params,headers)
        response = urllib.request.urlopen(request)
        myjson = json.loads(response.read().decode())
        reviews = myjson['userReviewList']
        result_list = []
        for i in range(len(reviews)):
            values = reviews[i]
            result_list.append([ appname, country, platform, values['date'], values['name'], values['title'], values['body'], values['rating'] ])
        name = ['appname','country','platform','date', 'name', 'title', 'content', 'rating']
        reviewdf = pd.DataFrame(columns=name, data=result_list)
        print('begin write reviews ...') 
        reviewdf.to_sql("customer_reviews", connect, if_exists='append', index=False)
        #csv_list = pd.DataFrame(columns=name, data=result_list)
        #csv_list.to_csv(str(appid)+'reviews.csv', index=None, encoding='utf_8_sig')
    else:
        print('no new customer reviews')
    print('begin write ratings ...') 
    ratingdf.to_sql("customer_ratings", connect, if_exists='append', index=False)

if __name__ == '__main__':
    main()

