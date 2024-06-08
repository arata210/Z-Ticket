import random
from connect_dbs import RedisConn, MySQLConn

login = RedisConn()


def Login_code(phone):
    code = str(random.randint(0, 999999)).zfill(6)
    login.conn.setex('film:phone:' + phone, 60, code)
    return '验证码: ' + code + ', 60秒有效'


def Login_code_check(phone, input_code):
    code = login.conn.get('film:phone:' + phone)
    if code == input_code:
        login.conn.delete('film:phone:' + phone)
        return True
    else:
        return False


def user_register(phone):
    register = MySQLConn()
    query = "INSERT INTO user (phone, pid, balance) VALUES (%s, %s, %s)"
    data = (phone, 'P000', 0)
    register.execute_insert(query, data)
    register.close_conn()


def user_del(phone):
    register = MySQLConn()
    query = "DELETE FROM users WHERE phone = %s"
    register.execute_delete(query, phone)
    register.close_conn()

