# coding:utf-8
import logging
import os
import sys
import time
from urllib.parse import unquote

cur_path = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.abspath(os.path.dirname(cur_path) + os.path.sep + ".")
sys.path.append(root_path)
from common import dbutil
from bs4 import BeautifulSoup as bs4


"""解析公众号文章：从html页面获取内容、用户评论、链接、发表时间等"""

conn = dbutil.connectdb()


if __name__ == '__main__':

    base = '/Users/liushinan/wechat/artical'
    articles = os.listdir(base)
    print('文章总量：%d' % len(articles))
    for article in articles:
        time_start = time.time()
        print('---------------开始----------------')
        # 过滤隐藏文件夹
        if article[0] == '.':
            continue
        url = unquote(article)
        url = url[0:url.find('.html')]
        print(url)
        f = os.path.join(base, article)
        content = open(f).read()
        # print(content)
        soup = bs4(content, "html.parser")
        try:
            title = soup.find(class_="rich_media_title").text.strip()
            print('文章标题：%s' % title)
        except:
            print('找不到标题，删除文件')
            os.remove(f)
            continue
        try:
            nick_name = soup.find('a', id='js_name').text.strip()
            print('公众号昵称：%s' % nick_name)
            # publish_time = soup.find(class_='rich_media_meta rich_media_meta_text').text
            publish_time = soup.find('em', id='publish_time').text
            print('发表时间：%s' % publish_time)
            media_content = soup.find(class_='rich_media_content')
            paragraph = media_content.find_all('p')
            string = ''
            for p in paragraph:
                string += p.text
            print('正文：%s' % string)
        except:
            print('提取文章内容出错')
        readnum = ''
        likenum = ''
        comments = []
        try:
            # 底部为阅读原文时，没有阅读量和点赞数
            readnum = soup.find('span', id='readNum3').text
            likenum = soup.find('span', id='likeNum3').text
            print('阅读量：%s' % readnum)
            print('在看：%s' % likenum)
        except:
            print('没有阅读量和点赞数')

        try:
            # 也可能没有用户评论
            discuss_list = soup.find(class_='discuss_list').find_all('li')
            for discuss in discuss_list:
                elected = discuss.find(class_='praise_num').text
                if len(elected) == 0:
                    elected = 0
                nickname = discuss.find(class_='nickname').text
                avatar = discuss.find(class_='avatar')['src']
                message = discuss.find(class_='discuss_message_content').text.replace('\n', '')
                comment = {
                    'nickname': nickname,
                    'elected': elected,
                    'avatar': avatar,
                    'comment': message
                }
                comments.append(comment)
            print('用户评论：%s' % comments)
        except:
            print('提取用户评论出错，可能是因为没有用户评论')
        images = soup.find_all('img')
        links = []
        for image in images:
            link = image.get('data-src')
            if link:
                links.append(link)

        print('链接：%s' % links)

        rich_message = {
            'title': title,
            'nickname': nick_name,
            'datetime': publish_time,
            'content': string,
            'readnum': readnum,
            'likenum': likenum,
            'comment': str(comments),
            'links': str(links)
        }
        # 表名
        table_name = 'content'
        conditions = {'contenturl': url}  # 更新所需条件
        # 构造update语句
        sentence1 = 'UPDATE %s SET ' % table_name
        sentence2 = ','.join(['%s=%r' % (k, rich_message[k]) for k in rich_message])
        sentence3 = ' WHERE '
        sentence4 = ' AND '.join(['%s=%r' % (k, conditions[k]) for k in conditions])
        sql = sentence1 + sentence2 + sentence3 + sentence4 + ';'
        dbutil.update_comment(conn, sql)
        time_end = time.time()
        print('总消耗时间：%f' % (time_end-time_start))
        # 删除文章
        os.remove(f)