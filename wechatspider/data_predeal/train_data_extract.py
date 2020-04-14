import codecs
import json
import re

from sklearn.neighbors import KernelDensity

from common import dbutil
import pandas as pd
import collections
import csv
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['savefig.dpi'] = 120 #图片像素
plt.rcParams['figure.dpi'] = 120 #分辨率

"""
读取id, title, digest, content前两段, strong_content和color content 前四句到csv文件
"""
conn = dbutil.connectdb_wechatcluster()


def extract_data():
    sql = "SELECT id, biz, title, digest, content, strong_content, color_content,`comment` FROM content WHERE datetime BETWEEN UNIX_TIMESTAMP('2019-06-01 00:00:00') and UNIX_TIMESTAMP('2019-07-01 00:00:00') "
    result = dbutil.query_with_sql(conn, sql)
    id_list = []
    biz_list = []
    title_list = []
    digest_list = []
    content_list = []
    strong_content_list = []
    color_content_list = []
    for (id, biz, title, digest, content, strong_content, color_content, comment) in result:
        if content:
            contents = content.split('\n')
            print('段落长度', len(contents))
            if len(contents) == 1:
                tmp = contents[0].split('。')
                if len(tmp) < 4:
                    content = contents[0]
                    content = re.sub("\n", "。", content)
                else:
                    content = "。".join(i for i in tmp[0:4])  # 前四句
            else:
                content = contents[0]+contents[1]  # 前两段
        id_list.append(id)
        biz_list.append(biz)
        title_list.append(title)
        digest_list.append(digest)
        content_list.append(content)
        if strong_content and len(strong_content.split('。')) > 4:
            tmp = strong_content.split('。')
            strong_content = '。'.join(i for i in tmp[0:4])
        if color_content and len(color_content.split('。')) > 4:
            tmp = color_content.split('。')
            color_content = '。'.join(i for i in tmp[0:4])
        strong_content_list.append(strong_content)
        color_content_list.append(color_content)
    dataframe = pd.DataFrame({'id': id_list, 'biz': biz_list,
                              'title': title_list, 'digest': digest_list,
                              'content': content_list, 'strong_content': strong_content_list,
                              'color_content': color_content_list})
    dataframe.to_csv("trainsix_wechat.csv", index=False, sep=',', quotechar='\"')



def extract_comment():
    sql = "SELECT id, biz, title, digest, content, strong_content, color_content,`comment` FROM content WHERE datetime BETWEEN UNIX_TIMESTAMP('2019-06-01 00:00:00') and UNIX_TIMESTAMP('2019-07-01 00:00:00') "
    result = dbutil.query_with_sql(conn, sql)
    id_list = []
    biz_list = []
    title_list = []
    digest_list = []
    content_list = []
    strong_content_list = []
    color_content_list = []
    for (id, biz, title, digest, content, strong_content, color_content, comment) in result:
        if content:
            contents = content.split('\n')
            print('段落长度', len(contents))
            if len(contents) == 1:
                tmp = contents[0].split('。')
                if len(tmp) < 4:
                    content = contents[0]
                    content = re.sub("\n", "。", content)
                else:
                    content = "。".join(i for i in tmp[0:4])  # 前四句
            else:
                content = contents[0]+contents[1]  # 前两段
        id_list.append(id)
        biz_list.append(biz)
        title_list.append(title)
        digest_list.append(digest)
        content_list.append(content)
        if strong_content and len(strong_content.split('。')) > 4:
            tmp = strong_content.split('。')
            strong_content = '。'.join(i for i in tmp[0:4])
        if color_content and len(color_content.split('。')) > 4:
            tmp = color_content.split('。')
            color_content = '。'.join(i for i in tmp[0:4])
        strong_content_list.append(strong_content)
        color_content_list.append(color_content)
    dataframe = pd.DataFrame({'id': id_list, 'biz': biz_list,
                              'title': title_list, 'digest': digest_list,
                              'content': content_list, 'strong_content': strong_content_list,
                              'color_content': color_content_list})
    dataframe.to_csv("trainsix_wechat.csv", index=False, sep=',', quotechar='\"')


