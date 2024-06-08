from flask import Flask, render_template, request, jsonify, redirect

from seat import *
from index_page import *
from info_page import *
from session_page import *
from login_page import *
from order_page import *
from ticket_page import *

# 设置静态元素存放路径和名字
app = Flask(__name__, static_url_path='/static', static_folder='static')


# 启动前更新电影评分
# update_films_rating_num()
create_seat_all()
address_add()

@app.route('/')
def index():
    return 'hello'

@app.route('/starcinema')
def starcinema_index():
    """
    星光影院(STARCinema)首页
    :return: html格式的电影数据
    功能扩充：电影状态 - 1 上映中
                - -1 结束放映
                - 0 即将上映
    """
    # 获取电影基本信息
    films_info = find_films_info()
    # 获取电影图片信息
    films_cover = find_films_intro()
    # 获取页面信息
    film_index = return_html_li(films_info, films_cover)
    address = round(address_distance_sh(), 2)
    near_by = address_distance_near_by()
    # 发送数据
    return render_template("index.html", data=film_index, address=address, near_by=near_by)


@app.route('/starcinema/info.html', methods=['GET'])
def info():
    """
    单个电影信息页
    :return: 电影数据
    """
    # 接收movie_id
    the_movie_id = request.args.get('movie_id')
    # 获取MySQL数据
    movie_id, title, release, country, movie_length, director, genre, actor, rating_num = find_film_info_byid(the_movie_id)[0]
    # 获取MongoDB数据
    film_intro = find_film_intro_byid(the_movie_id)
    movie_intro = film_intro['movie_intro']
    movie_cover = film_intro['movie_cover']
    # 发送数据
    return render_template('info.html', title=title, release=release, country=country,
                           movie_length=movie_length, director=director, genre=genre,
                           actor=actor, rating_num=rating_num, movie_intro=movie_intro,
                           movie_cover=movie_cover, movie_id=the_movie_id)


@app.route('/starcinema/session.html', methods=['GET'])
def session():
    the_movie_id = request.args.get('movie_id')
    cover = find_film_cover_byid(the_movie_id)
    film_info = find_film_info_byid(the_movie_id)[0]
    title = film_info[1]
    rating = film_info[-1]
    film_sessions = find_film_session_byMovieId(the_movie_id)
    sessions = str()
    if len(film_sessions) == 0:
        return render_template('session.html', sessions='<li><div class="s-middle"><p>暂无排片</p></div></li>',
                               cover=cover, title=title, rating=rating)
    for i in range(len(film_sessions)):
        sessions = sessions + (make_html_li_2(film_sessions[i]['start_time'], film_sessions[i]['finish_time'],
                                              film_sessions[i]['language'], film_sessions[i]['type'],
                                              film_sessions[i]['hall'], film_sessions[i]['price'],
                                              str(film_sessions[i]['_id']), str(film_sessions[i]['movie_id'])))

    return render_template('session.html', sessions=sessions, cover=cover, title=title, rating=rating)


@app.route('/starcinema/login.html', methods=['POST', 'GET'])
def login():
    the_movie_id = request.args.get('movie_id')
    the_session_id = request.args.get('session')
    data = '输入手机号获取验证码'
    return render_template('login.html', data=data, mid=the_movie_id, sid=the_session_id)


@app.route('/starcinema/get-login-code', methods=['GET'])
def get_login_code():
    try:
        login_phone = request.args.get('phone')
        code = Login_code(login_phone)
        response_data = {"message": f"{code}"}
        return jsonify(response_data)
    except Exception as e:
        print(f"Exception: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/starcinema/check-login-code', methods=['GET'])
def check_login_code():
    the_phone = request.args.get('phone')
    the_code = request.args.get('code')
    if Login_code_check(the_phone, the_code):
        return 'success'
    else:
        return 'error'


@app.route('/starcinema/ticket.html', methods=['GET'])
def ticket():
    the_movie_id = request.args.get('movie_id')
    the_session = request.args.get('session')
    the_phone = request.args.get('phone')
    the_code = request.args.get('code')
    user_register(the_phone)
    if Login_code_check(the_phone, the_code):
        seat = random_seat(f'film:session{the_movie_id}:{the_session}')
        if seat is False:
            return render_template('ticket.html', data='本场已满座，请选择其他场次', type='session', url=the_movie_id, name='movie_id', data2='点我返回排片页')
        else:
            order_id = ticket_order(the_movie_id, the_session, the_phone, seat, 1, buy_coupons(1, the_phone))
            return render_template('ticket.html', data='下单成功，', type='order', url=order_id, name='order_id', data2='点我进入订单页，查看取票码')
    else:
        user_del(the_phone)
        return redirect('/')


@app.route('/starcinema/order.html', methods=['GET'])
def order():
    the_order_id = request.args.get('order_id')
    order_info = find_order_byid(the_order_id)[0]
    phone = order_info[1][: 3] + '*' * 4 + order_info[1][-4:]
    actual_price = f"{order_info[3]}"
    count = order_info[4]
    seat = order_info[5]
    pay_time = order_info[6].strftime("%Y-%m-%d %H:%M:%S")
    payment = order_info[7]
    code = order_info[8]
    pay_info = find_pay_amount_byid(the_order_id)[0]
    price = f"{pay_info[0]}"
    coupon = f"{pay_info[1]}"
    parameter = f"{pay_info[2]}"
    session_id = order_info[2]
    sessions = find_film_session_byOrderId(session_id)
    date = sessions['date']
    start_time = sessions['start_time']
    language = sessions['language']
    movie_type = sessions['type']
    finish_time = sessions['finish_time']
    hall = sessions['hall']
    movie_id = sessions['movie_id']
    cover = find_film_cover_byid(movie_id)
    title = find_film_info_byid(movie_id)[0][1]
    qr_code_image = generate_qr_code(code)

    return render_template('order.html', the_order_id=the_order_id, date=date, start_time=start_time, language=language,
                           movie_type=movie_type, price=price,
                           finish_time=finish_time, hall=hall, cover=cover, title=title, phone=phone, actual_price=actual_price,
                           seat=seat, pay_time=pay_time, payment=payment, code=code, coupon=coupon,
                           parameter=parameter, count=count, qr_code_image=qr_code_image)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
