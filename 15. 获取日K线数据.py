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
# 获取代码网址 http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayqfq&param=sz000001,day,,,10,qfq&r=0.5643184591626897
# 正常网址 http://stockhtm.finance.qq.com/sstock/ggcx/000001.shtml
# 
# 关键参数sz000001 10 day 16位随机数

stock_code = 'sz000001' #股票代码
k_type = 'day' # 日线 day week month
num = 10 # 获取k线根数

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


url = 'http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_%sqfq&param=%s,%s,,,%s,qfq&r=0.%s'
url = url % (k_type, stock_code, k_type, num, _random())

print(url)


# ### 抓取数据

# In[4]:


content = urlopen(url).read().decode('gbk')
content = content.split('=', maxsplit=1)[-1]
content = json.loads(content)

print(type(content))
print(content)


# ### 整理数据

# In[5]:


k_data = content['data'][stock_code]
print(k_data)

if k_type in k_data:
    k_data = k_data[k_type]
elif 'qfq' + k_type in k_data:
    k_data = k_data['qfq' + k_type]
else:
    raise ValueError('已知key不存在')
    
df = pd.DataFrame(k_data)
print(df)


# In[6]:


rename_dict ={0:'candle_end_time', 1:'open', 2:'close', 3:'high', 4:'low', 5:'amount', 6:'info'}
# amount 单位为手
df.rename(columns=rename_dict, inplace=True)

if 'info' not in df:
    df['info'] = None
df = df[['candle_end_time', 'open', 'high', 'low', 'close', 'amount', 'info']]

print(df)


# ### 备注
# 
# info中存储除权信息，如果有会显示
# 
# 股票日线数据不超过640根，指数，ETF不限
# 
