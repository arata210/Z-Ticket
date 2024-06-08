from connect_dbs import MySQLConn
from connect_dbs import MongoDBConn


def find_film_info_byid(the_movie_id):
    """
    查找电影信息(MySQL数据库 - 查找操作)
    :return: 元组
    """
    film_info = MySQLConn()
    query = "SELECT * FROM film WHERE movie_id = %s "
    result = film_info.execute_query(query, (the_movie_id,))
    film_info.close_conn()
    return result


def find_film_intro_byid(the_movie_id):
    """
    查找电影信息(MySQL数据库 - 查找操作)
    :return: 元组
    """
    film_conn = MongoDBConn()
    cinemaDB = film_conn.client["CinemaDB"]["films"]
    return cinemaDB.find_one({"movie_id": the_movie_id})
