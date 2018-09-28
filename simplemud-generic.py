#!/usr/bin/python
# -*- coding: utf-8 -*-

import pymysql
import time

from copy import deepcopy
from random import randint

from cmsg import cmsg
from functions import log
from mudserver import MudServer


def fetch_env_vars(db_cursor):
    # Fetch tbl_ENV and populate env[]
    db_cursor.execute("SELECT * FROM tbl_ENV")
    db_response = cursor.fetchall()
    env = {}
    for en in db_response:
        env[en[0]] = {
        'name': en[1],
        'room': en[2],
        'vocabulary': en[3].split('|'),
        'talkDelay': en[4],
        'timeTalked': int(time.time()),
        'lastSaid': 0,
    }
    return env


def fetch_npcs(db_conn):
    db_cursor = db_conn.cursor(pymysql.cursors.DictCursor)
    db_cursor.execute("SELECT * FROM tbl_NPC;")
    db_response = cursor.fetchall()
    db_cursor.close()

    npcs = {}

    if db_response:
        for dict_row in db_response:
            seconds = int(time.time())
            dict_row['timeTalked'] = seconds
            dict_row['lastCombatAction'] = seconds

            dict_row['vocabulary'] = dict_row['vocabulary'].split('|')
            dict_row['isInCombat'] = 0
            dict_row['lastRoom'] = None
            dict_row['corpseTTL'] = 10
            dict_row['whenDied'] = None

            id = dict_row['id']
            npcs[id] = dict_row

    return npcs


def fetch_all_items(db_conn):
    db_cursor = db_conn.cursor(pymysql.cursors.DictCursor)
    db_cursor.execute("SELECT * FROM tbl_Items;")
    db_response = cursor.fetchall()
    db_cursor.close()

    item_dict = {}

    if db_response:
        for dict_row in db_response:
            id = dict_row['id']
            item_dict[id] = dict_row

    return item_dict


def fetch_player(db_cursor, name, password):
    db_cursor.execute(
        '''
            SELECT * 
            FROM tbl_Players 
            WHERE 
                name = %s
                AND password = %s
            ;
        ''', (name, password))
    db_response = db_cursor.fetchone()
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


