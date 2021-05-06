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
import re,random
import requests

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
            ratingname = ['appid', 'appname', 'country', 'platform', 'date', 'totalNumberOfReviews', 'ratingAverage',
                            'ratingCount', '1stars', '2stars', '3stars', '4starts', '5stars']
            rating_result_list = []
            rating_result_list.append(
                [self.appid, self.appname, self.country, self.platform, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
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
            for i in range(len(reviews)):
                values = reviews[i]
                result_list.append(
                    [values['userReviewId'], self.appid, self.appname, self.country, self.platform, values['date'],
                        values['name'], values['title'], values['body'], values['rating']])
            name = ['id', 'appid', 'appname', 'country', 'platform', 'date', 'name', 'title', 'content', 'rating']
            reviews_df = pd.DataFrame(columns=name, data=result_list)
            return reviews_df

        if self.platform == 'GooglePlay':
            reviews_result = reviews_all(
                self.appid,
                country=self.country,
                sort=Sort.MOST_RELEVANT)
            reviews_result_list = []
            reviews_name = ['id', 'appid', 'appname', 'country', 'platform', 'date', 'name', 'title', 'content', 'rating']
            # print("%s在%s总计%d行" % (self.appname, self.platform, len(reviews_result)))
            for i in range(len(reviews_result)):
                values = reviews_result[i]
                reviews_result_list.append(
                    [values['reviewId'], self.appid, self.appname, self.country, self.platform, values['at'],
                        values['userName'], '', values['content'], values['score']])
            reviews_df = pd.DataFrame(columns=reviews_name, data=reviews_result_list)
            return reviews_df

        if self.platform == 'TapTap':
            HEADERS = {'Host': 'api.taptapdada.com','Connection': 'Keep-Alive','Accept-Encoding': 'gzip','User-Agent': 'okhttp/3.10.0'}
            BASE_URL = 'https://api.taptapdada.com/review/v1/by-app?sort=new&app_id={}' \
                '&X-UA=V%3D1%26PN%3DTapTap%26VN_CODE%3D593%26LOC%3DCN%26LANG%3Dzh_CN%26CH%3Ddefault' \
                '%26UID%3D8a5b2b39-ad33-40f3-8634-eef5dcba01e4%26VID%3D7595643&from={}'
            end_from = 200
            reviews = []
            reviews_result_list = []
            for i in range(0, end_from+1, 10):
                url = BASE_URL.format(self.appid, i)
                try:
                    resp = requests.get(url, headers=HEADERS).json()
                    resp = resp.get('data').get('list')
                    for r in resp:
                        review = {}
                        review['id'] = str(r.get('id'))
                        review['appid'] = str(self.appid)
                        review['author'] = r.get('author').get('name').encode('gbk', 'ignore').decode('gbk')
                        review['updated_time'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(r.get('updated_time')))
                        review['stars'] = r.get('score')
                        content = r.get('contents').get('text').strip()
                        review['content'] = re.sub('<br />|&nbsp', '', content).encode('gbk', 'ignore').decode('gbk')
                        reviews.append(review)
                    #print('=============已爬取第 %d 页=============' % int(i/10))
                    # 等待0至1秒，爬下一页
                    if i != end_from:
                        pause = random.uniform(0, 1)
                        time.sleep(pause)
                except Exception as error:
                    raise error
            for i in range(len(reviews)):
                values = reviews[i]
                reviews_result_list.append(
                    [values['id'], self.appid, self.appname, self.country, self.platform, values['updated_time'],
                        values['author'], '', values['content'], values['stars']])
            name = ['id','appid', 'appname', 'country', 'platform', 'date', 'name', 'title', 'content', 'rating']
            reviews_df = pd.DataFrame(columns=name, data=reviews_result_list)
            return reviews_df

def write_mysql(connect, dataframe, tablename):
    if tablename == 'customer_reviews_temp':
        try:
            pd.read_sql(sql='truncate table customer_reviews_temp;', con=connect)
        except:
            dataframe.to_sql(tablename, connect, if_exists='append', index=False)
    else:
        dataframe.to_sql(tablename, connect, if_exists='append', index=False)

def logger_error(logs):
    write_logs = [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())]
    write_logs.extend(logs)
    f = open('error.log', 'a')
    f.write("\t".join(write_logs) + '\n')
    f.close()

def do_translate(df):
    content = df['content']
    code = df['lang']
    try:
        if code in translate_list:
            response = translate.translate_text(
                Text=content,
                SourceLanguageCode=code,
                TargetLanguageCode='zh')
            return response['TranslatedText']
    except BaseException as e:
        print("不支持翻译的语言")
        logger_error([df['appname'], df['platform'], '翻译不支持的语言  id：' + df['id'], ' 内容：'+ df['content']])        
    
def do_detect_language(df):
    content = df['content']
    language_code = comprehend.detect_dominant_language(Text=content)
    code = language_code['Languages'][0]['LanguageCode']
    return code

def do_sentiment(df):
    content = df['content']
    code = df['lang']
    try:
        sentiment = comprehend.detect_sentiment(Text=content, LanguageCode=code)
        return sentiment['Sentiment']
    except BaseException as e:
        print("不支持情感分析的语言")
        logger_error([df['appname'], df['platform'], 'Sentiment不支持的语言  id：' + df['id'] ,' 内容：'+ df['content']])

start = time.time()
rdshost = os.environ.get('rdshost')
rdsuser = os.environ.get('rdsuser')
rdspassword = os.environ.get('rdspassword')
database = os.environ.get('rdsdatabase')
connect = create_engine('mysql+pymysql://' + rdsuser + ':' + rdspassword + '@' + rdshost + ':3306/' + database + '?charset=utf8mb4')
appbucket = os.environ.get('appbucket')
# appkey = os.environ.get('appkey')
#s3
s3 = boto3.resource('s3')
# translate
translate = boto3.client('translate', region_name=os.environ.get('region'))
#comprehend
comprehend = boto3.client('comprehend', region_name=os.environ.get('region'))

#translate.csv
s3.meta.client.download_file(appbucket, 'translate.csv', 'translate.csv')
translate_df = pd.read_csv('translate.csv')
translate_num = translate_df.shape[0]
translate_list = []
for i in range(0, translate_num):
    translate_list.append(translate_df.iloc[i, 0])

#处理app.csv
s3.meta.client.download_file(appbucket, 'app.csv', 'app.csv')
app_df = pd.read_csv('app.csv')
app_num = app_df.shape[0]

for i in range(0,app_num):
    print('-------------------------------------------------------------')
    print("开始下载%s %s %s %s 的评论 ... " % (app_df.iloc[i,0],app_df.iloc[i,1],app_df.iloc[i,2],app_df.iloc[i,3]))
    app = App(app_df.iloc[i,0],app_df.iloc[i,1],app_df.iloc[i,2],app_df.iloc[i,3])
    #插入所有评论到customer_reviews_temp表
    write_mysql(connect, app.reviews(), 'customer_reviews_temp')
    print("%s %s %s %s 的评论下载完成" % (app_df.iloc[i,0],app_df.iloc[i,1],app_df.iloc[i,2],app_df.iloc[i,3]))
    #获取增量评论
    sql_cmd = "select id,appid,appname,country,country,platform,date,name,title,content,rating from customer_reviews_temp where id not in (select id from customer_reviews) and appid = '"+app_df.iloc[i,3]+"';"
    reviews_df = pd.read_sql(sql=sql_cmd, con=connect)
    reviews_df = reviews_df.loc[ reviews_df['content'].str.len() > 0 ]
    reviews_df = reviews_df.loc[ reviews_df['content'].str.len() < 1000]
    num = reviews_df.shape[0]
    if num > 0:
        print("%s %s %s %s 有 %d 条新增评论 ... " % (app_df.iloc[i,0],app_df.iloc[i,1],app_df.iloc[i,2],app_df.iloc[i,3],num))
        print('开始识别评论内容语言...')
        reviews_df['lang'] = reviews_df.apply(do_detect_language, axis=1)
        print('开始识别评论内容情感分析...')
        reviews_df['sentiment'] = reviews_df.apply(do_sentiment, axis=1)
        print('翻译评论内容')
        reviews_df['content_cn'] = reviews_df.apply(do_translate, axis=1)
        reviews_df.to_sql('customer_reviews', connect, index=False, if_exists='append')
        print('评论处理完毕')
    else:
        print("%s %s %s %s 没有新增评论 " % (app_df.iloc[i,0],app_df.iloc[i,1],app_df.iloc[i,2],app_df.iloc[i,3]))

end = time.time()
spend = (end - start)
print("总共花费时间为 %s秒" % spend)