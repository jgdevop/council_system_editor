__author__ = 'jaap'
"""
"""
# ---
import sys
import os
import os.path as P
import traceback

# ---
import time
import shutil
import datetime as DT

# ---
import sqlite3 as SQL

# ---
import settings as S

"""
CREATE TABLE cs_group(
    group_id int primary key,
    group_key varchar,
    group_name varchar,
    group_logo varchar);

CREATE TABLE cs_party(
    party_id int primary key, 
    party_key varchar,
    party_name varchar, 
    party_logo_name varchar);

CREATE TABLE cs_message(
    message_id int primary key, 
    message_key varchar, 
    message_value varchar);

CREATE TABLE cs_user(
    user_id int primary key, 
    user_key varchar, 
    user_name varchar, 
    party_id int,
    card_id int,
    can_vote int);

CREATE TABLE cs_group_position(
    pos_group_id int, 
    pos_id int, 
    pos_user_id int, 
    primary key(pos_group_id, pos_id));
    
CREATE TABLE cs_card(
   card_id integer primary key, # INTEGER primary key to get automatic values
   card_key varchar)

"""

# ---
PATH_DATA = S.PATH_DATA
PATH_DATA_HISTORY = S.PATH_DATA_HISTORY

USERS_XML = "" #P.join(PATH_DATA, S.USERS)
POSITIONS_XML = "" #P.join(PATH_DATA, S.POSITIONS)
IMAGES_XML = "" #P.join(PATH_DATA, S.IMAGES)

# ---
"""
<?xml version="1.0" encoding="UTF-8"?>
<users>
    <user>
        <id>1</id>
        <name>jaap</name>
        <group>VVD</group>
    </user>
</users>

"""
def get_timestamp():
    now = DT.datetime.now()
    s = now.strftime('%Y%m%d%H%M%S')
    return s

def get_timestamp_filename(fn):
    path, fn = P.split(fn)
    fn_pre, fn_ext = P.splitext(fn)
    timestamp = get_timestamp()
    fn = ''.join((fn_pre, '_', timestamp, fn_ext))
    fn = P.join(path, fn)
    return fn

def move_file_to_history(fn):
    gn = P.join(PATH_DATA_HISTORY, fn)
    gn = get_timestamp_filename(gn)
    print(gn)
    if P.exists(fn):
        shutil.copy(fn, gn)
# ---
class Position(object):
    def __init__(self):
        self.id = None
        self.name_id = None

class Group(object):
    def __init__(self):
        self.id = None
        self.name_id = None


