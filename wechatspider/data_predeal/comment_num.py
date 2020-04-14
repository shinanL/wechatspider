import time

import pymysql

from common import dbutil
# import logging
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
# logging.getLogger().setLevel(logging.INFO)

"""
微信公众号基础信息统计分析：
    评论随时间变化图，评论统计分布图
    评论点赞量随时间变化图，评论点赞量统计分布图

"""
START_TIME = 1546272000
END_TIME = 1577808000
conn = dbutil.connectdb_wechatcluster()

# 平均评论量 6
# 平均评论点赞量 933
# 没有评论的2463


def comment_to_table():
    """
    content表评论数据写入评论表
    :return:
    """
    discusses = []

    sql = "SELECT biz, contenturl,  title, datetime,`comment` FROM content order by datetime"
    result, rowcount = dbutil.query_with_sql_rowcount(conn, sql)
    for (biz, contenturl,  title, datetime, comment) in result:
        if len(comment) > 2:
            comment = comment[2:len(comment) - 2]
            aa = comment.split('}, {')
            comment_list = []
            for a in aa:
                a = "{%s}" % a
                comment_list.append(a)
            for discuss in comment_list:
                comment_like = 0
                di = eval(discuss)  # 字符串转数组，该函数不安全
                tmp = di.get('elected')  # 评论点赞量也有过万的,在数据持久化的时候，'elected'存放的数据不太规范，有String类型，把无数据的当做0整型数据存放了
                if isinstance(tmp, str) and '万' in tmp:
                    print('评论点赞量过万： %s' % discuss)
                    comment_like += float(tmp.split('万')[0]) * 10000
                else:
                    comment_like += int(tmp)
                # print('评论点赞量：%d' % comment_like)
                nickname = di.get('nickname')
                comment0 = di.get('comment')
                single = {
                            'biz' : biz,
                            'contenturl': contenturl,
                            'title': title,
                            'datetime': datetime,
                            'comment': comment0,
                            'nickname': nickname,
                            'commentlike': comment_like
                        }
                discusses.append(single)

    dbutil.insert_by_many_comment(conn, discusses)


def comment_vary_with_time(figurename):
    """
    评论随时间变化图，评论统计分布图
    评论点赞量随时间变化图，评论点赞量统计分布图
    :param figurename:
    :return:
    """
    discusses = []
    commentlike = []

    sql = "SELECT `comment` FROM test order by datetime"
    result, rowcount = dbutil.query_with_sql_rowcount(conn, sql)
    for (comment,) in result:
        if len(comment) > 2:
            comment = comment[2:len(comment) - 2]
            aa = comment.split('}, {')
            comment_list = []
            for a in aa:
                a = "{%s}" % a
                comment_list.append(a)

            discusses.append(len(comment_list))

            comment_like = len(comment_list)
            for discuss in comment_list:
                # print(discuss)
                di = eval(discuss)  # 字符串转数组，该函数不安全
                tmp = di.get('elected')  # 评论点赞量也有过万的,在数据持久化的时候，'elected'存放的数据不太规范，有String类型，把无数据的当做0整型数据存放了
                if isinstance(tmp, str) and '万' in tmp:
                    print('评论点赞量过万： %s' % discuss)
                    comment_like += float(tmp.split('万')[0]) * 10000
                else:
                    comment_like += int(tmp)
                # print('评论点赞量：%d' % comment_like)
            commentlike.append(comment_like)
        else:
            discusses.append(0)
            commentlike.append(0)

    mean_commentnum = int(sum(discusses) / rowcount)
    mean_commentlikenum = int(sum(commentlike) / rowcount)
    print('平均评论量    ', mean_commentnum)
    print('平均评论点赞量  ', mean_commentlikenum)

    # 开始画图  评论随时间变化图
    x = list(range(0, len(discusses)))
    plt.title('Comment Vary With Time')
    plt.plot(x, discusses, color='skyblue', label='comment')
    # plt.scatter(x, discusses, color='skyblue', label='comment')
    plt.legend()  # 显示图例
    plt.savefig('%s_comment_vary.png' % figurename)
    # plt.show()
    plt.close()

    # 开始画图  评论点赞量随时间变化图
    plt.title('CommentLike Vary With Time')
    # plt.scatter(x, commentlike, color='skyblue', label='comment')
    plt.plot(x, commentlike, color='blue', label='comment like')
    plt.legend()  # 显示图例
    plt.savefig('%s_comment_like_vary.png' % figurename)
    # plt.show()
    plt.close()



