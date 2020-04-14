import time
from common import dbutil, wxdriver, global_variable as glv

"""
更新公众号采集时间范围
"""
conn = dbutil.connectdb_wechatcluster()


if __name__ == '__main__':

    data = {}

    sql = "SELECT biz, MIN(datetime) as mintime FROM content GROUP BY biz"
    result = dbutil.query_with_sql(conn, sql)
    for(biz, mintime) in result:
        # 转换成localtime
        time_local = time.localtime(mintime)
        # 转换成新的时间格式(2016-05-05 20:28:54)
        mintime_format = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
        sql2 = "select nickname from bizinfo where biz='{}'".format(biz)
        nickname = dbutil.query_with_sql_one(conn, sql2)
        if nickname:
            sql3 = "SELECT MAX(datetime) as maxtime FROM content where biz = '{}'".format(biz)
            result3 = dbutil.query_with_sql_one(conn, sql3)
            maxtime = result3[0]
            # 转换成localtime
            time_local = time.localtime(maxtime)
            # 转换成新的时间格式(2016-05-05 20:28:54)
            maxtime_format = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
            meta = {
                'mintime': mintime_format,
                'maxtime': maxtime_format,
                'nickname': nickname
            }
            sql4 = "update bizinfo set mintime='{}', maxtime='{}' where biz='{}' "\
                .format(mintime_format, maxtime_format, biz)
            exec_sql = dbutil.exec_sql(conn, sql4)
            data[biz] = meta
        else:
            print('未查询到结果')

    print(len(data))
    for key in data.keys():
        print(key)
        print(data[key])


