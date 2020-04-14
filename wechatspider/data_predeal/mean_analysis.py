
from common import dbutil
from matplotlib_venn import venn2
from matplotlib_venn import venn3
from matplotlib import pyplot as plt

conn = dbutil.connectdb_wechatcluster()

def comment_cross_commentlike():
    """
    超过均值的评论和评论点赞量交集、并集
    :return:
    """
    map_discusses = {}
    map_commentlike = {}

    sql = "SELECT id, `comment` FROM test order by datetime"
    result, rowcount = dbutil.query_with_sql_rowcount(conn, sql)
    for (id, comment) in result:
        if len(comment) > 2:
            comment = comment[2:len(comment) - 2]
            aa = comment.split('}, {')
            comment_list = []
            for a in aa:
                a = "{%s}" % a
                comment_list.append(a)

            map_discusses[id] = len(comment_list)

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
            map_commentlike[id] = comment_like
        else:
            map_discusses[id] = 0
            map_commentlike[id] = 0

    mean_commentnum = int(sum(map_discusses.values()) / rowcount)
    mean_commentlikenum = int(sum(map_commentlike.values()) / rowcount)
    print('平均评论量    ', mean_commentnum)
    print('平均评论点赞量  ', mean_commentlikenum)

    discusses_set = set()
    for i in map_discusses:
        if map_discusses[i] > mean_commentnum:
            discusses_set.add(i)

    commentlike_set = set()
    for i in map_commentlike:
        if map_commentlike[i] > mean_commentlikenum:
            commentlike_set.add(i)

    print('大于均值的评论   ', len(discusses_set))
    print('大于均值的评论点赞量   ', len(commentlike_set))
    cross = len(discusses_set & commentlike_set)
    print('评论和评论点赞量交集   ', cross)
    union = len(discusses_set | commentlike_set)
    print('评论和评论点赞量并集   ', union)
    print('占比   ', cross / union)

    # # 画venn图
    # plt.figure()
    # venn2(subsets=[discusses_set, commentlike_set], set_labels=('comment', 'commentlike'))
    # plt.show()
    return discusses_set, commentlike_set


def read_cross_like():
    """
    超过均值的阅读量和点赞量交集、并集
    :return:
    """
    read_set = set()

    sql = "SELECT id FROM test WHERE readnum > (select ROUND(sum(readnum)/COUNT(*),4) FROM test WHERE readnum !='') "
    result = dbutil.query_with_sql(conn, sql)

    for (id,) in result:
        read_set.add(id)

    like_set = set()

    sql = "SELECT id FROM test WHERE likenum > (SELECT sum(likenum)/count(*) FROM test)"
    result = dbutil.query_with_sql(conn, sql)

    for (id,) in result:
        like_set.add(id)

    print(read_set)
    print('大于均值阅读量  ', len(read_set))
    print('大于均值点赞量  ', len(like_set))
    cross = len(read_set & like_set)
    print('阅读和点赞量交集   ', cross)
    union = len(read_set | like_set)
    print('阅读和点赞量并集   ', union)
    print('阅读和点赞量占比   ', cross / union)

    # 画venn图
    # plt.figure(figsize=(4, 4))
    # venn2(subsets=[read_set, like_set], set_labels=('read', 'like'))
    # plt.show()
    return read_set, like_set


if __name__ == '__main__':
    read_set, like_set = read_cross_like()
    comment_set, commentlike_set = comment_cross_commentlike()

    total_set = read_set | like_set | comment_set | like_set
    print('大于均值的四个集合总量     ', len(total_set))

    cross = len(read_set & comment_set)
    print('阅读和评论量交集   ', cross)
    union = len(read_set | comment_set)
    print('阅读和评论量并集   ', union)
    print('阅读和评论量占比   ', cross / union)

    cross = len(read_set & commentlike_set)
    print('阅读和评论量点赞量交集   ', cross)
    union = len(read_set | commentlike_set)
    print('阅读和评论量点赞量并集   ', union)
    print('阅读和评论量点赞量占比   ', cross / union)

    cross = len(like_set & comment_set)
    print('点赞量和评论量交集   ', cross)
    union = len(like_set | comment_set)
    print('点赞量和评论量并集   ', union)
    print('点赞量和评论量占比   ', cross / union)

    # 阅读量高、点赞和评论少的，以为头条位置的引流功能，但是实验发现，头条位置50%1|2|3|4位的占比是68%
    # three_set = like_set | comment_set | like_set
    # diff = read_set - three_set
    # print(diff)
    # print(len(diff))
    # count = 0
    # for i in diff:
    #     sql = "select contenturl, digest from test where id = %d" % i
    #     result = dbutil.query_with_sql_one(conn, sql)
    #     contenturl = result[0]
    #     index = contenturl.find('&idx=')
    #     idx = contenturl[index+5:index+6]
    #     if int(idx) < 5:
    #         count += 1
    #         print(contenturl)
    #         print(result[1])
    #     else:
    #         pass
    # print(count)


    # A = [read_set, like_set, comment_set, commentlike_set]
    # B = ['read', 'like', 'comment', 'commentlike']
    #
    # # 画venn图 两两分析
    # plt.figure(figsize=(4, 4))
    # venn2(subsets=[A[0], A[1]], set_labels=(B[0], B[1]))
    # plt.savefig('%s_%s.png' % (B[0], B[1]))
    # plt.close()
    # # plt.show()
    #
    # plt.figure(figsize=(4, 4))
    # venn2(subsets=[A[0], A[2]], set_labels=(B[0], B[2]))
    # plt.savefig('%s_%s.png' % (B[0], B[2]))
    # plt.close()
    # # plt.show()
    #
    # plt.figure(figsize=(4, 4))
    # venn2(subsets=[A[0], A[3]], set_labels=(B[0], B[3]))
    # plt.savefig('%s_%s.png' % (B[0], B[3]))
    # plt.close()
    # # plt.show()
    #
    # plt.figure(figsize=(4, 4))
    # venn2(subsets=[A[1], A[2]], set_labels=(B[1], B[2]))
    # plt.savefig('%s_%s.png' % (B[1], B[2]))
    # plt.close()
    # # plt.show()
    #
    # plt.figure(figsize=(4, 4))
    # venn2(subsets=[A[1], A[3]], set_labels=(B[1], B[3]))
    # plt.savefig('%s_%s.png' % (B[1], B[3]))
    # plt.close()
    # # plt.show()
    #
    # plt.figure(figsize=(4, 4))
    # venn2(subsets=[A[2], A[3]], set_labels=(B[2], B[3]))
    # plt.savefig('%s_%s.png' % (B[2], B[3]))
    # plt.close()
    # # plt.show()
    #
    # # 三三分析
    plt.figure(figsize=(4, 4))
    venn3(subsets=[A[0], A[1], A[2]], set_labels=(B[0], B[1], B[2]))
    plt.savefig('%s_%s_%s.png' % (B[0], B[1], B[2]))
    plt.close()
    # plt.show()
    #
    # plt.figure(figsize=(4, 4))
    # venn3(subsets=[A[0], A[1], A[3]], set_labels=(B[0], B[1], B[3]))
    # plt.savefig('%s_%s_%s.png' % (B[0], B[1], B[3]))
    # plt.close()
    # # plt.show()
    #
    # plt.figure(figsize=(4, 4))
    # venn3(subsets=[A[1], A[2], A[3]], set_labels=(B[1], B[2], B[3]))
    # plt.savefig('%s_%s_%s.png' % (B[1], B[2], B[3]))
    # plt.close()
    # # plt.show()












