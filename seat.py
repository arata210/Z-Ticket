import random

from connect_dbs import RedisConn, MongoDBConn


seat = RedisConn()


def create_seat_all():
    session = MongoDBConn()
    for x in session.getColl():
        if x.startswith('session'):
            session = list(session.client['CinemaDB'][x].find())
            for y in session:
                for i in range(0, 2):
                    for j in range(1, 3):
                        seat.conn.zadd(f"film:{x}:{y['_id']}", {f"{chr(ord('A') + i)}排{j}座": 1})


def random_seat(zset_name):
    cursor = 0
    members_with_score_one = []

    while True:
        cursor, members = seat.conn.zscan(zset_name, cursor, match='*', count=1000)
        for member, score in members:
            if float(score) == 1.0:
                members_with_score_one.append(member)

        if cursor == 0:
            break

    # 从符合条件的成员中随机选择一个
    if members_with_score_one:
        selected_member = random.choice(members_with_score_one)
        seat.conn.zadd(zset_name, {selected_member: 0})
        return selected_member
    else:
        return False
