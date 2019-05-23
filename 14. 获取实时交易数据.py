#!/usr/bin/env python
# coding: utf-8

# ## 通过sina获取实时交易数据
# 
# ### 利用爬虫库

# In[1]:


from urllib.request import urlopen
import pandas as pd
pd.set_option('expand_frame_repr', False) # 列不换行
pd.set_option('display.max_rows', 5000) # 最多显示行数

# 返回数据网址
# 获取代码网址 http://hq.sinajs.cn/list=sz000001,sh000001
# 正常网址 http://finance.sina.com.cn/realstock/company/sh600000/nc.shtml


# ### 构建网址

# In[2]:


# 含退市，停牌，新股
# 请在此处设置参数！
stock_code_list = ['sh600000', 'sz000002', 'sh600002', 'sh600003', 'sh600610', 'sh600145', 'sh603982']
url = 'http://hq.sinajs.cn/list=' + ','.join(stock_code_list)
# print(url)


# ### 抓取数据

# In[3]:


content = urlopen(url).read().decode('gbk')
# print(type(content))
# print(content)


# ### 整理数据

# In[4]:


content = content.strip() # 去除文本前后空格、回车等
data_line = content.split('\n') # 通过回车划分数据
# print(data_line)


# In[5]:


data_line = [data.replace('var hq_str_', '').split(',') for data in data_line] # 去除无意义文字，对每个列表再细分
df = pd.DataFrame(data_line, dtype='float') # 将数字识别出来
# print(df)


# ### 细整理数据，赋予列名

# In[6]:


df[0] = df[0].str.split('="')
df['stock_code'] = df[0].str[0].str.strip()
df['stock_name'] = df[0].str[-1].str.strip()
df['candle_end_time'] = df[30] + ' ' + df[31]
df['candle_end_time'] = pd.to_datetime(df['candle_end_time'])

# print(df)


# In[7]:


rename_dict = {1:'open', 2:'pre_close', 3:'close', 4:'high', 5:'low', 6:'buy1', 7:'sell1',
              8:'amount', 9:'volume', 32:'status'}
df.rename(columns=rename_dict, inplace=True)
df['status'] = df['status'].str.strip('";')

# print(df)


# In[8]:


df = df[['stock_code', 'stock_name', 'candle_end_time', 'open', 'high', 'low', 'close', 'pre_close', 
         'amount', 'volume', 'buy1', 'sell1', 'status']]
print(df)


# ### 备注
# 退市、停牌：开盘价为0 df[['open'] - 0 < 0.000001]
# 
# 正常：status = 00
# 
# 退市：status = -3, pre_close == 0
# 
# 停牌：status = 03, pre_close != 0
# 
# 
# 新上市：pre_close为发行价
# 
# 除权： pre_close为除权后的收盘价
