from connect_dbs import MySQLConn
from connect_dbs import MongoDBConn
import qrcode
from io import BytesIO
import base64


def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return qr_img_str


def find_film_session_byOrderId(the_order_id):
    film_conn = MongoDBConn()
    cinemaDB = film_conn.client['CinemaDB']['session'+the_order_id[0:-3]]
    return cinemaDB.find_one({"_id": int(the_order_id[-3:])})


def find_order_byid(the_order_id):
    """
    查找订单信息(MySQL数据库 - 查找操作)
    :return: 元组
    """
    film_info = MySQLConn()
    query = "SELECT * FROM ticket_order WHERE order_id = %s "
    result = film_info.execute_query(query, (the_order_id,))
    film_info.close_conn()
    return result


def find_pay_amount_byid(the_order_id):
    film_info = MySQLConn()
    query = "SELECT * FROM pay_amount WHERE order_id = %s "
    result = film_info.execute_query(query, (the_order_id,))
    film_info.close_conn()
    return result