def count_comment_nickname():
    dict = {}
    sql = "SELECT `comment` FROM content"
    result = dbutil.query_with_sql(conn, sql)
    for (comment,) in result:
        if len(comment) > 2:
            comment = comment[2:len(comment) - 2]
            aa = comment.split('}, {')
            comment_list = []
            for a in aa:
                a = "{%s}" % a
                comment_list.append(a)
            for discuss in comment_list:
                # print(discuss)
                di = eval(discuss)  # 字符串转数组，该函数不安全
                tmp = di.get('nickname')  # 评论点赞量也有过万的,在数据持久化的时候，'elected'存放的数据不太规范，有String类型，把无数据的当做0整型数据存放了
                dict.setdefault(tmp, 0)
                dict[tmp] += 1

    # jsObj = json.dumps(dict)
    # fileObject = open('jsonFile.json', 'w')
    # fileObject.write(jsObj)
    # fileObject.close()
    # csv_file = "nickname_output.csv"
    # csv_columns = ['Nickname', 'Count']
    # with open(csv_file, 'w') as csvfile:
    #     writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    #     writer.writeheader()
    #     for key, val in dict:
    #         writer.writerow([key, val])
    filename = "nickname_output.csv"
    with open(filename, 'w') as csv_file:
    # with open(filename, 'w', encoding='utf_8_sig') as csv_file: 或者这样
        csv_file.write(codecs.BOM_UTF8.decode())  # 不加会导致中文乱码
        writer = csv.writer(csv_file)
        for key, val in dict.items():
            writer.writerow([key, val])

    # print(len(dict))
    # count_list = sorted(dict.items(), key=lambda x: x[1], reverse=True)
    # print(count_list[:1000])

def func(pct, allvals):
    absolute = int(pct / 100. * np.sum(allvals))
    # return "{:.1f}%\n({:d})".format(pct, absolute)
    return "{:.2f}%".format(pct, absolute)


def donut_comment():
    fig, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))

    recipe = ["225 g flour",
              "90 g sugar",
              "1 egg",
              "60 g butter",
              "100 ml milk",
              "1/2 package of yeast"]

    data = [225, 90, 50, 60, 100, 5]

    wedges, texts = ax.pie(data, wedgeprops=dict(width=0.5), startangle=-40)

    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-"),
              bbox=bbox_props, zorder=0, va="center")

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1) / 2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        ax.annotate(recipe[i], xy=(x, y), xytext=(1.35 * np.sign(x), 1.4 * y),
                    horizontalalignment=horizontalalignment, **kw)

    ax.set_title("Matplotlib bakery: A donut")

    plt.show()


def analysis_comment():
    """评论数据分箱"""
    # 分组
    # bins = [0, 10,20,30,40,50,100,7000]
    # bins = [0, 5, 10, 50, 100, 7000]
    # bins = [0, 1, 2, 3, 4, 5, 10, 7000]
    # bins = [0, 1, 2, 5, 10, 7000]
    bins = [0, 1, 2, 5, 10, 1000, 7000]
    # 分箱
    df = pd.read_csv('nickname_output.csv', encoding='utf-8-sig', names=['nickname', 'count'])
    nums = df['count']
    nums_cat = pd.cut(nums, bins)
    print(pd.value_counts(nums_cat))

    pd.value_counts(nums_cat).to_excel('foo.xlsx', 'Sheet2')


    # fig, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))
    fig, ax = plt.subplots(subplot_kw=dict(aspect="equal"))

    # data = pd.DataFrame(pd.value_counts(nums_cat), ['区间','次数'])
    data = pd.value_counts(nums_cat).values
    # ingredients = ['0-5', '5-10', '>10']
    # ingredients = ['1', '2', '(2,5]', '(5-10]', '>10', '>1000']
    ingredients = ['1', '2', '(2,5]', '(5-10]', '(10,1000]', '>1000']

    wedges, texts, autotexts = ax.pie(data, autopct=lambda pct: func(pct, data),
                                      textprops=dict(color="w"),shadow=True)

    ax.legend(wedges, ingredients,
              title="reviews",
              loc="center left",
              bbox_to_anchor=(1, 0, 0.5, 1))

    plt.setp(autotexts, size=8, weight="bold")

    ax.set_title("Reviews Distribution")
    plt.savefig('Reviews_Distribution.png')
    plt.show()
    plt.clf()

    # plot pie
    # labels = ['0-5', '5-10', '10-50', '50-100', '大于100']
    # labels = ['0-5', '5-10', '>10']
    # explode = (0, 0, 0.2)
    # fig1, ax1 = plt.subplots()
    # ax1.pie(pd.value_counts(nums_cat),
    #         autopct='%1.1f%%',
    #         # fontsize=12,
    #         # figsize=(6, 6),
    #         labels=labels,
    #         # labeldistance=None
    #         explode=explode,
    #         shadow=True,
    #         startangle=90,
    #         # textprops={'size': 'smaller'},
    #         # radius=1.5
    #         # frame=True
    #          )
    # ax1.axis('equal')
    # plt.title('Authorwise distribution')
    # plt.show()