# ---
class DB(object):

    def __init__(self):
        self.db_name = S.DB
        self.db = None

    def connect(self):
        self.db = SQL.connect(self.db_name)

    def check(self, fnc):
        self_connected = False
        try:
            if not self.db:
                self.connect()
                self_connected = True
            return fnc()
        finally:
            if self_connected and self.db:
                self.disconnect()

    def _execute(self, sql, *args):
        db = self.db
        cursor = db.cursor()
        cursor.execute(sql, args)
        return cursor

    def _select_one(self, sql, *args):
        cursor = self._execute(sql, *args)
        result = cursor.fetchone()
        return result

    def _select(self, sql, *args):
        cursor = self._execute(sql, *args)
        result = cursor.fetchall()
        return result

    def get_cards(self):
        sql = """select cs_card.card_id, card_key
                        from cs_card 
                 inner join main.cs_user on cs_card.card_id = cs_user.card_id"""
        result = self._select(sql)
        return result

    def find_card(self, card_key):
        # -1 is not found
        sql = """select card_id from cs_card where card_key=?"""
        result = self._select_one(sql, card_key)
        if not result:
            return -1
        return result[0]

    def find_user_can_vote_by_card(self, card_key):
        card_id = self.find_card(card_key)
        if card_id <= 0:
            return 0

        sql = """select can_vote from main.cs_user where card_id = ?"""
        result = self._select_one(sql, card_id)
        if result:
            if not result[0]:
                return 0
            return 1
        return 0

    def find_user_by_card(self, card_key):
        card_id = self.find_card(card_key)
        if card_id <= 0:
            return 0

        sql = """select user_id from cs_user where card_id = ?"""
        result = self._select_one(sql, card_id)
        if result:
            if not result[0]:
                return 0
            return result[0]
        return 0

    def couple_card(self, person_id, card_key):
        card_id = self.find_card(card_key)
        if card_id < 0:
            _ = self.add_card(card_key)
            card_id = self.find_card(card_key)
            if card_id < 0:
                raise BaseException('')
        user_id = self.find_card_user(card_id)
        if user_id == person_id:
            # already ok
            return person_id, 0
        # remove card_id from old user
        print('ok')
        if user_id > 0:
            sql = """update cs_user set card_id=0 where user_id=?"""
            self._execute(sql, user_id)

        # set card_id for new user
        sql = """update cs_user set card_id=? where user_id=?"""
        self._execute(sql, card_id, person_id)
        self.commit()
        return person_id, user_id

    def add_card(self, card_key):
        sql = """select card_id from cs_card where card_key=?"""
        res = self._select_one(sql, card_key)
        if res:
            print('card_key exists')
            return res[0]
        sql = """insert into cs_card(card_key) values(?)"""
        self._execute(sql, card_key)
        self.commit()
        sql = """select card_id from cs_card where card_key=?"""
        res = self._select_one(sql, card_key)
        return res[0]

    def find_card_user(self, card_id):
        sql = """select user_id from cs_user where card_id = ?"""
        res = self._select_one(sql, card_id)
        if not res:
            return 0
        return res[0]

    def get_users(self):
        sql = """select user_id, user_key, user_name, party_id 
                from cs_user  """
        result = self._select(sql)
        return result

    def get_user(self, user_id=None, user_key=None  ):
        if not user_key and not user_id:
            return []
        sql = """select user_id, user_key, user_name, party_id from cs_user """
        sql_where = ''
        if user_id:
            sql_where = """where user_id = ?"""
            srch = user_id
        elif user_key:
            sql_where = """where user_key = ?"""
            srch = user_key
        sql = sql + sql_where
        result = self._select_one(sql, srch)
        return result

    def get_user_full(self, user_id):
        if not user_id:
            return []
        sql = """select user_id, user_key, user_name, party_id, card_id, can_vote from cs_user """
        sql_where = ''
        sql_where = """where user_id = ?"""
        srch = user_id

        sql = sql + sql_where
        result = self._select_one(sql, srch)
        return result

    def save_user(self, user_id=None, user_key='', user_name='', party_id=None, can_vote=0):
        # sql = """
        #     insert into cs_user(user_id, user_key, user_name, party_id)
        #     values(?, ?, ?, ?)
        #     on confict(user_id)
        #     do update set user_key = ?, user_name=?, party_id=?
        #     """
        if isinstance(can_vote, (str, bytes)) and can_vote.isdigit():
            can_vote = int(can_vote)
        if can_vote:
            can_vote = 1
        else:
            can_vote = 0

        sql_exists = """select user_id from cs_user where user_id=?"""

        sql_insert = """
                    insert into cs_user(user_id, user_key, user_name, party_id, can_vote)
                    values(?, ?, ?, ?, ?)
                    
                    """
        sql_update = """update cs_user set user_key = ?, user_name=?, party_id=?, can_vote=? where user_id=?"""
        cursor = self._execute(sql_exists, user_id)
        res = cursor.fetchone()
        if not res:
            #print('insert')
            cursor.execute(sql_insert, (user_id, user_key, user_name, party_id, can_vote))
        else:
            #print('update')
            cursor.execute(sql_update, (user_key, user_name, party_id, can_vote, user_id))
        cursor.close()
        self.db.commit()

    def get_positions(self):
        sql = """select pos_id, pos_user_id, pos_group_id from cs_group_position"""
        result = self._select(sql)
        return result

    def get_user_from_position(self, position_id, group_id=0):
        sql = """select pos_user_id from cs_group_position where pos_id=? and pos_group_id=?"""
        result = self._select_one(sql, position_id, group_id)
        print('db get_user_from_position', result)
        if result:
            return result[0]
        return 0

    def get_users_and_positions(self, group_id=0):
        # sql = """select user_id,
        #         user_name,
        #         pos_id,
        #         party_id,
        #         pos_group_id
        #         from cs_user
        #         left outer join cs_group_position
        #             on cs_user.user_id = cs_group_position.pos_user_id
        #         left out join cs_card on cs_card.card_id = cs_user.card_id
        #         where pos_group_id = ?
        #         order by user_name"""
        sql = """select user_id,
                        user_name,
                        party_id,
                        card_id,
                        can_vote
                        from cs_user 
                        order by user_name"""
        users = self._select(sql)
        sql = """select pos_user_id,
                        pos_id,
                        pos_group_id from
                        cs_group_position  
                        where pos_group_id = ?
                        """
        positions = self._select(sql, group_id)
        sql = """select card_id, card_key from cs_card order by card_id"""
        cards = self._select(sql)
        result = []
        for user in users:
            mic_id = 0 # mic_id ~ pos_id
            card_key = ''
            #found = False
            for position in positions:
                if user[0] == position[0]:
                    mic_id = position[1]
                    #found = True
                    break
            for card in cards:
                if user[3] == card[0]:
                    card_key = card[1]
                    break
            #if found:database.py
            result.append((user[0], user[1], mic_id, user[2], group_id, card_key, user[4]))
        #for r in result:
        #    print(r)
        return result

    def map_cards(self, cards, card_id):
        card_key = ''
        for card_id_val, card_key_val in cards:
            if card_id == card_id_val:
                return card_key_val
        return ''

    def get_user_and_position(self, user_id, group_id=0):
        cards = self.get_cards()
        sql = """select user_id,
                user_name,
                pos_id,
                party_id,
                pos_group_id, 
                card_id,
                can_vote
                from cs_user 
                left outer join cs_group_position on cs_user.user_id = cs_group_position.pos_user_id
                where user_id = ? and pos_group_id=?
                order by user_id"""
        result = self._select_one(sql, user_id, group_id)
        print(result, '----')
        if not result:
            sql = """select user_id,
                            user_name,
                            party_id,
                            card_id, 
                            can_vote
                            from cs_user 
                            where user_id = ?
                            order by user_id"""
            result = self._select_one(sql, user_id)

            if result:
                card_key = self.map_cards(cards, result[3])
                result = (result[0], result[1], 0, result[2], group_id, card_key, result[4])
        else:
            card_key = self.map_cards(cards, result[5])
            result = (result[0], result[1], result[2], result[3], result[4], card_key, result[6])
            print('get_user_and_position', result)
        return result

    def decouple_user(self, user_id, group_id=0):
        sql = """delete from  cs_group_position where pos_user_id=? and pos_group_id=?"""
        cursor = self._execute(sql, user_id, group_id)

    def save_position(self, position_id, user_id, group_id=0):
        # clear the position


        sql_exists = """select pos_id, pos_user_id from cs_group_position where pos_id=? and pos_group_id=?"""
        sql_insert = """insert into cs_group_position(pos_group_id, pos_id, pos_user_id) values(?, ?, ?)"""
        sql_update = """update cs_group_position set pos_user_id=? where pos_id=? and pos_group_id=?"""

        cursor = self._execute(sql_exists, position_id, group_id)
        res = cursor.fetchone()
        if not res:
            #print('insert')
            cursor.execute(sql_insert, (group_id, position_id, user_id))
        else:
            #print('update')
            cursor.execute(sql_update, (user_id, position_id, group_id))
        cursor.close()
        self.db.commit()

    def get_parties(self):
        sql = """select party_id, party_key, party_name, party_logo_name from  cs_party order by party_key"""
        result = self._select(sql)
        return result

    def get_party_logo_name(self, party_id=0):
        if not party_id:
            return ''
        sql = """select party_logo_name from  cs_party
                 where party_id = ?
        
        """
        result = self._select_one(sql, party_id)
        if result:
            party_logo_name = result[0]
            #party_logo_name = party_logo_name[0]
            return party_logo_name
        return ''

    def get_message(self, message_id=None, message_key=None):
        if not message_id and not message_key:
            return ''
        if message_id:
            srch_key = message_id
            sql_where = """where message_id=?"""
        elif message_key:
            srch_key = message_key
            sql_where = """where message_key=?"""

        sql = """select message_id, message_key, message_value 
                    from cs_message """
        sql = sql + sql_where
        result = self._select_one(sql, srch_key)
        if result:
            return result[0]
        return 0


    def set_message(self, message_id, message_key, message_value):
        sql_exists = """select message_id, message_key, message_value from cs_message where message_id=?"""
        sql_insert = """insert into cs_message(message_id, message_key, message_value) values(?, ?, ?)"""
        sql_update = """update cs_message set message_key=?, message_value=? where message_id=?"""

        cursor = self.db.cursor()
        cursor.execute(sql_exists, (message_id,))
        res = cursor.fetchone()
        if not res:
            cursor.execute(sql_insert, (message_id, message_key, message_value))
        else:
            cursor.execute(sql_update, (message_key, message_value, message_id, ))
        self.db.commit()
        cursor.close()

    def disconnect(self):
        if self.db:
            self.db.close()
        self.db = None


    def commit(self):
        self.db.commit()

    def list_db(self, group_id):
        db = self.db
        db.row_factory = SQL.Row
        c = db.cursor()
        sql = """select * from cs_party order by party_id asc"""
        c.execute(sql)
        parties = c.fetchall()
        sql = """select user_id, user_name, party_id, can_vote, cs_group_position.pos_id as mic_id from cs_user 
                left outer join cs_group_position on pos_user_id = user_id
                where party_id is not null 
                and cs_group_position.pos_group_id = ?
                order by party_id, user_name"""
        c.execute(sql, (group_id,))
        users = c.fetchall()

        return parties, users

# ---
class User(object):
    def __init__(self, user_id, user_key, user_name, party_id, card_id, can_vote):
        self.user_id = user_id
        self.user_key  = user_key
        self.user_name = user_name
        self.party_id = party_id
        self.card_id = card_id
        self.can_vote = can_vote
# ---
def check():
    pass

# ---
def test():
    print(SQL.version)
    t1 = time.time()
    x = DB()
    x.connect()

    # print(x.get_message(1))
    res = x.get_users_and_positions(1)
    x.save_position(0,4,1)
    x.get_user_from_position(1,1)
    x.save_position(1, 4, 1)
    print(res)
    x.disconnect()

    #print(t2-t1)

def run():
    test()
# ---
if __name__ == "__main__":
    run()
