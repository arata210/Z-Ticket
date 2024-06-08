import requests
from bs4 import BeautifulSoup
from connect_dbs import MySQLConn, MongoDBConn, RedisConn


def douban_rating_num(movie_id):
    """
    爬取豆瓣电影评分
    :param movie_id: 电影ID
    :return: 评分
    """
    # 设置请求标头
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',}
    # 获取请求内容
    response = requests.get('https://movie.douban.com/subject/' + movie_id, headers=headers)
    # 转换html文本
    html_content = response.text

    # bs4解析html
    soup = BeautifulSoup(html_content, 'html.parser')

    # 查找class为"rating_nums"的标签，并转为字符串
    rating_num = soup.find('div', {'class': 'rating_self'}).find('strong', {'class': 'll rating_num'}).text.strip()

    # 补充"暂无评分"的条件
    if len(rating_num) == 0:
        rating_num = '暂无评'

    return rating_num + '分'


def find_films_info():
    """
    查找电影信息(MySQL数据库 - 查找操作)
    :return: 元组
    """
    film_info = MySQLConn()
    # 电影ID倒序查找
    query = "SELECT * FROM film ORDER BY movie_id DESC"
    result = film_info.execute_query(query)
    film_info.close_conn()
    return result


def update_films_rating_num():
    """
    更新电影评分(MySQL数据库 - 更新操作)
    :return: None
    """
    # 启动连接
    film_info = MySQLConn()
    # 获取影片数量
    films = find_films_info()
    count = len(films)
    for x in range(count):
        # 获取豆瓣最新评分
        new_rating_num = douban_rating_num(films[x][0])
        # 数据库内的旧评分
        old_rating_num = films[x][-1]
        if new_rating_num != old_rating_num:
            # 如果不同, 则更新数据
            update_query = "UPDATE film SET rating_num = %s WHERE movie_id = %s"
            update_data = (new_rating_num, films[x][0])
            film_info.execute_update(update_query, update_data)
    # 关闭连接
    film_info.close_conn()


def find_films_intro():
    film_conn = MongoDBConn()
    cinemaDB = film_conn.client["CinemaDB"]["films"]
    return list(cinemaDB.find())


def make_html_li(mcover, mid, mtitle, mdirector, mactor, mrating):
    """
    自动创建每部电影在html中的<li>信息
    :param mcover: 电影封面
    :param mid: 电影ID
    :param mtitle: 电影标题
    :param mdirector: 电影导演
    :param mactor: 电影主演
    :param mrating: 电影评分
    :return:
    """
    info = """
    <li><section class="flex-cont"><div class="c-left"><img width="100" src="mcover"></div>
    <div class="flex-item" onclick="window.location.href='/starcinema/info.html?movie_id=mid';">
    <div class="flex-cont"><div class="flex-item c-middle"><div class="flex-cont flex-nav title">
    <h2>mtitle</h2><span class="max-ver">2D</span></div><p>mdirector</p><span class="info">mactor</span></div></div></div>
    <div class="c-right"><p><label style="font-size: 16px;">mrating</label></p>
    <button class="btn-bg4 btn-hot" onclick="window.location.href='/starcinema/session.html?movie_id=mid';">购票</button>
    </div></section></li>
    """
    return info.replace('mcover', mcover).replace('mid',
        mid).replace('mtitle', mtitle).replace('mdirector',mdirector).replace('mactor',
                                                                mactor).replace('mrating', mrating)


def return_html_li(films_info, films_cover):
    # 双重循环 制作显示的信息
    film_index = str()
    for i in range(len(films_info)):
        for j in range(len(films_cover)):
            if films_info[i][0] == films_cover[j]['movie_id']:
                film_index = film_index + (
                    make_html_li(films_cover[j]['movie_cover'], films_info[i][0], films_info[i][1], films_info[i][5],
                                 films_info[i][-2], films_info[i][-1]))
    return film_index


address = RedisConn()


def address_add():
    address.conn.geoadd("film:cinema:address", (121.480248, 31.236276, "上海市"))
    address.conn.geoadd("film:cinema:address", (121.658149, 31.270235, "STARCinema(二工大店)"))
    address.conn.geoadd("film:cinema:address", (121.663077, 31.27215, "顾唐路(地铁站)"))
    address.conn.geoadd("film:cinema:address", (121.656852, 31.270897, "金海路金丰路(公交站)"))


def address_distance_sh():
    distance_sh = address.conn.geodist('film:cinema:address', '上海市', 'STARCinema(二工大店)', unit='km')
    return distance_sh


def address_distance_near_by():
    near_by = address.conn.georadiusbymember("film:cinema:address", "STARCinema(二工大店)", 1, unit='km')
    near_by.remove("STARCinema(二工大店)")
    near_by_list = list()
    for x in near_by:
        distance = address.conn.geodist("film:cinema:address", "STARCinema(二工大店)", x, unit='m')
        near_by_list.append(f'{x}约有{int(distance)}米')
    return near_by_list
