from datetime import datetime, timedelta

from pymongo import MongoClient
from redis import Redis
import mysql.connector


class MongoDBConn:
    # 初始化 MongoDB 连接
    def __init__(self):
        # 获取数据库的连接
        self.client = MongoClient('192.168.88.130', 27017)

    # 电影
    def find_last_id(self, col):
        cinemadb = self.client["CinemaDB"]
        film = cinemadb[col]
        if film.count_documents({}) == 0:
            return 1
        documents = film.find().sort({"_id": -1}).limit(1)
        for document in documents:
            return int(document["_id"]) + 1

    def getColl(self):
        cinemadb = self.client["CinemaDB"]
        collections = cinemadb.list_collection_names()
        return collections

    def delById(self, film_id):
        cinemadb = self.client["CinemaDB"]
        film = cinemadb["films"]
        result = film.delete_one({"movie_id": film_id})
        if result.deleted_count == 1:
            return f"成功删除电影，movie_id: {film_id}"
        else:
            return f"未找到电影，movie_id: {film_id}"

    def updateFilm(self, movie_id, movie_intro):
        cinemadb = self.client["CinemaDB"]
        film = cinemadb["films"]
        try:
            film.update_one({"movie_id": movie_id}, {"$set": {"movie_intro": movie_intro}})
            return "更新成功！"
        except Exception as e:
            return f"更新失败，发生错误：{e}"

    # 场次

    def addSession(self, film_id, language, date, start_time, length, hall, type, price):
        cinemadb = self.client["CinemaDB"]
        col = "session" + self.filmName(film_id)
        session = cinemadb[col]
        # 将字符串时间转换为 datetime 对象
        start_time2 = datetime.strptime(start_time, "%H:%M")
        # 创建表示时长的 timedelta 对象
        duration = timedelta(minutes=length)
        # 计算结束时间
        finish_time = (start_time2 + duration).strftime('%H:%M')
        try:
            session.insert_one({"_id": self.find_last_id(col),
                                "movie_id": film_id,
                                "date": date,
                                "start_time": start_time,
                                "hall": hall,
                                "length": length,
                                "language": language,
                                "type": type,
                                "price": price,
                                "finish_time": finish_time
                                })
            return "插入成功！"
        except Exception as e:
            return f"插入失败，发生错误：{e}"


class RedisConn:
    # 初始化 Redis 连接
    def __init__(self):
        self.conn = Redis(host='192.168.88.130', port=6379, decode_responses=True, password='123456')


class MySQLConn:
    """
    MySQL操作, 连接/关闭/增/删/改/查
    """
    # 初始化 MySQL 连接
    def __init__(self, host='localhost', user='root', password='123456', database='cinema'):
        # 初始化数据库连接
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        # 创建游标对象
        self.cursor = self.conn.cursor()

    def close_conn(self):
        # 关闭游标和连接
        self.cursor.close()
        self.conn.close()

    def execute_query(self, query, params=None):
        # 执行查询
        if params is not None:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        # 获取查询结果
        result = self.cursor.fetchall()
        # 结果为空返回None
        if len(result) == 0:
            return None
        # 返回查询结果
        return result

    def execute_insert(self, query, data):
        try:
            # 执行插入操作
            self.cursor.execute(query, data)
            # 提交事务
            self.conn.commit()
            # 返回插入的记录的ID
            return self.cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            # 发生错误时回滚事务
            self.conn.rollback()
            return None

    def execute_delete(self, query, data=None):
        try:
            # 执行删除操作
            self.cursor.execute(query, data)
            # 提交事务
            self.conn.commit()
            # 返回受影响的行数
            return self.cursor.rowcount
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            # 发生错误时回滚事务
            self.conn.rollback()
            return 0

    def execute_update(self, query, data):
        try:
            # 执行更新操作
            self.cursor.execute(query, data)
            # 提交事务
            self.conn.commit()
            # 返回受影响的行数
            return self.cursor.rowcount
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            # 发生错误时回滚事务
            self.conn.rollback()
            return 0

    # def add_film_in_mysql(self):
    #     film_info = MySQLConn()
    #     insert_query = "INSERT INTO film (movie_id, title, release_date, country, length, director, genre, actor) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    #     insert_data = (
    #     "30270746", "寒单", "2024-01-05", "中国台湾", "125", "黄朝亮", "剧情", "郑人硕 / 胡宇威 / 黄瀞怡 / 林予晞")
    #     inserted_id = film_info.execute_insert(insert_query, insert_data)
    #     print(f"Inserted record ID: {inserted_id}")
    #     film_info.close_conn()

#
# Order = OrderManager("localhost", "root", "123456", "FilmOrder")
# print(Order)
# Order.close_connection()

