from connect_dbs import MongoDBConn


def find_film_session_byMovieId(the_movie_id):
    film_conn = MongoDBConn()
    cinemaDB = film_conn.client['CinemaDB']['session'+the_movie_id]
    return list(cinemaDB.find())


def find_film_cover_byid(the_movie_id):
    film_conn = MongoDBConn()
    cinemaDB = film_conn.client["CinemaDB"]["films"]
    return cinemaDB.find_one({"movie_id": the_movie_id})['movie_cover']


def make_html_li_2(start_time, finish_time, language, type, hall, price, sid, mid):
    info = """<li><div class="flex-cont flex-stretch schedule"  onclick="window.location.href='/starcinema/login.html?movie_id=mid&session=sid';"> <div class="s-left"><p>start_time</p> <span>finish_time散场</span></div><div class="s-middle"><p>language/type</p> <span>hall</span></div><div class="s-right"><p><label class="sign">￥</label> <label class="jiage">price</label></p></div></div> </li>"""
    return info.replace('start_time', start_time).replace('finish_time', finish_time).replace('language', language).replace('type', type).replace('hall', hall).replace('price', price).replace('sid', sid).replace('mid', mid)