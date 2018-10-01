# import pymysql
import sqlite3
import time


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class DB:
    def __init__(self, filename): #host, port, user, passwd, db):
        # self.db_conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)
        try:
            self.db_conn = sqlite3.connect(filename)
            self.db_conn.row_factory = dict_factory
            print('Checking if db is populated with npcs')
            self.fetch_npcs()
            print('Found npcs')
        except:
            print('No npcs found, re-populating db')
            query = open('database-dump.sql', 'r').read()
            self.db_conn.executescript(query)
            self.db_conn.commit()


    def fetch_npcs(self):
        db_cursor = self.db_conn.cursor()
        try:
            db_cursor.execute('SELECT * FROM tbl_NPC;')
            db_response = db_cursor.fetchall()
        finally:
            db_cursor.close()

        npcs = {}

        if db_response:
            for dict_row in db_response:
                seconds = int(time.time())
                dict_row['timeTalked'] = seconds
                dict_row['talkDelay'] = 0
                dict_row['lastCombatAction'] = seconds

                dict_row['vocabulary'] = dict_row['vocabulary'].split('|')
                dict_row['isInCombat'] = 0
                dict_row['lastRoom'] = None
                dict_row['corpseTTL'] = 10
                dict_row['whenDied'] = None

                id = dict_row['id']
                npcs[id] = dict_row

        return npcs


    def fetch_env_vars(self):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute('SELECT * FROM tbl_ENV;')
        db_response = db_cursor.fetchall()
        db_cursor.close()

        env = {}

        for en in db_response:
            env[en['id']] = {
                'name': en['name'],
                'room': en['room'],
                'vocabulary': en['vocabulary'].split('|'),
                'talkDelay': en['delay'],
                'timeTalked': int(time.time()),
                'lastSaid': 0,
            }

        return env


    def fetch_all_items(self):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("SELECT * FROM tbl_Items;")
        db_response = db_cursor.fetchall()
        db_cursor.close()

        item_dict = {}

        if db_response:
            for dict_row in db_response:
                id = dict_row['id']
                item_dict[id] = dict_row

        return item_dict


    def fetch_player_by_name_and_password(self, name, password):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("SELECT name FROM tbl_Players WHERE name = ? and pwd = ? ;", (name, password))
        row = db_cursor.fetchone()
        db_cursor.close()
        return row


    def fetch_player(self, name):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute(
            '''
                SELECT * 
                FROM tbl_Players 
                WHERE 
                    name = ?
                ;
            ''', (name, ))
        db_response = db_cursor.fetchone()
        db_cursor.close()

        if not db_response or not len(db_response):
            return None
        else:
            return {
                'room' : db_response[1],
                'lvl' : db_response[2],
                'exp' : db_response[3],
                'str' : db_response[4],
                'per' : db_response[5],
                'endu' : db_response[6],
                'cha' : db_response[7],
                'int' : db_response[8],
                'agi' : db_response[9],
                'luc' : db_response[10],
                'cred' : db_response[11],
                'inv' : db_response[12].split(',').filter(lambda it: it not in ('', ' ')),
                'pwd': db_response[13],
                'clo_head' : db_response[14],
                'clo_larm' : db_response[15],
                'clo_rarm' : db_response[16],
                'clo_lhand' : db_response[17],
                'clo_rhand' : db_response[18],
                'clo_chest' : db_response[19],
                'clo_lleg' : db_response[20],
                'clo_rleg' : db_response[21],
                'clo_feet' : db_response[22],
                'imp_head' : db_response[23],
                'imp_larm' : db_response[24],
                'imp_rarm' : db_response[25],
                'imp_lhand' : db_response[26],
                'imp_rhand' : db_response[27],
                'imp_chest' : db_response[28],
                'imp_lleg' : db_response[29],
                'imp_rleg' : db_response[30],
                'imp_feet' : db_response[31],
                'hp' : db_response[32],
                'charge' : db_response[33],
                'isInCombat' : 0,
                'lastCombatAction' : int(time.time()),
                'isAttackable' : 1,
                'corpseTTL' : 60
            }


    def save_player(self, p):
        db_cursor = self.db_conn.cursor()
        query = '''
            UPDATE tbl_Players 
            SET 
                room = '{room}',
                exp  = {exp},
                str  = {str},
                per  = {per},
                endu = {endu},
                cha  = {cha},
                inte  = {int},
                agi  = {agi},
                luc  = {luc},
                cred = {cred},
                inv  = '{inv}',
                pwd  = '{pwd}',

                clo_head  = {clo_head},
                clo_larm  = {clo_larm},
                clo_rarm  = {clo_rarm},
                clo_lhand = {clo_lhand},
                clo_rhand = {clo_rhand},
                clo_chest = {clo_chest},
                clo_lleg  = {clo_lleg},
                clo_rleg  = {clo_rleg},

                clo_feet  = {clo_feet},
                imp_head  = {imp_head},
                imp_larm  = {imp_larm},
                imp_rarm  = {imp_rarm},
                imp_lhand = {imp_lhand},
                imp_rhand = {imp_rhand},
                imp_chest = {imp_chest},
                imp_lleg  = {imp_lleg},
                imp_rleg  = {imp_rleg},
                imp_feet  = {imp_feet},

                hp = {hp},
                charge = {charge},
                lvl = {lvl} 
            WHERE name = '{name}';
            '''.format(
                room = p["room"] or '', 
                exp  = p["exp"] or 0, 
                str  = p["str"] or 0, 
                per  = p["per"] or 0,
                endu = p["endu"] or 0, 
                cha  = p["cha"] or 0, 
                int  = p["int"] or 0, 
                agi  = p["agi"] or 0, 
                luc  = p["luc"] or 0, 
                cred = p["cred"] or 0, 
                inv  = ",".join(p["inv"] or []),
                pwd  = p["pwd"],

                clo_head  = p["clo_head"] or 0, 
                clo_larm  = p["clo_larm"] or 0, 
                clo_rarm  = p["clo_rarm"] or 0, 
                clo_lhand = p["clo_lhand"] or 0, 
                clo_rhand = p["clo_rhand"] or 0, 
                clo_chest = p["clo_chest"] or 0, 
                clo_lleg  = p["clo_lleg"] or 0, 
                clo_rleg  = p["clo_rleg"] or 0, 

                clo_feet  = p["clo_feet"] or 0, 
                imp_head  = p["imp_head"] or 0, 
                imp_larm  = p["imp_larm"] or 0, 
                imp_rarm  = p["imp_rarm"] or 0, 
                imp_lhand = p["imp_lhand"] or 0, 
                imp_rhand = p["imp_rhand"] or 0, 
                imp_chest = p["imp_chest"] or 0, 
                imp_lleg  = p["imp_lleg"] or 0, 
                imp_rleg  = p["imp_rleg"] or 0, 
                imp_feet  = p["imp_feet"] or 0, 

                hp = p["hp"] or 0, 
                charge = p["charge"] or 0, 
                lvl = p["lvl"] or 0,
                name = p["name"]
            )
        db_cursor.execute(query)
        self.db_conn.commit()
        db_cursor.close()
        return db_cursor.rowcount


    def save_players(self, players):
        db_cursor = self.db_conn.cursor()
        for pl in players.values():
            if pl['authenticated'] is not None:
                self.save_player(pl)
                self.db_conn.commit()
        db_cursor.close()

