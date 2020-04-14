
from common import dbutil
from matplotlib import pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter
from matplotlib.font_manager import FontProperties
font_set = FontProperties(fname='/Library/Fonts/Songti.ttc', size=15)

conn = dbutil.connectdb_wechatcluster()


def millions(x, pos):
    'The two args are the value and tick position'
    return '$%1.1fM' % (x * 1e-6)


if __name__ == '__main__':

    sql = "SELECT nickname, sum(num) as total from advisement GROUP BY nickname ORDER BY sum(num)"
    result, rowcount = dbutil.query_with_sql_rowcount(conn, sql)
    names = []
    nums = []
    for (nickname, total) in result:
        names.append(nickname)
        nums.append(total)
    #
    # 标题
    plt.title("各公众号广告植入", fontproperties=font_set)

    # 横坐标描述
    plt.xlabel("公众号昵称", fontproperties=font_set)

    # 纵坐标描述
    plt.ylabel("2019广告植入量", fontproperties=font_set)

    x = np.arange(18)


    # # 设置数字标签
    for a, b in zip(x, nums):
        plt.text(a, b, b, ha='center', va='bottom', fontsize=13)
    #
    # # plt.hist(nums, bins=40, normed=0, facecolor="blue", edgecolor="black", alpha=0.7)
    # # plt.bar(names, nums, fc='b')
    # x = np.arange(len(names))
    # print(len(x))
    # print(x)
    # print(len(nums))
    # plt.bar(x, nums, fc='b')
    # plt.xticks(x, np.asarray(names))
    # # plt.bar(range(18), nums, fc='b', tick_label=names)
    # # plt.bar(range(len(nums)), nums, fc='b', tick_label=names)
    #
    # plt.show()



    x = np.arange(18)
    # money = [1.5e5, 2.5e6, 5.5e6, 2.0e7]





    # formatter = FuncFormatter(millions)

    # fig, ax = plt.subplots()
    # ax.yaxis.set_major_formatter(formatter)
    plt.bar(x, nums)
    # plt.margins(0.1)
    # plt.xticks(x, names, rotation='vertical')
    plt.ylim(0, 500)
    # plt.xli m(-0.5, 18)
    plt.xticks(x, names, rotation=80, fontproperties=font_set, fontsize=12)
    plt.tight_layout()
    plt.savefig('advertisement.png')
    plt.show()












