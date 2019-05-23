#!/usr/bin/env python
# coding: utf-8

# In[1]:


from urllib.request import urlopen
import pandas as pd
import json
from random import randint

pd.set_option('expand_frame_repr', False) # 列不换行
pd.set_option('display.max_rows', 5000) # 最多显示行数

# 返回数据网址
# 获取代码网址 http://ifzq.gtimg.cn/appstock/app/kline/mkline?param=sz000001,m5,,,100&_var=m5_today&r=0.5643184591626897
# 正常网址 http://stockhtm.finance.qq.com/sstock/ggcx/000001.shtml
# 
# 关键参数sz000001 10 day 16位随机数

stock_code = 'sz000001' #股票代码
k_type = '5' # 5, 15, 30, 60
num = 100 # 获取k线根数, 不超过320根

'''
参数说明：
可返回股票代码，如sz000001
可返回指数，如sh000001
可返回ETF，如sh5105000
'''


# ### 创建16位随机数

# In[2]:


def _random(n=16):
    """
    创建n位随机整数
    """
    start = 10**(n-1)
    end = (10**n)-1
    return str(randint(start, end))


# ### 构建网址

# In[3]:


url = 'http://ifzq.gtimg.cn/appstock/app/kline/mkline?param=%s,m%s,,,%s&_var=%s_today&r=0.%s'
url = url % (stock_code, k_type, num, k_type, _random())

print(url)


# ### 抓取数据

# In[4]:


content = urlopen(url=url, timeout=15).read().decode()
content = content.split('=', maxsplit=1)[-1]
content = json.loads(content)

print(type(content))
print(content)


# ### 整理数据

# In[5]:


k_data = content['data'][stock_code]['m' + str(k_type)]

df = pd.DataFrame(k_data)
print(df)


# In[7]:


rename_dict ={0:'candle_end_time', 1:'open', 2:'close', 3:'high', 4:'low', 5:'amount'}
# amount 单位为手
df.rename(columns=rename_dict, inplace=True)

print(df)


# ### 将时间变为可读格式

# In[8]:


df['candle_end_time'] = df['candle_end_time'].apply(lambda x:'%s-%s-%s %s:%s' % (x[0:4], x[4:6], x[6:8], x[8:10], x[10:12]))
df['candle_end_time'] = pd.to_datetime(df['candle_end_time'])

df = df[['candle_end_time', 'open', 'high', 'low', 'close', 'amount']]

print(df)


# ### 备注
# 
# 退市股票无分钟数据
# 分钟级别k线不做复权处理
