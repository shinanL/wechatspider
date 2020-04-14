# coding:utf-8
import logging

import pymysql


def connectdb_wechat():
    logging.info('连接到mysql服务器...')
    # 打开数据库连接
    # 用户名:root, 密码:123456，数据库wechat
    conn = pymysql.connect("localhost", "root", "1234567", "wechat", charset="utf8mb4")
    logging.info('连接上了!')
    return conn


def connectdb_wechatcluster():
    logging.info('连接到mysql服务器...')
    # 打开数据库连接
    # 用户名:root, 密码:123456，数据库wechat
    conn = pymysql.connect("localhost", "root", "1234567o", "wechatcluster", charset="utf8mb4")
    logging.info('连接上了!')
    return conn

def closedb(conn):
    conn.close()


def query(conn, sql):
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
    except Exception as e:
        conn.rollback()  # 发生错误时回滚
        logging.info("数据库异常: {0}".format(e))

def query_content_url(conn):
    try:
        with conn.cursor() as cursor:
            sql = "SELECT contenturl FROM content WHERE spider = 0"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
    except Exception as e:
        conn.rollback()  # 发生错误时回滚
        logging.info("数据库异常: {0}".format(e))

def shard_content_url(conn):
    try:
        with conn.cursor() as cursor:
            sql = "SELECT id, contenturl FROM content WHERE spider = 0"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
    except Exception as e:
        conn.rollback()  # 发生错误时回滚
        logging.info("数据库异常: {0}".format(e))


def query_with_sql(conn, sql):
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
    except Exception as e:
        conn.rollback()  # 发生错误时回滚
        print(e)
        logging.info("数据库异常: {0}".format(e))
        logging.exception(e)


def query_with_sql_rowcount(conn, sql):
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
            return result, cursor.rowcount
    except Exception as e:
        conn.rollback()  # 发生错误时回滚
        print(e)
        logging.info("数据库异常: {0}".format(e))
        logging.exception(e)


def query_with_sql_one(conn, sql):
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchone()
            return result
    except Exception as e:
        print("======={}".format(sql))
        conn.rollback()  # 发生错误时回滚
        logging.info("数据库异常: {}".format(e))


def insert_content(conn, content, url):
    try:
        sql = "UPDATE content SET content = '{}', spider = 1 WHERE contenturl = '{}'" \
            .format(pymysql.escape_string(content), url)
        # .format(content, url)
        # logging.info(sql)
        conn.cursor().execute(sql)
        conn.commit()
    except Exception as e:
        conn.rollback()  # 发生错误时回滚
        logging.info("数据库异常: {0}".format(e))


def update_bizinfo_addcontact(conn, biz):
    try:
        sql = "UPDATE bizinfo SET addcontact = 1 WHERE biz = '{}'" \
            .format(biz)
        logging.info('更新表bizinfo中addcontact')
        conn.cursor().execute(sql)
        conn.commit()
    except Exception as e:
        conn.rollback()  # 发生错误时回滚
        logging.info("数据库异常: {0}".format(e))


def update_bizinfo_spider(conn, biz):
    try:
        sql = "UPDATE bizinfo SET spider = 1 WHERE biz = '{}'" \
            .format(biz)
        logging.info('更新表bizinfo中spider')
        conn.cursor().execute(sql)
        conn.commit()
    except Exception as e:
        conn.rollback()  # 发生错误时回滚
        logging.info("数据库异常: {0}".format(e))


def update_content_spider(conn, url):
    try:
        sql = "UPDATE content SET spider = 1 WHERE contenturl = '{}'" \
            .format(url)
        # logging.info('更新数据--'+sql)
        conn.cursor().execute(sql)
        conn.commit()
    except Exception as e:
        conn.rollback()  # 发生错误时回滚
        logging.info("数据库异常: {0}".format(e))


def update_bizinfo_consume(conn, consume, biz):
    """
    更新一个公众号的数据量
    :param conn:
    :param total:
    :param consume:
    :param biz:
    :return:
    """
    try:
        sql = "UPDATE bizinfo SET url_consume = {}, spider = 1 WHERE biz = '{}'".format(consume, biz)
        logging.info('更新花费时间:%s' % sql)
        logging.info(sql)
        conn.cursor().execute(sql)
        conn.commit()
    except Exception as e:
        conn.rollback()  # 发生错误时回滚
        logging.info("数据库异常: {0}".format(e))


def update_bizinfo_total(conn, total, consume, biz):
    """
    更新一个公众号的数据量
    :param conn:
    :param total:
    :param consume:
    :param biz:
    :return:
    """
    try:
        sql = "UPDATE bizinfo SET total = {}, url_consume = {}  WHERE biz = '{}'".format(total, consume, biz)
        logging.info('更新总量')
        logging.info(sql)
        conn.cursor().execute(sql)
        conn.commit()
    except Exception as e:
        conn.rollback()  # 发生错误时回滚
        logging.info("数据库异常: {0}".format(e))


def insert_bizinfo(conn, data):
    """
    插入公众号主体信息
    :param conn:
    :param data:
    :return:
    """
    try:
        sql = "REPLACE INTO bizinfo(biz, nickname, operator, profile_desc,icon_url, data_url) \
           VALUES (%s, %s, %s, %s, %s, %s)"
        conn.cursor().execute(sql, data)
        conn.commit()
    except Exception as e:
        conn.rollback()  # 发生错误时回滚
        logging.info("数据库异常: {0}".format(e))


