#!/usr/bin/env python
# coding: utf-8

path_dir = r'/Users/yinianzhang/Downloads/股票数据/update_stock_data'
# 在此输入存放股票数据的文件夹，文件夹内文件为所有个股的历史数据


from urllib.request import urlopen
import pandas as pd
import time
from datetime import datetime
import re
import os
import json
pd.set_option('expand_frame_repr', False) # 列不换行
pd.set_option('display.max_rows', 5000) # 最多显示行数




def get_content_from_internet(url, max_try_num = 10, sleep_time = 5):
    get_success = False
    
    for i in range(max_try_num):
        try:
            content = urlopen(url=url, timeout = 10).read()
            get_success = True
            break
        except Exception as e:
            print('抓取报错次数：', i+1, '报错内容：', e)
            time.sleep(sleep_time)
    
    if get_success:
        return content
    else:
        raise ValueError('抓取数据失败')
            

def get_today_data_from_sinajs(code_list):
    url = 'http://hq.sinajs.cn/list=' + ','.join(code_list)
    
    content = get_content_from_internet(url)
    content = content.decode('gbk')
    
    content = content.strip() # 去除文本前后空格、回车等
    data_line = content.split('\n') # 通过回车划分数据
    data_line = [data.replace('var hq_str_', '').split(',') for data in data_line] # 去除无意义文字，对每个列表再细分
    df = pd.DataFrame(data_line, dtype='float') # 将数字识别出来
    df[0] = df[0].str.split('="')
    df['stock_code'] = df[0].str[0].str.strip()
    df['stock_name'] = df[0].str[-1].str.strip()
    df['candle_end_time'] = df[30] + ' ' + df[31]
    df['candle_end_time'] = pd.to_datetime(df['candle_end_time'])
    rename_dict = {1:'open', 2:'pre_close', 3:'close', 4:'high', 5:'low', 6:'buy1', 7:'sell1',
                  8:'amount', 9:'volume', 32:'status'}
    df.rename(columns=rename_dict, inplace=True)
    df['status'] = df['status'].str.strip('";')
    df = df[['stock_code', 'stock_name', 'candle_end_time', 'open', 'high', 'low', 'close', 'pre_close', 
         'amount', 'volume', 'buy1', 'sell1', 'status']]
    return df

def is_today_trading_day():
    df = get_today_data_from_sinajs(code_list = ['sh000001'])
    sh_date = df.iloc[0]['candle_end_time']
    return datetime.now().date() == sh_date.date()

def get_all_today_stock_data_from_sina_marketcenter():
    raw_url = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/'   \
            'Market_Center.getHQNodeData?page=%s&num=80&sort=symbol&asc=0&node=hs_a&symbol=&_s_r_a=sort'
    page_num = 1
    
    all_df = pd.DataFrame()
    
    while True:
        url = raw_url % (page_num)
        print('开始抓取数据', page_num)
        
        content = get_content_from_internet(url)
        content = content.decode('gbk')
        
        if 'null' in content:
            print('抓取到页面尽头')
            break
        
        content = re.sub(r'(?<={|,)([a-zA-Z][a-zA-Z0-9]*)(?=:)', r'"\1"', content)
        content = json.loads(content)
        
        df = pd.DataFrame(content)
        rename_dict = {'symbol': '股票代码', 'name': '股票名称', 'open': '开盘价', 'high': '最高价', 'low': '最低价', 'trade': '收盘价',
                       'settlement': '前收盘价', 'volume': '成交量', 'amount': '成交额'}
        df.rename(columns=rename_dict, inplace=True)
        df['交易日期'] = pd.to_datetime(datetime.now().date())
        df = df[['股票代码', '股票名称', '开盘价', '最高价', '最低价', '收盘价', '前收盘价', '成交量', '成交额']]
        
        all_df = all_df.append(df, ignore_index=True)
        
        page_num += 1
        time.sleep(0.1)
    return all_df
    

if is_today_trading_day() is False:
    print('今天不是交易日，无法更新数据')
    exit()

if datetime.now().hour < 15:
    print('尚未收盘，无法更新数据')
    exit()
    
df = pd.DataFrame()
df = get_all_today_stock_data_from_sina_marketcenter()


for i in df.index:
    t = df.iloc[i:i+1, :]
    stock_code = t.iloc[0]['股票代码']
    
    path=path_dir + stock_code + '.csv'
    
    if os.path.exists(path):
        t.to_csv(path, header=None, index= False, mode='a', encoding='gbk')
    else:
        pd.DataFrame(columns=['数据整理']).to_csv(path, index=False, encoding='gbk')
        t.to_csv(path, index= False, mode='a', encoding='gbk')

