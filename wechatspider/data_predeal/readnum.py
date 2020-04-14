import time
from common import dbutil
# import logging
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
# logging.getLogger().setLevel(logging.INFO)

"""
微信公众号基础信息统计分析：
    1、包括阅读量统计分析
    2、点赞量统计分析
    3、评论统计分析
    4、评论点赞量统计分析
"""
START_TIME = 1546272000
END_TIME = 1577808000
conn = dbutil.connectdb_wechatcluster()


if __name__ == '__main__':

    read = []
    min_readnum = 0
    max_readnum = 0
    total_readnum = 0
    mean_readnum = 0

    like = []
    min_likenum = 0
    max_likenum = 0
    total_likenum = 0
    mean_likenum = 0

    discusses = []
    min_commentnum = 0
    max_commentnum = 0
    total_commentnum = 0
    mean_commentnum = 0

    commentlike = []
    min_commentlike = 0
    max_commentlike = 0
    total_commentlikenum = 0
    mean_commentlikenum = 0

    date = []

    sql = "SELECT biz, contenturl, readnum, likenum, `comment`, datetime FROM test order by datetime"
    result, rowcount = dbutil.query_with_sql_rowcount(conn, sql)
    for(biz, contenturl, readnum, likenum, comment, datetime) in result:
        print('链接：%s' % contenturl)
        # 转换成localtime
        time_local = time.localtime(datetime)
        # 转换成时间格式
        time_format = time.strftime("%Y-%m-%d %H:%M", time_local)
        date.append(time_format)
        if readnum == "":
            print('阅读量为0')
            readnum = 0
        elif '万' in readnum:
            readnum = float(readnum.split('万')[0]) * 10000  # 阅读量过万的
        readnum = int(readnum)
        read.append(readnum)
        print('阅读量：%d' % readnum)
        total_readnum += readnum
        min_readnum = min(min_readnum, readnum)
        max_readnum = max(max_readnum, readnum)

        if likenum == '':
            print('点赞量为0')
            likenum = 0
        elif '万' in likenum:
            likenum = float(likenum.split('万')[0])*10000
        likenum = int(likenum)
        like.append(likenum)
        print('点赞量 %d' % likenum)
        total_likenum += likenum
        min_lienum = min(min_likenum, likenum)
        max_likenum = max(max_likenum, likenum)

        if len(comment) > 2:
            comment_like = 0
            comment = comment[2:len(comment) - 2]
            aa = comment.split('}, {')
            comment_list = []
            for a in aa:
                a = "{%s}" % a
                comment_list.append(a)

            discusses.append(len(comment_list))
            total_commentnum += len(comment_list)
            min_commentnum = min(min_commentnum, len(comment_list))
            max_commentnum = max(max_commentnum, len(comment_list))

            comment_like = 0
            for discuss in comment_list:
                # print(discuss)
                di = eval(discuss)  # 字符串转数组，该函数不安全
                tmp = di.get('elected')  # 评论点赞量也有过万的,在数据持久化的时候，'elected'存放的数据不太规范，有String类型，把无数据的当做0整型数据存放了
                if isinstance(tmp, str) and '万' in tmp:
                    print('评论点赞量过万： %s' % discuss)
                    comment_like += float(tmp.split('万')[0]) * 10000
                else:
                    comment_like += int(tmp)
                print('评论点赞量：%d' % comment_like)
            min_commentlike = min(min_commentlike, comment_like)
            max_commentlike = max(max_commentlike, comment_like)
            commentlike.append(comment_like)
            total_commentlikenum += comment_like
        else:
            discusses.append(0)
            commentlike.append(0)

    mean_readnum = int(total_readnum/rowcount)
    mean_likenum = int(total_likenum/rowcount)
    mean_commentnum = int(total_commentnum/rowcount)
    mean_commentlikenum = int(total_commentlikenum/rowcount)
    conn.close()

    # 写入文件持久化
    file = open('readinfo.txt', 'w')
    file.write('**********read**********')
    file.write('\n\n')
    file.write('min_readnum:     %d' % min_readnum)
    file.write('\n')
    file.write('max_readnum:     %d' % max_readnum)
    file.write('\n')
    file.write('total_readnum:     %d' % total_readnum)
    file.write('\n')
    file.write('mean_readnum:     %d' % mean_readnum)
    file.write('\n')
    file.write(str(read))
    file.write('\n\n')

    file.write('**********like**********')
    file.write('\n\n')
    file.write('min_likenum:     %d' % min_likenum)
    file.write('\n')
    file.write('max_likenum:     %d'% max_likenum)
    file.write('\n')
    file.write('total_likenum:     %d' % total_likenum)
    file.write('\n')
    file.write('mean_likenum:     %d' % mean_likenum)
    file.write('\n')
    file.write(str(like))
    file.write('\n\n')

    file.write('**********comment**********')
    file.write('\n\n')
    file.write('min_commentnum:     %d' % min_commentnum)
    file.write('\n')
    file.write('max_commentnum:     %d' % max_commentnum)
    file.write('\n')
    file.write('total_commentnum:     %d' % total_commentnum)
    file.write('\n')
    file.write('mean_commentnum:     %d' % mean_commentnum)
    file.write('\n')
    file.write(str(discusses))
    file.write('\n\n')

    file.write('**********commentlike**********')
    file.write('\n\n')
    file.write('min_commentlike:     %d' % min_commentlike)
    file.write('\n')
    file.write('max_commentlike:     %d' % max_commentlike)
    file.write('\n')
    file.write('total_commentlikenum:     %d' % total_commentlikenum)
    file.write('\n')
    file.write('mean_commentlikenum:     %d' % mean_commentlikenum)
    file.write('\n')
    file.write(str(commentlike))
    file.write('\n\n')

    file.write('**********date**********')
    file.write('\n\n')
    file.write(str(date))

    # 开始画图
    # plt.title('Read Information Analysis')
    #
    # plt.plot(date, read, color='green', label='read num')
    # plt.plot(date, like, color='red', label='like num')
    # plt.plot(date, discusses, color='skyblue', label='comment')
    # plt.plot(date, commentlike, color='blue', label='comment like')
    # plt.legend()  # 显示图例
    #
    # plt.xlabel('publish times')
    # plt.ylabel('rate')
    # plt.show()



