#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import pandas as pd 
import json

def getHTMLText(url):
    response = urllib.request.urlopen(url)
    myjson = json.loads(response.read().decode())
    return myjson

def main():
    appid = input("请输入应用id号:")
    # appName = input("请输入应用名称:")
    count = 0
    total = 10
    totalCount = 0
    result_list = []
    for n in range(total):
        url = 'https://itunes.apple.com/rss/customerreviews/page=' + \
            str(n+1) + '/id=' + str(appid) + \
            '/sortby=mostrecent/json?l=en&&cc=cn'
        print('当前地址：' + url)
        jsonText = getHTMLText(url)
        # print(jsonText)
        data_feed = jsonText['feed']
        entry = data_feed['entry']
        for i in range(len(entry)):
            value = entry[i]
            fixedIndex = i + 1
            startRow = totalCount + 1
            result_list.append([value['author']['name']['label'], value['title']['label'], value['content']['label'], value['im:version']['label'], value['im:rating']['label']])
            totalCount = totalCount + 1
        count = count + 1
    # print(result_list)

    name = ['作者', '标题', '评论内容', '版本', '评级']
    csv_list = pd.DataFrame(columns=name, data=result_list)
    csv_list.to_csv('xx.csv', index=None, encoding='utf_8_sig')

if __name__ == '__main__':
    main()