def update_comment(conn, sql):
    """
    更新content表，插入文章内容和用户评论
    :param conn:
    :param data:
    :return:
    """
    try:
        # 插入
        conn.cursor().execute(sql)
        conn.commit()
        logging.info('---插入数据成功---')
        # print('---插入数据成功---')
    except Exception as e:
        conn.rollback()  # 发生错误时回滚
        logging.info("数据库异常: {0}".format(e))


def exec_sql(conn, sql):
    """
    更新content表，插入文章内容和用户评论
    :param conn:
    :param data:
    :return:
    """
    try:
        # 插入
        conn.cursor().execute(sql)
        conn.commit()
        # print('---插入数据成功---')
    except Exception as e:
        print("-----------{}".format(sql))
        conn.rollback()  # 发生错误时回滚
        print(e)
        logging.info("数据库异常: {0}".format(e))


def insert_by_many_comment(conn, data):
    """
    批量插入指定公众号爬取的文章链接
    :param conn:
    :param data:
    :return:
    """
    # 这里你知道table和data，其中data是一个字典，写插入数据库的代码
    cols = ", ".join('`{}`'.format(k) for k in data[0].keys())
    # logging.info(cols)  # '`name`, `age`'

    val_cols = ', '.join('%({})s'.format(k) for k in data[0].keys())
    # logging.info(val_cols)  # '%(name)s, %(age)s'

    # 不存在插入，存在忽略
    sql = "insert ignore into comment(%s) values(%s)"
    # sql = "replace into content(%s) values(%s)"   // 不存在插入，存在更新
    res_sql = sql % (cols, val_cols)
    # logging.info(res_sql)  # 'insert into users(`name`, `age`) values(%(name)s, %(age)s)'

    try:
        # 批量插入
        conn.cursor().executemany(res_sql, data)
        conn.commit()
        logging.info('---插入数据成功---')
    except Exception as e:
        conn.rollback()  # 发生错误时回滚
        logging.info("数据库异常: {0}".format(e))


def insert_by_many_content_url(conn, data):
    """
    批量插入指定公众号爬取的文章链接
    :param conn:
    :param data:
    :return:
    """
    # 这里你知道table和data，其中data是一个字典，写插入数据库的代码
    cols = ", ".join('`{}`'.format(k) for k in data[0].keys())
    # logging.info(cols)  # '`name`, `age`'

    val_cols = ', '.join('%({})s'.format(k) for k in data[0].keys())
    # logging.info(val_cols)  # '%(name)s, %(age)s'

    # 不存在插入，存在忽略
    sql = "insert ignore into content(%s) values(%s)"
    # sql = "replace into content(%s) values(%s)"   // 不存在插入，存在更新
    res_sql = sql % (cols, val_cols)
    # logging.info(res_sql)  # 'insert into users(`name`, `age`) values(%(name)s, %(age)s)'

    try:
        # 批量插入
        conn.cursor().executemany(res_sql, data)
        conn.commit()
        logging.info('---插入数据成功---')
    except Exception as e:
        conn.rollback()  # 发生错误时回滚
        logging.info("数据库异常: {0}".format(e))


def insert_by_many_biz(conn, data):
    """
    批量插入指定公众号爬取的文章链接
    :param conn:
    :param data:
    :return:
    """
    # 这里你知道table和data，其中data是一个字典，写插入数据库的代码
    cols = ", ".join('`{}`'.format(k) for k in data[0].keys())
    # logging.info(cols)  # '`name`, `age`'

    val_cols = ', '.join('%({})s'.format(k) for k in data[0].keys())
    # logging.info(val_cols)  # '%(name)s, %(age)s'

    sql = "replace into bizinfo(%s) values(%s)"
    res_sql = sql % (cols, val_cols)
    # logging.info(res_sql)  # 'insert into users(`name`, `age`) values(%(name)s, %(age)s)'

    try:
        # 批量插入
        conn.cursor().executemany(res_sql, data)
        conn.commit()
        print('---插入数据成功---')
    except Exception as e:
        conn.rollback()  # 发生错误时回滚
        print("数据库异常: {0}".format(e))


def insert_by_many_bizinfo(conn, data):
    try:
        sql = "INSERT INTO bizinfo(biz, nickname, operator, profile_desc,icon_url, data_url) \
           VALUES (%s, %s, %s, %s, %s, %s)"
        # 批量插入
        conn.cursor().executemany(sql, data)
        conn.commit()
    except Exception as e:
        conn.rollback()  # 发生错误时回滚
        logging.info("数据库异常: {0}".format(e))


def insert_by_many_bizinfo_addcontact(conn, data):
    try:
        sql = "INSERT INTO bizinfo(biz, addcontact) \
           VALUES (%s, 1)"
        # 批量插入
        conn.cursor().executemany(sql, data)
        conn.commit()
        logging.info('插入数据成功')
    except Exception as e:
        conn.rollback()  # 发生错误时回滚
        logging.info("数据库异常: {0}".format(e))