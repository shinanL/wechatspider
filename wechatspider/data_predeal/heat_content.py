import os
import time
from common import dbutil, pltutil
from matplotlib.font_manager import FontProperties
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import collections
from matplotlib_venn import venn2
from matplotlib_venn import venn3
# import pandas as pd

from matplotlib.font_manager import FontProperties
font_set = FontProperties(fname='/Library/Fonts/Songti.ttc', size=15)

"""
微信公众号阅读量统计分析
"""
START_TIME = 1546272000
END_TIME = 1577808000
conn = dbutil.connectdb_wechatcluster()


def heat_quantity():
    """
    热议文章和优质文章的交集，评论点赞量取对数
    :return:
    """
    sql = "select biz, nickname from bizinfo"
    result = dbutil.query_with_sql(conn, sql)
    total = 0

    for (biz, nickname) in result:
        print("公众号昵称", nickname)
        heat_id = set()
        sql = "SELECT AVG((comment_num+LN(commentlike_num))/readnum) as mean FROM content WHERE biz = '%s'" % biz
        result = dbutil.query_with_sql_one(conn, sql)
        mean = result[0]

        sql = "SELECT id, (comment_num+LN(commentlike_num))/readnum as num FROM content WHERE biz = '%s'" % biz
        result = dbutil.query_with_sql(conn, sql)

        for (id, num) in result:
            if num and num > mean:
                heat_id.add(id)

        print(len(heat_id))

        quanlity_id = set()
        sql = "SELECT AVG(likenum/readnum) as mean FROM content WHERE biz = '%s'" % biz
        result = dbutil.query_with_sql_one(conn, sql)
        mean = result[0]

        sql = "SELECT id, likenum/readnum as num FROM content WHERE biz = '%s'" % biz
        result = dbutil.query_with_sql(conn, sql)

        for (id, num) in result:
            if num and num > mean:
                quanlity_id.add(id)

        print(len(quanlity_id))

        cross = heat_id & quanlity_id
        total += len(cross)

        plt.figure(figsize=(4, 4))
        venn2(subsets=[heat_id, quanlity_id], set_labels=('heat', 'quanlity'))
        plt.savefig("./heat/" + '%s.png' % nickname)
        plt.close()
    print("总量", total)


def heat_quantity2():
    """
    热议文章和优质文章的交集，评论点赞量常量比，这个比值可以根据各个公众号进行拟合
    :return:
    """

    sql = "select biz, nickname from bizinfo"
    result = dbutil.query_with_sql(conn, sql)
    total = 0

    for (biz, nickname) in result:
        print("公众号昵称", nickname)
        heat_id = set()
        sql = "SELECT AVG((comment_num+commentlike_num/200)/readnum) as mean FROM content WHERE biz = '%s'" % biz
        result = dbutil.query_with_sql_one(conn, sql)
        mean = result[0]

        sql = "SELECT id, (comment_num+commentlike_num/200)/readnum as num FROM content WHERE biz = '%s'" % biz
        result = dbutil.query_with_sql(conn, sql)

        for (id, num) in result:
            if num and num > mean:
                heat_id.add(id)

        print(len(heat_id))

        quanlity_id = set()
        sql = "SELECT AVG(likenum/readnum) as mean FROM content WHERE biz = '%s'" % biz
        result = dbutil.query_with_sql_one(conn, sql)
        mean = result[0]

        sql = "SELECT id, likenum/readnum as num FROM content WHERE biz = '%s'" % biz
        result = dbutil.query_with_sql(conn, sql)

        for (id, num) in result:
            if num and num > mean:
                quanlity_id.add(id)

        print(len(quanlity_id))

        cross = heat_id & quanlity_id
        total += len(cross)

        plt.figure(figsize=(4, 4))
        venn2(subsets=[heat_id, quanlity_id], set_labels=('heat', 'quanlity'))
        plt.savefig("./heat/" + '%s.png' % nickname)
        plt.close()
    print("总量", total)