def save_player(db_cursor, p):
    # print('Saving' + p['name'])
    db_cursor.execute('''
        UPDATE tbl_Players 
        SET 
            room = {room},
            exp  = {exp},
            str  = {str},
            per  = {per},
            endu = {endu},
            cha  = {cha},
            int  = {int},
            agi  = {agi},
            luc  = {luc},
            cred = {cred},
            inv  = '{inv}',

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
            room = p["room"], 
            exp  = p["exp"], 
            str  = p["str"], 
            per  = p["per"], 
            endu = p["endu"], 
            cha  = p["cha"], 
            int  = p["int"], 
            agi  = p["agi"], 
            luc  = p["luc"], 
            cred = p["cred"], 
            inv  = ",".join(p["inv"]),

            clo_head  = p["clo_head"], 
            clo_larm  = p["clo_larm"], 
            clo_rarm  = p["clo_rarm"], 
            clo_lhand = p["clo_lhand"], 
            clo_rhand = p["clo_rhand"], 
            clo_chest = p["clo_chest"], 
            clo_lleg  = p["clo_lleg"], 
            clo_rleg  = p["clo_rleg"], 

            clo_feet  = p["clo_feet"], 
            imp_head  = p["imp_head"], 
            imp_larm  = p["imp_larm"], 
            imp_rarm  = p["imp_rarm"], 
            imp_lhand = p["imp_lhand"], 
            imp_rhand = p["imp_rhand"], 
            imp_chest = p["imp_chest"], 
            imp_lleg  = p["imp_lleg"], 
            imp_rleg  = p["imp_rleg"], 
            imp_feet  = p["imp_feet"], 

            hp = p["hp"], 
            charge = p["charge"], 
            name = p["name"]
        ))


def save_players(db_conn, players):
    db_cursor = db_conn.cursor()
    for pl in players.values():
        if pl['authenticated'] is not None:
            # print('Saving' + p['name'])
            save_player(db_cursor, pl)
            db_conn.commit()
    db_cursor.close()


def create_corpse(body):
    return { 
        'room': body['room'], 
        'name': str(body['name'] + '`s corpse'), 
        'inv' : body['inv'], 
        'died': int(time.time()), 
        'TTL' : body['corpseTTL'], 
        'owner': 1
    }


log("", "Server Boot")


# Load rooms
rooms = {
    '$rid=0$': {'description': 'You wake up in your private quarter aboard the Mariner spacecraft. Your room is dark, the only source of light being a wall screen displaying current time of day on Earth. You can hear a distant hum of ventilation equipment and a characteristic buzz of FTL engines, currently pushing you through a vast, unknown expand of space.',
                'exits': {'door': '$rid=1$', 'bathroom': '$rid=4$'},
                'name': 'Private Quarter'},
    '$rid=1$': {'description': 'You are standing in a wide corridor, which circles around the second level of the craft. Private quarters of other crew members are located on this level. A broken ceiling light flickers every few seconds. The air pumped through the vents is chilly and refreshing.',
                'exits': {'quarter door': '$rid=0$',
                'north': '$rid=2$', 'south': '$rid=3$'},
                'name': 'Corridor'},
    '$rid=2$': {'description': 'You are in a corridor. It ends here abruptly with a dead end.',
                'exits': {'south': '$rid=1$'},
                'name': 'Corridor'},
    '$rid=3$': {'description': "You are standing in the middle of a wide corridor. It's impossible to venture further south, a pile of rubble is blocking the way.",
                'exits': {'north': '$rid=1$'},
                'name': 'Corridor'},
    '$rid=4$': {'description': 'You are standing in a tiny bathroom, which is part of a private quarter aboard Mariner. Only bare essentials here, certainly nothing luxurious.',
                'exits': {'door': '$rid=0$'},
                'name': 'Small Bathroom'},
    '$rid=666$': {'description': 'Void. This is how you would describe your surroundings. You realise you cannot see your physical body and somehow it feels like you are not ACTUALLY there in a physical sense. It`s unbelievably bright here. You can see a slightly darker patch in a distance. It almost looks like an open rift, a tear in whatever fabric the environment is made of.',
                'exits': {'rift': '$rid=0$'},
                'name': 'Void'},
    }

log("Rooms loaded: " + str(len(rooms)), "info")

# Declare NPCs master (template) tuple
npcsTemplate = {}

corpses = {}
env = {}
fights = {}
itemsDB = {}
itemsInWorld = {}
npcs = {}

# Declare number of seconds to elapse between State Saves
# A State Save takes values held in memory and updates the database
# at set intervals to achieve player state persistence
stateSaveInterval = 10
log("State Save interval: " + str(stateSaveInterval) + " seconds", "info")

# Set last state save to 'now' on server boot
lastStateSave = int(time.time())

# Database connection details
DBhost = 'localhost'
DBport = 3306
DBuser = '<user>'
DBpasswd = '<password>'
DBdatabase = '<database>'

log("Connecting to database", "info")
cnxn = pymysql.connect(host=DBhost, port=DBport, user=DBuser, passwd=DBpasswd, db=DBdatabase)
cursor = cnxn.cursor()

npcs = fetch_npcs(cnxn)
log("NPCs loaded: " + str(len(npcs)), "info")

# Deepcopy npcs fetched from a database into a master template
npcsTemplate = deepcopy(npcs)

env = fetch_env_vars(cursor)
log("Environment Actors loaded: " + str(len(env)), "info")

itemsDB = fetch_all_items(cnxn)
log("Items loaded: " + str(len(itemsDB)), "info")

# Put some items in the world for testing and debugging
itemsInWorld['$rid=1$'] = [
    { 'id': 200001, 'room': '$rid=1$', 'whenDropped': 1533133523, 'lifespan': 90000000, 'owner': 1},
    { 'id': 200002, 'room': '$rid=1$', 'whenDropped': 1533133523, 'lifespan': 90002000, 'owner': 2},
    { 'id': 200001, 'room': '$rid=1$', 'whenDropped': 1533433523, 'lifespan': 90003000, 'owner': 1}
]

# List items in world for debugging purposes
# for x in itemsInWorld:
    # print (x)
    # for y in itemsInWorld[x]:
        # print(y,':',itemsInWorld[x][y])
        
# Close a database connection, all data has been fetched to memory
log("Closing database connection", "info")
cursor.close()
cnxn.close()

# Connect to the database
# cnxn = pymysql.connect(host=DBhost, port=DBport, user=DBuser, passwd=DBpasswd, db=DBdatabase)

# stores the players in the game
players = {}

# start the server
mud = MudServer()


# main game loop. We loop forever (i.e. until the program is terminated)
while True:

    # pause for 1/5 of a second on each loop, so that we don't constantly
    # use 100% CPU time
    time.sleep(0.1)

    # 'update' must be called in the loop to keep the game running and give
    # us up-to-date information
    mud.update()

    # Check if State Save is due and execute it if required
    now = int(time.time())
    if now >= lastStateSave + stateSaveInterval:
        # print("[info] Saving player state")
        
        # State Save logic
        cnxn = pymysql.connect(host=DBhost, port=DBport, user=DBuser, passwd=DBpasswd, db=DBdatabase)
        save_players(cnxn, players)
        cnxn.close()
        lastStateSave = now

    # Handle Player Deaths
    for (pid, pl) in players.items():
        if pl['authenticated'] == True:
            if pl['hp'] <= 0:
                # Create player's corpse in the room
                corpses.append(create_corpse(pl))

                # Clear player's inventory, it stays on the corpse
                # This is bugged, causing errors when picking up things after death
                # players[pid]['inv'] = ''
                pl['isInCombat'] = 0
                pl['lastRoom'] = pl['room']
                pl['room'] = '$rid=666$'

                fights = {
                    fight_id: fight for fight_id, fight in fights.items()
                    if fight['s1id'] != pid and fight['s2id'] != pid
                }

                for (pid2, pl_2) in players.items():
                    if pl_2['authenticated'] is not None \
                        and pl_2['room'] == pl['lastRoom'] \
                        and pl_2['name'] != pl['name']:
                        mud.send_message(pid2, '<u><f32>{}<r> <f124>has been killed.'.format(pl['name']))
                pl['lastRoom'] = None
                mud.send_message(pid, '<b88><f158>Oh dear! You have died!')
                pl['hp'] = 4

    # Handle Fights
    for fighter in fights.values():
        # PC -> PC
        s1id = fighter['s1id']
        s2id = fighter['s2id']
        player_1 = players[s1id]
        player_2 = players[s2id]

        if fighter['s1type'] == 'pc' and fighter['s2type'] == 'pc':
            if player_1['room'] == player_2['room']:
                if int(time.time()) >= player_1['lastCombatAction'] + 10 - player_1['agi']:
                    if player_2['isAttackable'] == 1:
                        player_1['isInCombat'] = 1
                        player_2['isInCombat'] = 1
                        # Do damage to the PC here
                        if randint(0, 1) == 1:
                            modifier = randint(0, 10)
                            if player_1['hp'] > 0:
                                player_2['hp'] = player_2['hp'] - (player_1['str'] + modifier)
                                player_1['lastCombatAction'] = int(time.time())
                                mud.send_message(s1id, 'You manage to hit <f32><u>' + player_2['name'] + '<r> for <f0><b2>' + str(player_1['str'] + modifier) + '<r> points of damage.')
                                mud.send_message(s2id, '<f32>' + player_1['name'] + '<r> has managed to hit you for <f15><b88>' + str(player_1['str'] + modifier) + '<r> points of damage.')
                                # print('----------')
                                # print(player_1['name'] + ': ' + str(player_1['hp']))
                                # print(player_2['name'] + ': ' + str(player_2['hp']))
                        else:
                            player_1['lastCombatAction'] = int(time.time())
                            mud.send_message(s1id, 'You miss trying to hit <f32><u>' + player_2['name'] + '')
                            mud.send_message(s2id, '<f32><u>' + player_1['name'] + '<r> missed while trying to hit you!')
                    else:
                        mud.send_message(s1id, '<f225>Suddnely you stop. It wouldn`t be a good idea to attack <f32>' + player_2['name'] + ' at this time.')

                        fights = {fight_id: fight for fight_id, fight in fights.items() if fight['s1id'] != s1id or fight['s2id'] != s2id}

        # PC -> NPC
        elif fighter['s1type'] == 'pc' and fighter['s2type'] == 'npc':
            npc_2 = npcs[s2id]
            if player_1['room'] == npc_2['room']:
                if int(time.time()) >= player_1['lastCombatAction'] + 10 - player_1['agi']:
                    if npc_2['isAttackable'] == 1:
                        player_1['isInCombat'] = 1
                        npc_2['isInCombat'] = 1
                        # Do damage to the NPC here
                        if randint(0, 1) == 1:
                            modifier = randint(0, 10)
                            if player_1['hp'] > 0:
                                npc_2['hp'] = npc_2['hp'] - (player_1['str'] + modifier)
                                player_1['lastCombatAction'] = int(time.time())
                                mud.send_message(s1id, 'You manage to hit <f21><u>' + npc_2['name'] + '<r> for <b2><f0>' + str(player_1['str'] + modifier)  + '<r> points of damage')
                                # print(npc_2['hp'])
                        else:
                            player_1['lastCombatAction'] = int(time.time())
                            mud.send_message(s1id, 'You miss <u><f21>' + npc_2['name'] + '<r> completely!')
                    else:
                        mud.send_message(s1id, '<f225>Suddenly you stop. It wouldn`t be a good idea to attack <u><f21>' + npc_2['name'] + '<r> at this time.')
                        fights = {fight_id: fight for fight_id, fight in fights.items() if fight['s1id'] != s1id or fight['s2id'] != s2id}

        # NPC -> PC
        elif fighter['s1type'] == 'npc' and fighter['s2type'] == 'pc':
            npc_1 = npcs[s1id]
            if npc_1['room'] == player_2['room']:
                if int(time.time()) >= npc_1['lastCombatAction'] + 10 - npc_1['agi']:
                    npc_1['isInCombat'] = 1
                    player_2['isInCombat'] = 1
                    # Do the damage to PC here
                    if randint(0, 1) == 1:
                        modifier = randint(0, 10)
                        if npc_1['hp'] > 0:
                            player_2['hp'] = player_2['hp'] - (npc_1['str'] + modifier)
                            npc_1['lastCombatAction'] = int(time.time())
                            mud.send_message(s2id, '<f21><u>' + npc_1['name'] + '<r> has managed to hit you for <f15><b88>' + str(npc_1['str'] + modifier) + '<r> points of damage.')
                    else:
                        npc_1['lastCombatAction'] = int(time.time())
                        mud.send_message(s2id, '<f21><u>' + npc_1['name'] + '<r> has missed you completely!')
        elif fighter['s1type'] == 'npc' and fighter['s2type'] == 'npc':
            test = 1
            # NPC -> NPC
            

    # Iterate through NPCs, check if its time to talk, then check if anyone is attacking it
    for (nid, npc) in npcs.items():
        # Check if any player is in the same room, then send a random message to them
        now = int(time.time())
        if now > npc['timeTalked'] + npc['talkDelay']:
            rnd = randint(0, len(npc['vocabulary']) - 1)
            for (pid, pl) in players.items():
                if npc['room'] == pl['room']:
                    if len(npc['vocabulary']) > 1:
                        #mud.send_message(pid, npc['vocabulary'][rnd])
                        msg = '<f21><u>' + npc['name'] + '<r> says: <f86>' + npc['vocabulary'][rnd]
                        mud.send_message(pid, msg)
                    else:
                        #mud.send_message(pid, npc['vocabulary'][0])
                        msg = '<f21><u>' + npc['name'] + '<r> says: <f86>' + npc['vocabulary'][0]
                        mud.send_message(pid, msg)
            npc['timeTalked'] =  now
        # Iterate through fights and see if anyone is attacking an NPC - if so, attack him too if not in combat (TODO: and isAggressive = true)
        for fight in fights.values():
            fs1id = fight['s1id']
            fs2id = fight['s2id']
            npc2 = npcs[fs2id]

            if fs2id == nid and npc2['isInCombat'] == 1 and fight['s1type'] == 'pc' and fight['retaliated'] == 0:
                # print('player is attacking npc')
                # BETA: set las combat action to now when attacking a player
                npc2['lastCombatAction'] = int(time.time())
                fight['retaliated'] = 1
                npc2['isInCombat'] = 1
                fights[len(fights)] = {
                    's1': npc2['name'],
                    's2': players[fs1id]['name'],
                    's1id': nid,
                    's2id': fs1id,
                    's1type': 'npc',
                    's2type': 'pc',
                    'retaliated': 1
                }
            elif fs2id == nid and npc2['isInCombat'] == 1 and fight['s1type'] == 'npc' and fight['retaliated'] == 0:
                # print('npc is attacking npc')
                # BETA: set las combat action to now when attacking a player
                npc2['lastCombatAction'] = int(time.time())
                fight['retaliated'] = 1
                npc2['isInCombat'] = 1
                fights[len(fights)] = {
                    's1': npc2['name'],
                    's2': players[fs1id]['name'], 
                    's1id': nid, 
                    's2id': fs1id, 
                    's1type': 'npc', 
                    's2type': 'npc', 
                    'retaliated': 1
                }
        # Check if NPC is still alive, if not, remove from room and create a corpse, set isInCombat to 0, set whenDied to now and remove any fights NPC was involved in
        if npc['hp'] <= 0:
            npc['isInCombat'] = 0
            npc['lastRoom'] = npc['room']
            npc['whenDied'] = int(time.time())
            fights = {fight_id: fight for fight_id, fight in fights.items() if fight['s1id'] != nid and fight['s2id'] != nid}

            corpses.append(create_corpse(npc))

            for (pid, pl) in players.items():
                if pl['authenticated'] is not None and pl['room'] == npc['room']:
                    mud.send_message(pid, "<f32><u>{}<r> <f88>has been killed.".format(npc['name']))
            npc['room'] = None
            npc['hp'] = npcsTemplate[nid]['hp']

    # Iterate through ENV elements and see if it's time to send a message to players in the same room as the ENV elements
    for e in env.values():
        now = int(time.time())
        if now > e['timeTalked'] + e['talkDelay']:
            rnd = randint(0, len(e['vocabulary']) - 1)
            for (pid, pl) in players.items():
                if e['room'] == pl['room']:
                    if len(e['vocabulary']) > 1:
                        msg = '<f58>[' + e['name'] + ']: <f236>' + e['vocabulary'][rnd]
                        mud.send_message(pid, msg)
                    else:
                        msg = '<f58>[' + e['name'] + ']: <f236>' + e['vocabulary'][0]
                        mud.send_message(pid, msg)
            e['timeTalked'] =  now

    # Keep corpses not older than their TTL
    corpses = {id: corpse for id, corpse in corpses.items() if int(time.time()) < corpse['died'] + corpse['TTL']}

    # Handle NPC respawns
    for (nid, npc) in npcs.items():
        if npc['whenDied'] is not None and int(time.time()) >= npc['whenDied'] + npc['respawn']:
            npc['whenDied'] = None
            npc['room'] = npcsTemplate[nid]['room']
            # print("respawning " + npcs[nid]['name'])

    # go through any newly connected players
    for id in mud.get_new_players():
        # add the new player to the dictionary, noting that they've not been
        # named yet.
        # The dictionary key is the player's id number. We set their room to
        # None initially until they have entered a name
        # Try adding more player stats - level, gold, inventory, etc
        players[id] = {
            'name': None,
            'room': None,
            'lvl': None,
            'exp': None,
            'str': None,
            'per': None,
            'endu': None,
            'cha': None,
            'int': None,
            'agi': None,
            'luc': None,
            'cred': None,
            'inv': [],
            'authenticated': None,
            'clo_head': None,
            'clo_larm': None,
            'clo_rarm': None,
            'clo_lhand': None,
            'clo_rhand': None,
            'clo_chest': None,
            'clo_lleg': None,
            'clo_rleg': None,
            'clo_feet': None,
            'imp_head': None,
            'imp_larm': None,
            'imp_rarm': None,
            'imp_lhand': None,
            'imp_rhand': None,
            'imp_chest': None,
            'imp_lleg': None,
            'imp_rleg': None,
            'imp_feet': None,
            'hp': None,
            'charge': None,
            'isInCombat': None,
            'lastCombatAction': None,
            'isAttackable': None,
            'lastRoom': None,
            'corpseTTL': None,
            }

        # send the new player a prompt for their name
        # mud.send_message(id, 'Connected to server!')
        mud.send_message(id, "<f250><b25> ______            _______ ")
        mud.send_message(id, "<f250><b25>(  __  \ |\     /|(       )")
        mud.send_message(id, "<f250><b25>| (  \  )| )   ( || () () |")
        mud.send_message(id, "<f250><b25>| |   ) || |   | || || || |")
        mud.send_message(id, "<f250><b25>| |   | || |   | || |(_)| |")
        mud.send_message(id, "<f250><b25>| |   ) || |   | || |   | |")
        mud.send_message(id, "<f250><b25>| (__/  )| (___) || )   ( |")
        mud.send_message(id, "<f250><b25>(______/ (_______)|/     \|")
        mud.send_message(id, " ")
        mud.send_message(id, "<f250><b25> a modern MU* engine       ")
        mud.send_message(id, "<f15><b25>    dumengine.wikidot.com  ")
        mud.send_message(id, " ")
        mud.send_message(id, "<f250><b25> Development Server 1       ")
        mud.send_message(id, " ")
        mud.send_message(id, '<f15>What is your username?')
        log("Client ID: " + str(id) + " has connected", "info")

    # go through any recently disconnected players
    for id in mud.get_disconnected_players():

        # if for any reason the player isn't in the player map, skip them and
        # move on to the next one
        if id not in players:
            continue
        
        log("Client ID:" + str(id) + " has disconnected (" + str(players[id]['name']) + ")", "info")
        
        # go through all the players in the game
        for (pid, pl) in players.items():
            # send each player a message to tell them about the diconnected
            # player if they are in the same room
            if (players[pi]['authenticated'] is not None 
                     and pl['authenticated'] is not None
                     and pl['room'] == players[id]['room'] 
                     and pl['name'] != players[id]['name']):
                mud.send_message(pid, "<f32><u>{}<r>'s body has vanished.".format(players[id]['name']))

        # Code here to save player to the database after he's disconnected and before removing him from players dictionary
        if players[id]['authenticated'] is not None:
            cnxn = pymysql.connect(host=DBhost, port=DBport, user=DBuser, passwd=DBpasswd, db=DBdatabase)
            cursor = cnxn.cursor()
            log("Player disconnected, saving state", "info")
            save_player(cursor, players[id])
            cnxn.commit()
            cnxn.close()

        # TODO: IDEA - Some sort of a timer to have the character remain in the game for some time after disconnection?

        # Filter out fights with disconnected player
        fights = {
            fight_id: fight for fight_id, fight in fights.items() 
            if fight['s1'] != player_name and fight['s2'] != player_name
        }

        # remove the player's entry in the player dictionary
        del players[id]

    # go through any new commands sent from players
    for (id, command, params) in mud.get_commands():
        # if for any reason the player isn't in the player map, skip them and
        # move on to the next one
        if id not in players:
            continue

        # if the player hasn't given their name yet, use this first command as
        # their name and move them to the starting room.
        if players[id]['name'] is None:
            cnxn = pymysql.connect(host=DBhost, port=DBport, user=DBuser, passwd=DBpasswd, db=DBdatabase)
            cursor = cnxn.cursor()
            cursor.execute("SELECT name FROM tbl_Players WHERE name = %s ;", (command, ))
            dbResponse = cursor.fetchone()

            if dbResponse != None:
                players[id]['name'] = dbResponse[0]

                # Closing DB cursor, all required data has been extracted from the database
                cursor.close()
                cnxn.close()

                log("Client ID: " + str(id) + " has requested existing user (" + command + ")", "info")
                mud.send_message(id, 'Hi <u><f32>' + command + '<r>!')
                mud.send_message(id, '<f15>What is your password?')
            else:
                mud.send_message(id, '<f202>User <f32>' + command + '<r> was not found!')
                log("Client ID: " + str(id) + " has requested non existent user (" + command + ")", "info")

        elif players[id]['name'] is not None and players[id]['authenticated'] is None:

            cnxn = pymysql.connect(host=DBhost, port=DBport, user=DBuser, passwd=DBpasswd, db=DBdatabase)
            db_cursor = cnxn.cursor()
            p = fetch_player(db_cursor, name, command)
            db_cursor.close()
            cnxn.close()

            if p:
                p['authenticated'] = True
                players[id] = p

                log("Client ID: " + str(id) + " has successfully authenticated user " + players[id]['name'], "info")

                # Debug - print data extracted from DB onto console
                #print('Loaded player ' + players[id]['name'] + 'room: ' \
                #    + players[id]['room'] + 'lvl: ' \
                #    + str(players[id]['lvl']) + 'exp: ' \
                #    + str(players[id]['exp']) + 'str: ' \
                #    + str(players[id]['str']) + 'per: ' \
                #    + str(players[id]['per']) + 'endu: ' \
                #    + str(players[id]['endu']) + 'cha: ' \
                #    + str(players[id]['cha']) + 'int: ' \
                #    + str(players[id]['int']) + 'agi: ' \
                #    + str(players[id]['agi']) + 'luc: ' \
                #    + str(players[id]['luc']) + 'cred: ' \
                #    + str(players[id]['cred']))

                # go through all the players in the game
                for (pid, pl) in players.items():
                     # send each player a message to tell them about the new player
                     # print("player pid: " + players[pid]["room"] + ", player id: " + players[id]["room"])
                    if pl['authenticated'] is not None \
                        and pl['room'] == players[id]['room'] \
                        and pl['name'] != players[id]['name']:
                        mud.send_message(pid, '{} has materialised out of thin air nearby.'.format(p['name']))

                # send the new player a welcome message
                mud.send_message(id, '<f15>Welcome to the game, {}. '.format(players[id]['name']))
                mud.send_message(id, '<f15>-------------------------------------------------')
                mud.send_message(id, "<f15>Type 'help' for a list of commands. Have fun!")

                # send the new player the description of their current room
                # print('about to send room description...')
                # print('Description: ' + rooms[players[id]['room']]['description'])
                # mud.send_message(id, rooms[players[id]['room']]['description'])
            else:
                mud.send_message(id, '<f202>Password incorrect!')
                log("Client ID: " + str(id) + " has failed authentication", "info")

        elif command.lower() == 'help':
        # 'help' command
            # send the player back the list of possible commands
            mud.send_message(id, 'Commands:')
            mud.send_message(id, '  say <message>    - Says something out loud, '  + "e.g. 'say Hello'")
            mud.send_message(id, '  look             - Examines the ' + "surroundings, e.g. 'look'")
            mud.send_message(id, '  go <exit>        - Moves through the exit ' + "specified, e.g. 'go outside'")
            mud.send_message(id, '  attack <target>  - attack target ' + "specified, e.g. 'attack cleaning bot'")
            mud.send_message(id, '  check inventory  - check the contents of ' + "your inventory")
            mud.send_message(id, '  take <item>      - pick up an item lying ' + "on the floor")
            mud.send_message(id, '  drop <item>      - drop an item from your inventory ' + "on the floor")
            mud.send_message(id, '  colortest        - showcase client`s ability to display ' + "colorful text")
            
        elif command.lower() == 'say':
        # 'say' command
            # go through every player in the game
            for (pid, pl) in players.items():
                # if they're in the same room as the player
                if pl['room'] == players[id]['room']:
                    # send them a message telling them what the player said
                    mud.send_message(pid, '<f32>{}<r> says: <f159>{}'.format(players[id]['name'], params))
        elif command.lower() == 'look':
        # 'look' command
            # store the player's current room
            rm = rooms[players[id]['room']]

            # send the player back the description of their current room
            mud.send_message(id, "<f42>" + rm['description'])

            # Get name of every player in the game
            # if they're in the same room as the player and they have a name to be shown
            playershere = (
                [p['name'] for (pid, p) in players.items() 
                 if p['room'] == players[id]['room']
                 and p['name'] is not None
                 and p['name'] != players[id]['name']
                ]
                +
                ##### Show corpses in the room
                [corpse['name'] for (corpse_id, corpse) in corpses.items()
                 if corpse['room'] == players[id]['room']
                ]
                +
                ##### Show NPCs in the room #####
                [npc['name'] for (npc_id, npc) in npcs.items()
                 if npc['room'] == players[id]['room']
                ]
            )

            itemshere = []

            ##### Show items in the room
            player_room_id = players[id]['room']
            for item_record in itemsInWorld.get(player_room_id, []):
                real_item = itemsDB[item_record['id']]
                itemshere.append(real_item['article'] + ' ' + real_item['name'])
            
            # send player a message containing the list of players in the room
            if len(playershere) > 0:
                mud.send_message(id, '<f42>You see: <f77>{}'.format(', '.join(playershere)))

            # send player a message containing the list of exits from this room
            mud.send_message(id, '<f42>Exits are: <f94>{}'.format(', '.join(rm['exits'])))

            # send player a message containing the list of items in the room
            if len(itemshere) > 0:
                mud.send_message(id, '<f42>You notice: <f222>{}'.format(', '.join(itemshere)))

        elif command.lower() == 'attack':
            # attack command
        
            isAlreadyAttacking = False
            target = params #.lower()
            targetFound = False

            for (fighter_id, fighter) in fights.items():
                if fighter['s1'] == players[id]['name']:
                    isAlreadyAttacking = True
                    currentTarget = fighter['s2']

            if isAlreadyAttacking == False:
                if players[id]['name'].lower() != target.lower():
                    for (pid, pl) in players.items():
                        if pl['name'].lower() == target.lower():
                            targetFound = True
                            victimId = pid
                            attackerId = id
                            if pl['room'] == players[id]['room']:
                                fights[len(fights)] = { 
                                  's1': players[id]['name'], 
                                  's2': target, 
                                  's1id': attackerId, 
                                  's2id': victimId, 
                                  's1type': 'pc', 
                                  's2type': 'pc', 
                                  'retaliated': 0 
                                }
                                mud.send_message(id, '<f214>Attacking <r><u><f32>' + target + '!')
                            else:
                                targetFound = False

                    # mud.send_message(id, 'You cannot see ' + target + ' anywhere nearby.|')
                    if targetFound == False:
                        for (nid, npc) in npcs.items():
                            if npc['name'].lower() == target.lower():
                                victimId = nid
                                attackerId = id
                                # print('found target npc')
                                if npc['room'] == players[id]['room'] and targetFound == False:
                                    targetFound = True
                                    # print('target found!')
                                    if players[id]['room'] == npc['room']:
                                        fights[len(fights)] = {
                                            's1': players[id]['name'], 
                                            's2': nid, 
                                            's1id': attackerId, 
                                            's2id': victimId, 
                                            's1type': 'pc', 
                                            's2type': 'npc', 
                                            'retaliated': 0
                                        }
                                        mud.send_message(id, 'Attacking <u><f21>' + npc['name'] + '<r>!')
                                    else:
                                        pass

                    if targetFound == False:
                        mud.send_message(id, 'You cannot see ' + target + ' anywhere nearby.')
                else:
                    mud.send_message(id, 'You attempt hitting yourself and realise this might not be the most productive way of using your time.')
            else:
                if type(currentTarget) is not int:
                    mud.send_message(id, 'You are already attacking ' + currentTarget)
                else:
                    mud.send_message(id, 'You are already attacking ' + npcs[currentTarget]['name'])
            # List fights for debugging purposes
            # for x in fights:
                # print (x)
                # for y in fights[x]:
                    # print (y,':',fights[x][y])

        elif command.lower() == 'go':
        # 'go' command
            # store the exit name
            ex = params.lower()

            # store the player's current room
            rm = rooms[players[id]['room']]

            # if the specified exit is found in the room's exits list
            if ex in rm['exits']:
                # go through all the players in the game
                for (pid, pl) in players.items():
                    # if player is in the same room and isn't the player
                    # sending the command
                    if pl['room'] == players[id]['room'] and pid != id:
                        # send them a message telling them that the player
                        # left the room
                        mud.send_message(pid, '<f32>{}<r> left via exit {}'.format(players[id]['name'], ex))

                # update the player's current room to the one the exit leads to
                players[id]['room'] = rm['exits'][ex]
                rm = rooms[players[id]['room']]

                # go through all the players in the game
                for (pid, pl) in players.items():
                    # if player is in the same (new) room and isn't the player
                    # sending the command
                    if pl['room'] == players[id]['room'] and pid != id:
                        # send them a message telling them that the player
                        # entered the room
                        # mud.send_message(pid, '{} arrived via exit {}|'.format(players[id]['name'], ex))
                        mud.send_message(pid, '<f32>{}<r> has arrived.'.format(players[id]['name'], ex))

                # send the player a message telling them where they are now
                #mud.send_message(id, 'You arrive at {}'.format(players[id]['room']))
                mud.send_message(id, 'You arrive at <f106>{}'.format(rooms[players[id]['room']]['name']))
            else:
            # the specified exit wasn't found in the current room
                # send back an 'unknown exit' message
                mud.send_message(id, "Unknown exit <f226>'{}''".format(ex))

        elif command.lower() == 'check':
        # 'check' command
            if params.lower() == 'inventory' or params.lower() == 'inv':
                mud.send_message(id, 'You check your inventory.')
                if len(players[id]['inv']) > 0:
                    mud.send_message(id, 'You are currently in possession of: ')
                    for i in players[id]['inv']:
                        mud.send_message(id, '<b234>' + itemsDB[int(i)]['name'])
                else:
                    mud.send_message(id, 'You haven`t got any items on you.')
            elif params.lower() == 'stats':
                mud.send_message(id, 'You check your character sheet.')
            else:
                mud.send_message(id, 'Check what?')

        # 'drop' command
        elif command.lower() == 'drop':

            itemID = None
            for (iid, item) in itemsDB.items():
                if item['name'].lower() == str(params).lower():
                    # ID of the item to be dropped
                    itemID = iid
                    break

            # Check if item is in player's inventory
            itemInInventory = False
            for item in players[id]['inv']:
                if int(item) == itemID:
                    itemInInventory = True
            
            if itemID is not None and itemInInventory:
                for i in players[id]['inv']:
                    if int(i) == itemID:
                        # Remove first matching item from inventory
                        players[id]['inv'].remove(i)
                        break

                # Create item on the floor in the same room as the player
                player_room_id = players[id]['room']
                itemsInWorld[player_room_id] = itemsInWorld.get(player_room_id, []).append({
                  'id': itemID, 
                  'room': player_room_id, 
                  'whenDropped': int(time.time()), 
                  'lifespan': 900000000, 
                  'owner': id 
                })
                
                # Print itemsInWorld to console for debugging purposes
                # for x in itemsInWorld:
                    # print (x)
                    # for y in itemsInWorld[x]:
                            # print(y,':',itemsInWorld[x][y])
                            
                mud.send_message(id, 'You drop ' + itemsDB[int(i)]['article'] + ' ' + itemsDB[int(i)]['name'] + ' on the floor.')
                
            else:
                mud.send_message(id, 'You don`t have that!')


        # take command
        elif command.lower() == 'take':

            itemPickedUp = False
            item_id = None
            player_room_id = players[id]['room']
            items_in_player_room = itemsInWorld.get(player_room_id, [])
            for item_record in items_in_player_room:
                if itemsDB[item_record['id']]['name'].lower() == str(params).lower():
                    item_id = item_record['id']
                    players[id]['inv'].append(str(item_id))
                    items_in_player_room.remove(item_record)
                    itemPickedUp = True
                    break

            if itemPickedUp:
                mud.send_message(id, 'You pick up and place ' + itemsDB[item_id]['article'] + ' ' + itemsDB[item_id]['name'] + ' in your inventory.')
            else:
                mud.send_message(id, 'You cannot see ' + str(params) + ' anywhere.')

        else:
        # some other, unrecognised command
            # send back an 'unknown command' message
            mud.send_message(id, "Unknown command '{}'".format(command))