def comment_vary_with_time(figurename):
    """
    评论随时间变化图，评论统计分布图
    评论点赞量随时间变化图，评论点赞量统计分布图
    :param figurename:
    :return:
    """
    discusses = []
    commentlike = []

    sql = "SELECT `comment` FROM test order by datetime"
    result, rowcount = dbutil.query_with_sql_rowcount(conn, sql)
    for (comment,) in result:
        if len(comment) > 2:
            comment = comment[2:len(comment) - 2]
            aa = comment.split('}, {')
            comment_list = []
            for a in aa:
                a = "{%s}" % a
                comment_list.append(a)

            discusses.append(len(comment_list))

            comment_like = len(comment_list)
            for discuss in comment_list:
                # print(discuss)
                di = eval(discuss)  # 字符串转数组，该函数不安全
                tmp = di.get('elected')  # 评论点赞量也有过万的,在数据持久化的时候，'elected'存放的数据不太规范，有String类型，把无数据的当做0整型数据存放了
                if isinstance(tmp, str) and '万' in tmp:
                    print('评论点赞量过万： %s' % discuss)
                    comment_like += float(tmp.split('万')[0]) * 10000
                else:
                    comment_like += int(tmp)
                # print('评论点赞量：%d' % comment_like)
            commentlike.append(comment_like)
        else:
            discusses.append(0)
            commentlike.append(0)

    mean_commentnum = int(sum(discusses) / rowcount)
    mean_commentlikenum = int(sum(commentlike) / rowcount)
    print('平均评论量    ', mean_commentnum)
    print('平均评论点赞量  ', mean_commentlikenum)

    # 开始画图  评论随时间变化图
    x = list(range(0, len(discusses)))
    plt.title('Comment Vary With Time')
    plt.plot(x, discusses, color='skyblue', label='comment')
    # plt.scatter(x, discusses, color='skyblue', label='comment')
    plt.legend()  # 显示图例
    plt.savefig('%s_comment_vary.png' % figurename)
    # plt.show()
    plt.close()

    # 开始画图  评论点赞量随时间变化图
    plt.title('CommentLike Vary With Time')
    # plt.scatter(x, commentlike, color='skyblue', label='comment')
    plt.plot(x, commentlike, color='blue', label='comment like')
    plt.legend()  # 显示图例
    plt.savefig('%s_comment_like_vary.png' % figurename)
    # plt.show()
    plt.close()


def comment_vary_with_time(figurename):
    """
    评论随时间变化图，评论统计分布图
    评论点赞量随时间变化图，评论点赞量统计分布图
    :param figurename:
    :return:
    """
    discusses = []
    commentlike = []

    sql = "SELECT `comment` FROM test order by datetime"
    result, rowcount = dbutil.query_with_sql_rowcount(conn, sql)
    for (comment,) in result:
        if len(comment) > 2:
            comment = comment[2:len(comment) - 2]
            aa = comment.split('}, {')
            comment_list = []
            for a in aa:
                a = "{%s}" % a
                comment_list.append(a)

            discusses.append(len(comment_list))

            comment_like = len(comment_list)
            for discuss in comment_list:
                # print(discuss)
                di = eval(discuss)  # 字符串转数组，该函数不安全
                tmp = di.get('elected')  # 评论点赞量也有过万的,在数据持久化的时候，'elected'存放的数据不太规范，有String类型，把无数据的当做0整型数据存放了
                if isinstance(tmp, str) and '万' in tmp:
                    print('评论点赞量过万： %s' % discuss)
                    comment_like += float(tmp.split('万')[0]) * 10000
                else:
                    comment_like += int(tmp)
                # print('评论点赞量：%d' % comment_like)
            commentlike.append(comment_like)
        else:
            discusses.append(0)
            commentlike.append(0)

    mean_commentnum = int(sum(discusses) / rowcount)
    mean_commentlikenum = int(sum(commentlike) / rowcount)
    print('平均评论量    ', mean_commentnum)
    print('平均评论点赞量  ', mean_commentlikenum)

    # 开始画图  评论随时间变化图
    x = list(range(0, len(discusses)))
    plt.title('Comment Vary With Time')
    plt.plot(x, discusses, color='skyblue', label='comment')
    # plt.scatter(x, discusses, color='skyblue', label='comment')
    plt.legend()  # 显示图例
    plt.savefig('%s_comment_vary.png' % figurename)
    # plt.show()
    plt.close()

    # 开始画图  评论点赞量随时间变化图
    plt.title('CommentLike Vary With Time')
    # plt.scatter(x, commentlike, color='skyblue', label='comment')
    plt.plot(x, commentlike, color='blue', label='comment like')
    plt.legend()  # 显示图例
    plt.savefig('%s_comment_like_vary.png' % figurename)
    # plt.show()
    plt.close()


