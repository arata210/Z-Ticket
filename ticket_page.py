import random
import time
import uuid
import json
from datetime import datetime

from login_page import user_register
from connect_dbs import RedisConn, MongoDBConn, MySQLConn


coupon = RedisConn()


# 创建唯一兑换ID
def coupon_id_creator(number):
    # 0-25随机数
    c = random.randint(0, 25)
    # uuid4算法
    d = uuid.uuid4()
    # 随机数转为随机大小写·字母+16进制4位ID+uuid4第一段
    unique_id = f"{chr(ord(random.choice(['A', 'a'])) + c)}{hex(number+128)[2:].zfill(4)}{str(d).split('-')[0]}"
    # print(unique_id, end='|')
    return unique_id


def couponGenerator(name=None, discount=1, count=10, exp=7):
    for x in range(count):
        new_coupon = dict()
        # Mf校验码+唯一id
        new_id = "Mf" + coupon_id_creator(x)
        # 创建字典, 优惠券名, 折扣, 状态,开始时间预留, 有效期预留
        new_coupon[new_id] = {
            "name": name,
            "discount": discount,
            # state = 0 未启用
            "state": 0,
            "start": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "exp": exp,
        }
        coupon.conn.sadd('film:coupons', new_id)
        coupon.conn.hset('film:coupons_info', new_id, json.dumps(new_coupon[new_id], ensure_ascii=False))


def create_coupon():
    couponGenerator("1元立减券", -1, 5, 7)
    couponGenerator("95折折扣券", 0.95, 10, 7)
    couponGenerator("7折折扣券", 0.7, 4, 7)
    couponGenerator("10元立减券", -10, 1, 7)


def Get_all_info():
    hash_dict = coupon.conn.hgetall('film:coupons_info')
    result = {key: json.loads(value) for key, value in hash_dict.items()}
    return result


def del_alldata():
    # 清空数据
    coupon.conn.delete('film:coupons')
    coupon.conn.delete('film:coupons_info')


def Check_number():
    return len(coupon.conn.smembers('film:coupons'))


def Get_info(coupons_id):
    coupons_info = eval(coupon.conn.hget('film:coupons_info', coupons_id))
    return coupons_info


def Last_order_id():
    if not coupon.conn.exists('film:order_id'):
        # 如果键不存在，则添加一个初始元素
        coupon.conn.zadd('film:order_id', {'S0000': 0})
    # 执行 zrange 操作
    return coupon.conn.zcard('film:order_id') - 1


def coupon_order(order_id, phone, coupon_set):
    new_order = dict()
    new_order[order_id] = {
        "phone": phone,
        "coupons": list(coupon_set),
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "payment": "在线支付"
    }
    coupon.conn.hset('film:order_info', order_id, json.dumps(new_order, ensure_ascii=False))


def Change_state(coupon_id, coupon_state):
    coupons_info = Get_info(coupon_id)
    coupons_info['state'] = coupon_state
    coupon.conn.hset('film:coupons_info', coupon_id, json.dumps(coupons_info, ensure_ascii=False))


def coupon_order_id():
    # 获取最后id+1位
    last_id = Last_order_id() + 1
    # 订单ID以S开头
    order_id = 'S' + str(last_id).zfill(4)
    # 加入数据库
    coupon.conn.zadd('film:order_id', {order_id: last_id})
    return order_id


def coupon_order_receive(phone, coupon_set):
    # 获取订单ID，接收传入的用户ID和优惠券集
    coupon_order(coupon_order_id(), phone, coupon_set)


def buy_coupons(number, phone):
    coupon_set = set()
    # 不能超额购买，超额默认购买余存全部
    if Check_number() - number < 0:
        number = Check_number()
    if Check_number() - number < 0:
        print(phone, ':库存不足')
    else:
        # 获取指定数量优惠券，更改优惠券状态为1，并生成订单
        for x in range(number):
            coupon_set.add(coupon.conn.spop('film:coupons'))
        if coupon_set:
            coupon_order_receive(phone, coupon_set)

        for coupon_id in coupon_set:
            Change_state(coupon_id, 1)
            # print(new_dict)
            # print(f"{phone}:{coupon_id}，{Get_info(coupon_id)['name']}至【优惠券】兑换")
            return coupon_id
    # except Exception as e:
    #     print(phone, ':优惠券售空')


# buy_coupons(2, "13812345478")


def ticket_order(the_movie_id, the_session, the_phone, the_seat, the_count=1, the_coupon=''):
    sqldb = MySQLConn()
    film_conn = MongoDBConn()
    q1 = "select pid from user where phone=%s"
    parameter = sqldb.execute_query(q1, (the_phone,))
    q2 = "select pvalue from parameter where pid=%s"
    p_value = sqldb.execute_query(q2, (parameter[0][0],))[0][0]

    the_session_id = the_movie_id+str(the_session).zfill(3)
    price = float(film_conn.client["CinemaDB"]["session"+the_movie_id].find_one({"movie_id": the_movie_id})['price']) * the_count

    if len(the_coupon) == 0:
        coupon_discount = 1
    else:
        coupon_discount = Get_info(the_coupon)['discount']

    if coupon_discount > 0:
        coupon_price = price - price * coupon_discount
        if p_value > 0:
            actual_price = (price - coupon_price) * p_value
            parameter_price = price - actual_price - coupon_price
        else:
            parameter_price = - p_value
            actual_price = price - coupon_price + p_value
    else:
        coupon_price = - coupon_discount
        if p_value > 0:
            actual_price = (price - coupon_price) * p_value
            parameter_price = price - actual_price - coupon_price
        else:
            parameter_price = - p_value
            actual_price = price - coupon_price + p_value

    order_id = 'S' + str(int(time.time()))
    q3 = "INSERT INTO ticket_order (order_id, phone, session_id, actual_price, count, seat, datetime, payment, code) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    the_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = str(random.randint(1000, 9999)) + str(int(time.time()))[-4:]
    d3 = (order_id, the_phone, the_session_id, actual_price, the_count, the_seat, the_time, '在线支付', code)
    print(sqldb.execute_insert(q3, d3))

    q4 = "INSERT INTO pay_amount (original_price, coupon_amount, parameter_amount, actual_price, order_id) VALUES (%s, %s, %s, %s, %s)"
    d4 = (price, coupon_price, parameter_price, actual_price, order_id)
    print(sqldb.execute_insert(q4, d4))

    sqldb.close_conn()
    return order_id




# print(ticket_order('35725869', '3',
#                    '13812342278','D排3座, D排1座', 1))
