#coding=utf-8
import pymongo
import tushare as ts
import re
class seller:
    """
    """
    def monitortrade(self):
        conn = pymongo.MongoClient('192.168.222.188', port=27017)
        # for item in conn.mystock.trade.find({'buytime':re.compile('2016-05-27')}):
        for item in conn.mystock.trade.find():

            # print item['buytime']
            df = ts.get_realtime_quotes(item['code'])
            df1 = ts.get_hist_data(item['code']).head(1)

            status = item['detailtype']

            open = df1['open'][0]
            nowprice = df['price'][0]
            profit = (float(nowprice)-float(item['buyprice']))/float(item['buyprice'])*100

            if(status=='lowopencross0'):

                print item['code'],item['buytime'],'buy price ',item['buyprice'],'and now price ',nowprice ,'收益:',round(profit,2),'%'
            if (status == 'highopenlowhigh'):

                print item['code'],item['buytime'],' buy price ', item['buyprice'],'and now price ', nowprice,'收益:',round(profit,2),'%'

seller().monitortrade()