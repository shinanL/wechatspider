import time

from sklearn import preprocessing

from common import dbutil,pltutil
from matplotlib.font_manager import FontProperties
import numpy as np
import matplotlib.pyplot as plt
import collections
# from matplotlib_venn import venn2

from matplotlib.font_manager import FontProperties
font_set = FontProperties(fname='/Library/Fonts/Songti.ttc', size=15)
font_set2 = FontProperties(fname='/Library/Fonts/Songti.ttc', size=12)
plt.rcParams['axes.unicode_minus'] = False



"""
微信公众号阅读量统计分析
"""
conn = dbutil.connectdb_wechatcluster()


def drag_index_to_tabel():
    a = []

    sql = "SELECT id, contenturl FROM content"
    result, rowcount = dbutil.query_with_sql_rowcount(conn, sql)
    for (id, contenturl) in result:
        index = contenturl.find('&idx=')
        idx = int(contenturl[index + 5:index + 6])
        tmp = {
            'id': id,
            'idx':idx
        }
        a.append(tmp)
        sql = 'update content set idx= %d where id = %d' %(idx, id)
        dbutil.exec_sql(conn, sql)


def index_totol_infection():
    x = list(range(1,9))
    # sql = "SELECT ROUND(AVG(readnum)/10,1) a, ROUND(AVG(likenum)) b FROM content GROUP BY idx ORDER BY idx"
    sql = "SELECT ROUND(AVG(readnum)) a, ROUND(AVG(likenum)) b, ROUND(AVG(comment_num)) c, ROUND(AVG(commentlike_num)) d FROM content GROUP BY idx ORDER BY idx"
    result, rowcount = dbutil.query_with_sql_rowcount(conn, sql)
    readnum = []
    likenum = []
    commentnum = []
    commentlikenum = []
    for(a, b, c, d) in result:
        readnum.append(a)
        likenum.append(b)
        commentnum.append(c)
        commentlikenum.append(d)

    scaler = preprocessing.MinMaxScaler()
    y1 = scaler.fit_transform(np.array(readnum).reshape(-1, 1))
    y2 = scaler.fit_transform(np.array(likenum).reshape(-1, 1))
    y3 = scaler.fit_transform(np.array(commentnum).reshape(-1, 1))
    y4 = scaler.fit_transform(np.array(commentlikenum).reshape(-1, 1))

    # 标题
    plt.title('索引对微文各项数据的影响', fontproperties=font_set)

    # 横坐标描述
    plt.xlabel('索引位置', fontproperties=font_set)

    # 纵坐标描述
    # plt.ylabel('', fontproperties=font_set)


    plt.plot(x, y1, color='green', label='阅读量')
    plt.plot(x, y2, color='red', label='点赞量')
    plt.plot(x, y3, color='skyblue', label='评论量')
    plt.plot(x, y4, color='blue', label='评论点赞量')
    # plt.legend(prop=font_set1, loc="upper right", fontsize=8)
    plt.legend(prop=font_set2, loc="upper right")

    plt.savefig('./索引对微文各项数据的影响')

    plt.show()

    # pltutil.plot/_single_figure(x, readnum, "索引位置对阅读量的影响", "索引位置", "阅读量/万", "total_read")





def index_total_biz():
    """
    索引位置对所有公众号的影响统计：计算不同索引位置的平均阅读量和点赞量
    :return:
    """
    # 索引位置最长8篇
    read_map = {}  # 阅读量
    read_id = {}  # 文章标识
    like_map = {}  # 点赞量

    sql = "SELECT id, contenturl, readnum, likenum, title, digest FROM content"
    result, rowcount = dbutil.query_with_sql_rowcount(conn, sql)
    for (id, contenturl, readnum, likenum, title, digest) in result:
        index = contenturl.find('&idx=')
        idx = int(contenturl[index + 5:index + 6])
        read_map.setdefault(idx, [])
        read_map[idx].append(readnum)
        read_id.setdefault(idx, [])
        read_id[idx].append(id)
        like_map.setdefault(idx, [])
        like_map[idx].append(likenum)

    idx_read_list = []  # 索引位置平均阅读量
    idx_like_list = []  # 索引位置平均点赞量
    x = list(range(1, len(read_map) + 1))

    for i in x:
        idx_read_list.append(round(sum(read_map[i]) / (len(read_map[i]) * 10000), 2))  # 以万为单位
        idx_like_list.append(round(sum(like_map[i]) / len(like_map[i]), 1))

    # 分布图
    pltutil.plot_single_figure(x, idx_read_list, "索引位置对阅读量的影响", "索引位置", "阅读量/万", "total_read")
    pltutil.plot_single_figure(x, idx_like_list, "索引位置对点赞量的影响", "索引位置", "点赞量", "total_like")


def index_each_biz():
    """
    索引位置对各个公众号的影响：计算不同索引位置的平均阅读量和点赞量
    :return:
    """
    sql = "select biz, nickname from bizinfo"
    result = dbutil.query_with_sql(conn, sql)

    for (biz, nickname) in result:
        print("公众号昵称", nickname)
        read_map = {}  # 阅读量
        read_id = {}  # 文章标识
        like_map = {}  # 点赞量

        sql2 = "SELECT id, contenturl, readnum, likenum, title, digest FROM content where biz = '%s'" % biz
        result2, rowcount = dbutil.query_with_sql_rowcount(conn, sql2)
        for (id, contenturl, readnum, likenum, title, digest) in result2:
            index = contenturl.find('&idx=')
            idx = int(contenturl[index + 5:index + 6])
            read_map.setdefault(idx, [])
            read_map[idx].append(readnum)
            read_id.setdefault(idx, [])
            read_id[idx].append(id)
            like_map.setdefault(idx, [])
            like_map[idx].append(likenum)

        idx_read_list = []  # 索引位置平均阅读量
        idx_like_list = []  # 索引位置平均点赞量
        x = list(range(1, len(read_map) + 1))

        for i in x:
            idx_read_list.append(round(sum(read_map[i]) / (len(read_map[i]) * 10000), 2))  # 以万为单位
            idx_like_list.append(round(sum(like_map[i]) / len(like_map[i]), 1))

        # 分布图
        plot_single_figure(x, idx_read_list, "索引位置对阅读量的影响", "索引位置", "阅读量/万", nickname + "_read")
        plot_single_figure(x, idx_like_list, "索引位置对点赞量的影响", "索引位置", "点赞量", nickname + "_like")


if __name__ == '__main__':
    # index_each_biz()
    # index_total_biz()
    # drag_index_to_tabel()
    index_totol_infection()




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












