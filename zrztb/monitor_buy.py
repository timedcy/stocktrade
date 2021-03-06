#coding=utf-8
import pymongo
import json
import tushare as ts
import time
import easytrader as et

#最弱涨停板监控
#

useryjb = et.use('yjb')
useryjb.prepare('yjb.json')


user = et.use('xq')
user.prepare('xq.json')



maxstockcount = 6

conn = pymongo.MongoClient('192.168.222.188', port=27017)
inserttime = time.strftime("%Y-%m-%d", time.localtime())

while 1:
    if (time.strftime("%H:%M:%S", time.localtime()) < '08:30:00'):
        time.sleep(3600)
    if(time.strftime("%H:%M:%S", time.localtime())< '09:30:00'):
        continue

    if(time.strftime("%H:%M:%S", time.localtime())== '11:30:00'):
        time.sleep(5400)
    #下午3点退出
    if (time.strftime("%H:%M:%S", time.localtime()) == '15:00:00'):
            break

    for item in conn.mystock.monitor_weakhardencode.find({"isdeal":0}):
        try:
            df = ts.get_realtime_quotes(item['code'])
            # conn.mystock.monitor_his.insert(json.loads(df.to_json(orient='records')))

            if(item['status']=='init'):
                #判断低开
                if(df['pre_close']>df['open']).bool():
                    conn.mystock.monitor_weakhardencode.update({'code':item['code'],'status':'init'},{'$set':{'status':'lowopen'}})

                # 判断高开
                if(df['pre_close']<=df['open']).bool():
                    conn.mystock.monitor_weakhardencode.update({'code': item['code'],'status':'init'},{'$set': {'status': 'highopen'}})

            #低开过零轴
            if(item['status']=='lowopen'):
                #及时数据有可能没有拿到，所有应该取当日所有数据（当时）
                if(df['price']>df['pre_close']).bool():
                    print "D0，推荐买入！！！",item['code']
                    print "买入时间：", time.strftime("%Y-%m-%d %X", time.localtime())
                    print "买入价格", df['price'][0]

                    conn.mystock.monitor_weakhardencode.update({'code': item['code'], 'status': 'lowopen'},{'$set': {'status': 'lowopencross0', 'isdeal': 1}})

                    # 佣金宝购买策略
                    # stockcount = int(user.balance[0]['enable_balance'] / (buyprice * 100))
                    conn.mystock.yjbtrade.insert(
                        {"code": item['code'], "buytime": time.strftime("%Y-%m-%d %X", time.localtime()),
                         "buytype": "zrztb", "detailtype": "lowopencross0", "buyprice": df['price'][0],
                         "tradestatus": 0, 'stockcount': stockcount})
                    buyprice = round(float(df['price'][0]) * 1.02, 2)

                    # 买入股票(初期设置100的数量，后期使用策略)
                    useryjb.buy(item['code'], price=buyprice, amount=100)
                    print '***********************'
                    print '***********************'
                    print '*****佣金宝买入成功*****'
                    print '***********************'
                    print '***********************'
                    print '买入价格', buyprice


                    #持仓数量小于策略数量时，购买
                    if(maxstockcount > len(user.position)):
                        # 买入价格高于当前价格，以确定肯定能买到
                        buyprice = round(float(df['price'][0])*1.02,2)
                        stockcount = int(user.balance[0]['enable_balance'] / (maxstockcount-len(user.position)) / (buyprice))
                        conn.mystock.trade.insert({"code":item['code'],"buytime":time.strftime("%Y-%m-%d %X", time.localtime()),"buytype":"zrztb","detailtype":"lowopencross0","buyprice":df['price'][0],"tradestatus":0,'stockcount':stockcount})
                        user.buy(item['code'],float(df['price'][0]),stockcount)
                        print '账户买入成功'
                        print '剩余可用资金', user.balance[0]['enable_balance']
                        print '买入数量', stockcount





                    #高开低走
            if (item['status'] == 'highopen'):
                if (df['price'] < df['open']).bool():
                    print item['code'],'判断低走价格',df['price'][0]
                    conn.mystock.monitor_weakhardencode.update({'code': item['code'],'status':'highopen'},{'$set': {'status': 'highopenlow'}})
            #高开低走再高走(判断再高走的条件20160601修改)
            if (item['status'] == 'highopenlow'):
                if (df['price'] > df['open']).bool():
                    print "GDG，推荐买入！！！",item['code']
                    print "买入时间：",time.strftime("%Y-%m-%d %X", time.localtime())
                    print "买入价格", df['price'][0]

                    conn.mystock.monitor_weakhardencode.update({'code': item['code'], 'status': 'highopenlow'},{'$set': {'status': 'highopenlowhigh', 'isdeal': 1}})

                    # 佣金宝购买策略
                    # stockcount = int(user.balance[0]['enable_balance'] / (buyprice * 100))
                    conn.mystock.yjbtrade.insert(
                        {"code": item['code'], "buytime": time.strftime("%Y-%m-%d %X", time.localtime()),
                         "buytype": "zrztb", "detailtype": "lowopencross0", "buyprice": df['price'][0],
                         "tradestatus": 0, 'stockcount': stockcount})
                    buyprice = round(float(df['price'][0]) * 1.02, 2)

                    # 买入股票(初期设置100的数量，后期使用策略)
                    useryjb.buy(item['code'], price=buyprice, amount=100)
                    print '***********************'
                    print '***********************'
                    print '*****佣金宝买入成功*****'
                    print '***********************'
                    print '***********************'
                    print '买入价格', buyprice

                    # 持仓数量小于策略数量时，购买
                    if (maxstockcount > len(user.position)):
                        #买入价格高于当前价格，以确定肯定能买到
                        buyprice = round(float(df['price'][0]) * 1.02, 2)
                        #购买股票数量
                        stockcount = int(user.balance[0]['enable_balance'] / (maxstockcount-len(user.position)) / (buyprice))

                        if stockcount<= 0:
                            print '资金不足'
                            continue

                        conn.mystock.trade.insert(
                            {"code": item['code'], "buytime": time.strftime("%Y-%m-%d %X", time.localtime()),
                             "buytype": "zrztb", "detailtype": "highopenlowhigh", "buyprice": df['price'][0],
                             "tradestatus": 0, 'stockcount': stockcount})
                        user.buy(item['code'], float(df['price'][0]), stockcount)
                        print '账户买入成功'
                        print '剩余可用资金', user.balance[0]['enable_balance']
                        print '买入数量', stockcount





        except Exception as e:
            print e
            continue

