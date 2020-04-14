import time

import pymysql

from common import dbutil
# import logging
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
# logging.getLogger().setLevel(logging.INFO)

"""
微信公众号活跃度排名

"""
conn = dbutil.connectdb_wechatcluster()


if __name__ == '__main__':
    # comment_to_table()
    # comment_distribute('test')
    aa = {}

    sql = 'SELECT biz, (COUNT(*)+0.1*SUM(comment_num)) num FROM content GROUP BY biz'
    result = dbutil.query_with_sql(conn, sql)

    for (biz, num) in result:
        aa.setdefault(biz, num)

    sql = 'SELECT biz, num from userstick'
    result = dbutil.query_with_sql(conn, sql)

    bb = {}
    for (biz, num) in result:
        bb.setdefault(biz, aa.get(biz)+num)

    c = sorted(bb.items(), reverse=True, key=lambda kv: (kv[1], kv[0]))
    flag = 0
    for key, value in c:
        if flag == 10:
            break
        flag = flag+1
        print(value)

        # sql = "select nickname from bizinfo where biz ='{}'".format(key)
        # result = dbutil.query_with_sql_one(conn, sql)
        # print(result[0])

