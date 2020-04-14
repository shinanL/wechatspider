from common import dbutil, wxdriver, global_variable as glv

"""
数据预处理，去除多余的空行
"""
conn = dbutil.connectdb_wechatcluster()


if __name__ == '__main__':

    sql = "SELECT id,content FROM test limit 0,200"
    result = dbutil.query_with_sql(conn, sql)
    file = open("test.txt", "w")
    for (id, content) in result:
        # 不为空
        if content:
            # content = content.lstrip("\n").rstrip("\n")
            # content = re.sub("\n{2,}", "\n", content)
            # print(content)
            # print("\n---------------------------\n")
            # sql = "update test set content = '{}' where id = {}".format(pymysql.escape_string(content), id)
            # dbutil.exec_sql(conn, sql)
            # print(id)
            file.write(content)
            file.write("\n")
            # file.write("\n---------------------------\n")
    file.close()