def analysis_comment_distr():
    pd.set_option('display.width', 480)  # 150，设置打印宽度
    pd.set_option('display.max_columns', None)

    df = pd.read_csv('nickname_output.csv', encoding='utf-8-sig', names=['nickname', 'count'])
    print(df.head(10))
    df_length = len(df)  # 获取数据的行数
    print('评论人次     ', df_length)
    nums = df['count']
    print(type(nums))
    mean = nums.mean()
    print('均值   ', mean)
    print('最大值  ', nums.max())
    print('中位数  ', nums.median())
    print(nums.value_counts())
    # fig, ax = plt.subplots()
    # df['count'].value_counts().plot(ax=ax, kind='bar')
    # df['count'].value_counts().plot(kind='bar')

    df['count'].value_counts().to_excel('foo.xlsx', 'Sheet1')


    # df['count'].value_counts().plot.pie(autopct='%.1f', fontsize=20, figsize=(6, 6))
    # plt.title('Authorwise distribution')
    # plt.show()

    # #
    # # 制作分布密度图:使用Seaborn设计作图背景样式方案
    sns.set_style("ticks")  # 风格选择包括："white", "dark", "whitegrid", "darkgrid", "ticks"
    sns.set_style({'font.sans-serif': ['SimHei', 'Calibri']})  # 设置中文设定

    # 绘制高中/本科生平均成绩分布密度图
    plt.figure(figsize=(8, 4), dpi=100)  # 通过dpi参数指定图像的分辨率
    sns.distplot(nums, hist=False, kde=True, rug=True,  # 选择是否显示条形图、密度曲线、观测的小细条（边际毛毯）
                 kde_kws={"color": "lightcoral", "lw": 1.5, 'linestyle': '--'},  # 设置选择True的条件(其密度曲线颜色、线宽、线形)
                 rug_kws={'color': 'lightcoral', 'alpha': 1, 'lw': 2, }, label='评论次数')

    # 绘制学生各类别的平均成绩辅助线
    plt.axvline(mean, color='lightcoral', linestyle=":", alpha=2)
    plt.text(mean + 2, 0.012, '评论次数均值: %.1fcm' % (mean), color='indianred')


    # 设置图表其他内容
    # plt.ylim([0, 0.05])
    plt.grid(linestyle='--')
    plt.title(("微信公众号不同昵称评论次数密度图"))
    plt.savefig('Reviews_Density.png')
    plt.show()


if __name__ == '__main__':
    # extract_data()
    # count_comment_nickname()

    # analysis_comment()
    analysis_comment_distr()
    # df = pd.read_excel('foo.xlsx', "Sheet1")
    # df.sort_values(by=['nickname']).to_excel('foo.xlsx', 'Sheet2')



    # pd.set_option('max_colwidth', 200)
    # file = pd.read_csv("train_wechat.csv")
    # print(file['color_content'])
    # # content = '。。。22。。'
    # # print(len('。。。22。。'.split('。')))
    # content = re.sub("。{2,}", "。", content)
    # print(content)


    # aa = '我是中国馆过过过'
    # print(aa[0:2])

    # content = "快递员被爆私拆客户包裹，内衣化妆品被摆拍发朋友圈！顺丰深夜回应,\n斯里兰卡23日进入全国紧急状态\n斯爆炸中国公民死亡数修正为1人#\n最高法回应视觉中国“黑洞”事件#"
    # if content:
    #     contents = content.split('\n')
    #     print('段落长度', len(contents))
    #     if len(contents) == 1:
    #         tmp = contents[0].split('。')
    #         if len(tmp) < 4:
    #             content = contents[0]
    #             content = re.sub("\n", "。", content)
    #         else:
    #             content = "。".join(i for i in tmp[0:4])  # 前四句
    #     else:
    #         content = contents[0] + contents[1]  # 前两段
    #
    # print(content)