import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import linecache
from common import dbutil
from matplotlib import pyplot as plt
import numpy as np
import subprocess
from matplotlib.font_manager import FontManager
import time

conn = dbutil.connectdb_wechatcluster()
import re
import pymysql

"""
    数据预处理
"""

def update_num_of_comment_commentlike():
    # 更新content表中的评论量和点赞量
    time0 = time.time()
    sql = "SELECT id, `comment` FROM content"
    result, rowcount = dbutil.query_with_sql_rowcount(conn, sql)
    for (id, comment) in result:
        if len(comment) > 2:
            comment = comment[2:len(comment) - 2]
            aa = comment.split('}, {')
            comment_list = []
            for a in aa:
                a = "{%s}" % a
                comment_list.append(a)
            comment_like = 0
            for discuss in comment_list:
                di = eval(discuss)  # 字符串转数组，该函数不安全
                tmp = di.get('elected')  # 评论点赞量也有过万的,在数据持久化的时候，'elected'存放的数据不太规范，有String类型，把无数据的当做0整型数据存放了
                if isinstance(tmp, str) and '万' in tmp:
                    # print('评论点赞量过万： %s' % discuss)
                    comment_like += float(tmp.split('万')[0]) * 10000
                else:
                    comment_like += int(tmp)
                # print('评论点赞量：%d' % comment_like)
            sql2 = "update content set comment_num = %d, commentlike_num = %d WHERE id = %d" \
                   % (len(comment_list), comment_like, id)
            dbutil.exec_sql(conn, sql2)

    print('用时   ', time.time()-time0)


def update_readnum():
    time0 = time.time()
    sql = "select id, readnum from content where readnum like '%万%'"
    result, rowcount = dbutil.query_with_sql_rowcount(conn, sql)
    for (id, readnum) in result:
        tmp = float(readnum.split('万')[0]) * 10000
        sql2 = "update content set readnum= %s where id = %d" % (int(tmp), id)
        dbutil.exec_sql(conn, sql2)

    print('用时   ', time.time()-time0)

def write_content_to_file(table):
    """
    把文章内容写入文件
    :return:
    """
    time0 = time.time()
    sql = "SELECT id,content FROM %s" % table
    result = dbutil.query_with_sql(conn, sql)
    file = open("content.txt", "w")
    for (id, content) in result:
        if content:
            file.write(content)
            file.write("\n---------------------------\n")
    file.close()
    print('用时   ', time.time()-time0)


def write_content_to_file_with_sql(sql):
    """
    把文章内容写入文件
    :return:
    """
    time0 = time.time()
    result = dbutil.query_with_sql(conn, sql)
    file = open("content.txt", "w")
    for (content,) in result:
        if content:
            file.write(content)
            file.write("\n")
    file.close()
    print('用时   ', time.time()-time0)


def delete_white_line():
    """
    去除内容冗余的空行和前后空格
    """
    time0 = time.time()
    sql = "SELECT id,digest FROM content"
    result = dbutil.query_with_sql(conn, sql)
    for (id, digest) in result:
        # 不为空
        if digest:
            # 去除多余的空行，只保留一个空行
            content = digest.lstrip("\n").rstrip("\n")
            content = re.sub("\n{2,}", "\n", content)
            digest = content.strip()
        sql = "update content set digest = '{}' where id = {}"\
            .format(pymysql.escape_string(digest), id)
        dbutil.exec_sql(conn, sql)
        # print(digest)
    print('用时   ', time.time()-time0)


def delete_white_space():
    """
    去除内容冗余的空行和前后空格
    """
    time0 = time.time()
    sql = "SELECT id,strong_content, color_content FROM content"
    result = dbutil.query_with_sql(conn, sql)
    for (id, strong_content, color_content) in result:
        # 不为空
        if strong_content:
            # 去除多余的空行，只保留一个空行
            content = strong_content.lstrip("。").rstrip("。")
            content = re.sub("。{2,}", "。", content)
            strong_content = content.strip()
        if color_content:
            # 去除多余的空行，只保留一个空行
            content = color_content.lstrip("。").rstrip("。")
            content = re.sub("。{2,}", "。", content)
            color_content = content.strip()
        sql = "update content set strong_content = '{}' , color_content='{}' where id = {}"\
            .format(pymysql.escape_string(strong_content), pymysql.escape_string(color_content), id)
        dbutil.exec_sql(conn, sql)
        # print(digest)
    print('用时   ', time.time()-time0)

if __name__ == '__main__':

    # update_num_of_comment_commentlike()

    # update_readnum()
    # sql = "SELECT DISTINCT(content) FROM test WHERE content!='' and LENGTH(content) < 30 ORDER BY content"
    # write_content_to_file_with_sql(sql)
    delete_white_line()
    # delete_white_space()