if __name__ == '__main__':

    headlines = set()
    quans = set()
    hot = set()
    sql = 'select id from content where idx=1'
    result = dbutil.query_with_sql(conn, sql)
    for (id,) in result:
        headlines.add(id)

    # data = pd.read_excel('优质和热议的文章.xls')
    # mean_quan = 106.8859
    # mean_hot = 84.6293
    # quans = data['id'][data['quan']>mean_quan]
    # print(quans)


    sql = 'select id from content where likenum/readnum > 0.0106886'
    result = dbutil.query_with_sql(conn, sql)
    for (id,) in result:
        quans.add(id)

    sql = 'select id from content where (comment_num+0.004*commentlike_num)/readnum > 0.0008463'
    result = dbutil.query_with_sql(conn, sql)
    for (id,) in result:
        hot.add(id)

    print(len(headlines))
    print(len(quans))
    print(len(hot))
    # # 标题
    # plt.title('候选文集', fontproperties=font_set)
    #
    # # 横坐标描述
    # plt.xlabel(xlabel, fontproperties=font_set)
    #
    # # 纵坐标描述
    # plt.ylabel(ylabel, fontproperties=font_set)
    # plt.figure(figsize=(2, 2))

    venn3(subsets=[headlines, quans, hot], set_labels=('headlines', 'high quantity', 'hot') )
    plt.savefig('./头条优质热议文章集合')
    plt.show()


    # heat_quantity()
    # heat_quantity2()
    # index_each_biz()
    # read_id = set()
    # sql = "SELECT id FROM content WHERE biz = 'MzA5OTQyMDgyOQ==' and readnum>(select AVG(readnum) from content where biz ='MzA5OTQyMDgyOQ==') "
    # result = dbutil.query_with_sql(conn, sql)
    # for(id,) in result:
    #     read_id.add(id)
    # print(len(read_id))
    #
    # comment_set = set()
    # sql = "SELECT id FROM content WHERE biz = 'MzA5OTQyMDgyOQ==' and comment_num>(select AVG(comment_num) from content where biz ='MzA5OTQyMDgyOQ==') "
    # result = dbutil.query_with_sql(conn, sql)
    # for (id,) in result:
    #     comment_set.add(id)
    # print(len(comment_set))
    #
    #
    # comment_id = set()
    # nums =[]
    #
    # sql = "SELECT AVG(comment_num+commentlike_num) as mean FROM content WHERE biz = 'MzA5OTQyMDgyOQ=='"
    # result = dbutil.query_with_sql_one(conn, sql)
    # mean = result[0]
    #
    #
    # sql = "SELECT id, (comment_num+commentlike_num) as num FROM content WHERE biz = 'MzA5OTQyMDgyOQ=='"
    # print(sql)
    # result = dbutil.query_with_sql(conn, sql)
    #
    # for (id, num) in result:
    #     if num and num > mean:
    #         comment_id.add(id)
    #
    # print(len(comment_id))










        # read_set = set()
        # last = 0
        # for i in aa:
        #     for j in range(0, len(read_map[i])):
        #         if read_map[i][j] > idx_read_list[i-1]:
        #             read_set.add(read_id[i][j])
        #     print('占比', (len(read_set) - last) / len(read_map[i]))
        #     last = len(read_set)
        #
        # read_set2 = set()
        #
        # sql = "SELECT id FROM test WHERE readnum > (select ROUND(sum(readnum)/COUNT(*),4) FROM test WHERE readnum !='') "
        # result = dbutil.query_with_sql(conn, sql)
        #
        # for (id,) in result:
        #     read_set2.add(id)
        #
        # print(len(read_set)/8789)
        # print(len(read_set2)/8789)
        # venn2([read_set, read_set2], set_labels=('read_mean_with_index', 'read_mean_no_index'))
        # plt.show()



    # 阅读量
    # plt.scatter(list(range(0,len(read_map[1]))), read_map[1], color='red', label='1')
    # plt.scatter(list(range(0,len(read_map[2]))), read_map[2], color='skyblue', label='2')
    # plt.scatter(list(range(0,len(read_map[3]))), read_map[3], color='blue', label='3')
    # plt.scatter(list(range(0,len(read_map[4]))), read_map[4], color='yellow', label='4')
    # plt.scatter(list(range(0,len(read_map[5]))), read_map[5], color='orange', label='5')
    # plt.scatter(list(range(0,len(read_map[6]))), read_map[6], color='purple', label='6')
    # plt.scatter(list(range(0,len(read_map[7]))), read_map[7], color='cyan', label='7')
    # plt.scatter(list(range(0,len(read_map[8]))), read_map[8], color='green', label='8')
    # plt.legend()
    # plt.show()

    # 点赞量
    # plt.scatter(list(range(0,len(like_map[1]))), like_map[1], color='red', label='1')
    # plt.scatter(list(range(0,len(like_map[2]))), like_map[2], color='skyblue', label='2')
    # plt.scatter(list(range(0,len(like_map[3]))), like_map[3], color='blue', label='3')
    # plt.scatter(list(range(0,len(like_map[4]))), like_map[4], color='yellow', label='4')
    # plt.scatter(list(range(0,len(like_map[5]))), like_map[5], color='orange', label='5')
    # plt.scatter(list(range(0,len(like_map[6]))), like_map[6], color='purple', label='6')
    # plt.scatter(list(range(0,len(like_map[7]))), like_map[7], color='cyan', label='7')
    # plt.scatter(list(range(0,len(like_map[8]))), like_map[8], color='green', label='8')
    # plt.legend()
    # plt.show()












