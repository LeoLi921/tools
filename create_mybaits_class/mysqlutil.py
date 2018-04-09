import pymysql


class MySQLUtil:
    # 数据库地址 用户 密码 自己配置
    def __init__(self, host='127.0.0.1', user='root', passwd='1234', db='test'):
        self.conn = pymysql.connect(host=host,
                                    user=user,
                                    password=passwd,
                                    db=db,
                                    charset="utf8mb4",
                                    cursorclass=pymysql.cursors.DictCursor)

    def query(self, sql):
        cursor = self.conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchall();
        cursor.close()
        return result

    def execute(self, sql):
        cursor = self.conn.cursor()
        cursor.execute(sql)
        self.conn.commit()
        cursor.close()
        return

    def handleresult(self, description, obj):
        result = []
        for row in obj:
            temp = {}
            for i in range(len(row)):
                temp[description[i][0]] = row[i]

            result.append(temp)

        return result

    def querymap(self, sql):
        cursor = self.conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchall();
        result = self.handleresult(cursor.description, result)
        cursor.close()
        return result

    def close(self):
        self.conn.close()