def comment_vary_with_every_punish(figurename):
    """
        评论随每次发布时间变化图
        评论点赞量随每次发布时间变化图
        :param figurename:
        :return:
    """
    discusses = []
    commentlike = []
    date = []

    sql = "SELECT distinct(datetime) FROM test order by datetime"
    result, rowcount = dbutil.query_with_sql_rowcount(conn, sql)

    for (datetime,) in result:
        date.append(datetime)
        sql2 = "SELECT `comment` FROM test where datetime= %d " % datetime
        result2, rowcount2 = dbutil.query_with_sql_rowcount(conn, sql2)
        discuss_count = 0
        comment_like = 0
        for (comment,) in result2:
            if len(comment) > 2:
                comment = comment[2:len(comment) - 2]
                aa = comment.split('}, {')
                comment_list = []
                for a in aa:
                    a = "{%s}" % a
                    comment_list.append(a)
                discuss_count += len(comment_list)

                comment_like = len(comment_list)  # 每个评论看成一次点赞，这个权重可以调整
                for discuss in comment_list:
                    # print(discuss)
                    di = eval(discuss)  # 字符串转数组，该函数不安全
                    tmp = di.get('elected')  # 评论点赞量也有过万的,在数据持久化的时候，'elected'存放的数据不太规范，有String类型，把无数据的当做0整型数据存放了
                    if isinstance(tmp, str) and '万' in tmp:
                        print('评论点赞量过万： %s' % discuss)
                        comment_like += float(tmp.split('万')[0]) * 10000
                    else:
                        comment_like += int(tmp)
                    # print('评论点赞量：%d' % comment_like)
        discusses.append(discuss_count)
        commentlike.append(comment_like)

    mean_commentnum = int(sum(discusses) / len(discusses))
    mean_commentlikenum = int(sum(commentlike) / len(commentlike))
    print('平均评论量    ', mean_commentnum)
    print('平均评论点赞量  ', mean_commentlikenum)

    # 开始画图  评论随时间变化图
    x = date
    plt.title('Comment Vary With Time')
    plt.plot(x, discusses, color='skyblue', label='comment')
    # plt.scatter(x, discusses, color='skyblue', label='comment')
    plt.legend()  # 显示图例
    plt.savefig('%s_comment_vary_with_punish.png' % figurename)
    # plt.show()
    plt.close()

    # 开始画图  评论点赞量随时间变化图
    plt.title('CommentLike Vary With Time')
    # plt.scatter(x, commentlike, color='skyblue', label='comment')
    plt.plot(x, commentlike, color='blue', label='comment like')
    plt.legend()  # 显示图例
    plt.savefig('%s_comment_like_vary_with_punish.png' % figurename)
    # plt.show()
    plt.close()


def comment_distribute(figurename):
    """
    评论统计分布图、评论点赞量统计分布图
    :param figurename:
    :return:
    """
    discusses = []
    commentlike = []

    sql = "SELECT `comment` FROM test order by datetime"
    result, rowcount = dbutil.query_with_sql_rowcount(conn, sql)
    for (comment,) in result:
        if len(comment) > 2:
            comment = comment[2:len(comment) - 2]
            aa = comment.split('}, {')
            comment_list = []
            for a in aa:
                a = "{%s}" % a
                comment_list.append(a)

            discusses.append(len(comment_list))

            comment_like = len(comment_list)
            for discuss in comment_list:
                # print(discuss)
                di = eval(discuss)  # 字符串转数组，该函数不安全
                tmp = di.get('elected')  # 评论点赞量也有过万的,在数据持久化的时候，'elected'存放的数据不太规范，有String类型，把无数据的当做0整型数据存放了
                if isinstance(tmp, str) and '万' in tmp:
                    print('评论点赞量过万： %s' % discuss)
                    comment_like += float(tmp.split('万')[0]) * 10000
                else:
                    comment_like += int(tmp)
                # print('评论点赞量：%d' % comment_like)
            commentlike.append(comment_like)
        else:
            discusses.append(0)
            commentlike.append(0)

    mean_commentnum = int(sum(discusses) / rowcount)
    mean_commentlikenum = int(sum(commentlike) / rowcount)
    print('平均评论量    ', mean_commentnum)
    print('平均评论点赞量  ', mean_commentlikenum)

    # 评论统计分布图
    map_comment = {}
    for i in discusses:
        map_comment.setdefault(i, 0)
        map_comment[i] += 1
    # 评论点赞统计分布图
    map_comment_like = {}
    for i in commentlike:
        map_comment_like.setdefault(i, 0)
        map_comment_like[i] += 1

    x = []
    y = []
    for i in sorted(map_comment):
        x.append(i)
        y.append(map_comment[i])

    plt.title('Comment Distribute')
    plt.plot(x, y, color='skyblue', label='comment')
    # plt.scatter(x, discusses, color='skyblue', label='comment')
    plt.legend()  # 显示图例
    plt.savefig('%s_comment_distribute.png' % figurename)
    # plt.show()
    plt.close()

    # 评论点赞量统计分布图
    x = []
    y = []
    for i in sorted(map_comment_like):
        print((i, map_comment_like[i]), end=' ')
        x.append(i)
        y.append(map_comment_like[i])
    plt.title('CommentLike Distribute')
    # plt.scatter(x, commentlike, color='skyblue', label='comment')
    plt.plot(x, y, color='blue', label='comment like')
    plt.legend()  # 显示图例
    plt.savefig('%s_comment_like_distribute.png' % figurename)
    # plt.show()
    plt.close()


if __name__ == '__main__':
    # comment_to_table()
    # comment_distribute('test')


