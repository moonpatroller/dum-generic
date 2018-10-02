#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import random
import time

from copy import deepcopy

from cmsg import cmsg
from fights import handle_fights, pump_npcs
from functions import log
from mudserver import MudServer
from DB import DB


def respawn_npcs(npcs, npcsTemplate):
    # Handle NPC respawns
    for (nid, npc) in npcs.items():
        if npc['whenDied'] is not None and now >= npc['whenDied'] + npc['respawn']:
            npc['whenDied'] = None
            npc['room'] = npcsTemplate[nid]['room']

def pump_env_messages(env, players, mud, now):
    # Iterate through ENV elements and see if it's time to send a message to players in the same room as the ENV elements
    for e in env.values():
        if now > e['timeTalked'] + e['talkDelay']:
            for (pid, pl) in players.items():
                if e['room'] == pl['room']:
                    if len(e['vocabulary']) > 1:
                        msg = '<f58>[' + e['name'] + ']: <f236>' + random.choice(e['vocabulary'])
                        mud.send_message(pid, msg)
                    else:
                        msg = '<f58>[' + e['name'] + ']: <f236>' + e['vocabulary'][0]
                        mud.send_message(pid, msg)
            e['timeTalked'] = now


def create_corpse(body):
    return { 
        'room': body['room'], 
        'name': str(body['name'] + '`s corpse'), 
        'inv' : body['inv'], 
        'died': int(time.time()), 
        'TTL' : body['corpseTTL'], 
        'owner': 1
    }


def get_players_in_room(room_id):
    return ((pid, pl) for (pid, pl) in players.items() if pl['room'] != room_id)


def get_npcs_in_room(room_id):
    return ((npc_id, npc) for (npc_id, npc) in npcs.items() if npc['room'] != room_id)


def set_fights(fs):
    global fights
    fights = fs


log("", "Server Boot")


# Load rooms
with open("rooms.json", "r") as read_file:
    rooms = json.load(read_file)
    for r in rooms.values():
        r['items'] = []

log("Rooms loaded: " + str(len(rooms)), "info")


corpses = {}
fights = {}
players = {}

# Declare number of seconds to elapse between State Saves
# A State Save takes values held in memory and updates the database
# at set intervals to achieve player state persistence
stateSaveInterval = 10
lastStateSave = int(time.time())
log('State save interval: {0}, last stats save is now: {1}.'.format(stateSaveInterval, lastStateSave), "info")

db = DB('sample.db')

npcs = db.fetch_npcs()
log('Npcs loaded: {0}'.format(len(npcs)), "info")

# Save npcs as a master template
npcsTemplate = deepcopy(npcs)

env = db.fetch_env_vars()
log('Environment actors loaded: {0}'.format(env), "info")

itemsDB = db.fetch_all_items()
log('Items loaded: {0}'.format(itemsDB), "info")
log('Rooms loaded: {0}'.format(rooms), "info")

# Put some items in the world for testing and debugging
rooms['$rid=1$']['items'].append(itemsDB[200001])
rooms['$rid=1$']['items'].append(itemsDB[200002])
rooms['$rid=1$']['items'].append(itemsDB[200001])


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
        db.save_players(players)
        lastStateSave = now

    # Handle Player Deaths
    for (pid, pl) in players.items():
        if pl['authenticated']:
            if pl.get('hp', 0) <= 0:
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

                for (pid2, pl_2) in get_players_in_room(pl['lastRoom']):
                    if pl_2['authenticated'] is not None and pl_2['name'] != pl['name']:
                        mud.send_message(pid2, '<u><f32>{}<r> <f124>has been killed.'.format(pl['name']))
                pl['lastRoom'] = None
                mud.send_message(pid, '<b88><f158>Oh dear! You have died!')
                pl['hp'] = 4

    # Handle Fights
    handle_fights(fights, players, npcs, mud, now, set_fights)

    pump_npcs(fights, players, npcs, mud, now, set_fights, get_players_in_room)

    pump_env_messages(env, players, mud, now)

    # Keep corpses not older than their TTL
    corpses = {
        id: corpse for id, corpse in corpses.items() 
        if now < corpse['died'] + corpse['TTL']
    }

    respawn_npcs(npcs, npcsTemplate)

    # go through any newly connected players
    for id in mud.get_new_players():
        # add the new player to the dictionary, noting that they've not been named yet.
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
            'hp': 100,
            'charge': None,
            'isInCombat': None,
            'lastCombatAction': None,
            'isAttackable': None,
            'lastRoom': None,
            'corpseTTL': None,
        }

        # send the new player a prompt for their name
        # mud.send_message(id, 'Connected to server!')
        mud.send_message(id, 
            ("<f250><b25> ______            _______ \n\r"
             "<f250><b25>(  __  \\ |\\     /|(       )\n\r"
             "<f250><b25>| (  \\  )| )   ( || () () |\n\r"
             "<f250><b25>| |   ) || |   | || || || |\n\r"
             "<f250><b25>| |   | || |   | || |(_)| |\n\r"
             "<f250><b25>| |   ) || |   | || |   | |\n\r"
             "<f250><b25>| (__/  )| (___) || )   ( |\n\r"
             "<f250><b25>(______/ (_______)|/     \\|\n\r"
             " \n\r"
             "<f250><b25> a modern MU* engine      \n\r"
             "<f15><b25>    dumengine.wikidot.com  \n\r"
             " \n\r"
             "<f250><b25> Development Server 1       \n\r"
             " \n\r"
             '<f15>What is your username?\n\r')
        )

        log("Client ID: " + str(id) + " has connected", "info")

    # go through any recently disconnected players
    for id in mud.get_disconnected_players():

        # if for any reason the player isn't in the player map, skip them and
        # move on to the next one
        if id not in players:
            continue
        
        log("Client ID:" + str(id) + " has disconnected (" + str(players[id]['name']) + ")", "info")
        
        # go through all the players in the game
        for (pid, pl) in get_players_in_room(players[id]['room']):
            # send each player a message to tell them about the diconnected
            # player if they are in the same room
            if (players[pi]['authenticated'] is not None 
                     and pl['authenticated'] is not None
                     and pl['name'] != players[id]['name']):
                mud.send_message(pid, "<f32><u>{}<r>'s body has vanished.".format(players[id]['name']))

        # Code here to save player to the database after he's disconnected and before removing him from players dictionary
        if players[id]['authenticated'] is not None:
            log("Player disconnected, saving state", "info")
            db.save_player(players[id])

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

        current_player = players[id]
        player_room_id = current_player['room']
        # if the player hasn't given their name yet, use this first command as
        # their name and move them to the starting room.
        if current_player['name'] is None:
            current_player['name'] = command

            log('trying to fetch {0}'.format(command), 'info')
            row = db.fetch_player(command)
            log('result {0}'.format(row), 'info')

            if row is not None:

                log("Client ID: " + str(id) + " has requested existing user (" + command + ")", "info")
                mud.send_message(id, 'Hi <u><f32>' + command + '<r>!')
                mud.send_message(id, '<f15>What is your password?')
            else:
                mud.send_message(id, '<f202>User <f32>' + command + '<r> was not found!')
                log("Client ID: " + str(id) + " has requested non existent user (" + command + ")", "info")

        elif current_player['name'] is not None and current_player['authenticated'] is None:

            log('fetching player by name and password {0} {1}'.format(current_player['name'], command), 'info')
            fetched_player = db.fetch_player_by_name_and_password(current_player['name'], command)
            log('got player {0}'.format(fetched_player), 'info')

            if not fetched_player:
                log('saving player password {0} {1}'.format(current_player['name'], command), 'info')
                current_player['pwd'] = command
                count = db.save_player(current_player)
                log('saved player, updated rows = {0}'.format(count), 'info')
    
            current_player['authenticated'] = True
            current_player['room'] = '$rid=0$'
            log('current_player {0}'.format(current_player), 'info')
            players[id] = current_player
            log('players {0}'.format(players), 'info')

            log("Client ID: " + str(id) + " has successfully authenticated user " + current_player['name'], "info")

            # go through all the players in the game
            for (pid, pl) in get_players_in_room(current_player['room']):
                 # send each player a message to tell them about the new player
                 # print("player pid: " + players[pid]["room"] + ", player id: " + players[id]["room"])
                if pl['authenticated'] is not None and pl['name'] != current_player['name']:
                    mud.send_message(pid, '{} has materialised out of thin air nearby.'.format(p['name']))

            # send the new player a welcome message
            mud.send_message(id, '<f15>Welcome to the game, {}. '.format(current_player['name']))
            mud.send_message(id, 
                ('<f15>-------------------------------------------------\n\r'
                 "<f15>Type 'help' for a list of commands. Have fun!")
            )

        elif command.lower() == 'help':
        # 'help' command
            # send the player back the list of possible commands
            mud.send_message(id, 
                ('Commands:\n\r'
                 '  say <message>    - Says something out loud, '  + "e.g. 'say Hello'\n\r"
                 '  look             - Examines the ' + "surroundings, e.g. 'look'\n\r"
                 '  go <exit>        - Moves through the exit ' + "specified, e.g. 'go outside'\n\r"
                 '  attack <target>  - attack target ' + "specified, e.g. 'attack cleaning bot'\n\r"
                 '  check inventory  - check the contents of your inventory\n\r'
                 '  take <item>      - pick up an item lying on the floor\n\r'
                 '  drop <item>      - drop an item from your inventory on the floor\n\r'
                 '  colortest        - showcase client`s ability to display colorful text\n\r')
            )
            
        elif command.lower() == 'say':
        # 'say' command
            # go through every player in the game
            for (pid, pl) in get_players_in_room(player_room_id):
                # send them a message telling them what the player said
                mud.send_message(pid, '<f32>{}<r> says: <f159>{}'.format(current_player['name'], params))
        elif command.lower() == 'look':
        # 'look' command
            # store the player's current room
            rm = rooms[player_room_id]

            # send the player back the description of their current room
            mud.send_message(id, "<f42>" + rm['description'])

            # Get name of every player in the game
            # if they're in the same room as the player and they have a name to be shown

            playershere = (
                [p['name'] for (pid, p) in get_players_in_room(player_room_id) 
                 if p['name'] is not None
                 and p['name'] != current_player['name']
                ]
                +
                ##### Show corpses in the room
                [corpse['name'] for (corpse_id, corpse) in corpses.items()
                 if corpse['room'] == player_room_id
                ]
                +
                ##### Show NPCs in the room #####
                [npc['name'] for (npc_id, npc) in get_npcs_in_room(player_room_id)]
            )

            itemshere = []

            ##### Show items in the room
            for item in rm['items']:
                itemshere.append(item['article'] + ' ' + item['name'])
            
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
                if fighter['s1'] == current_player['name']:
                    isAlreadyAttacking = True
                    currentTarget = fighter['s2']

            if not isAlreadyAttacking:
                if current_player['name'].lower() != target.lower():
                    for (pid, pl) in players.items():
                        if pl['name'].lower() == target.lower():
                            targetFound = True
                            victimId = pid
                            attackerId = id
                            if pl['room'] == player_room_id:
                                fights[len(fights)] = { 
                                  's1': current_player['name'], 
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
                    if not targetFound:
                        for (nid, npc) in get_npcs_in_room(player_room_id):
                            if npc['name'].lower() == target.lower():
                                victimId = nid
                                attackerId = id
                                # print('found target npc')
                                if not targetFound:
                                    targetFound = True
                                    # print('target found!')
                                    fights[len(fights)] = {
                                        's1': current_player['name'], 
                                        's2': nid, 
                                        's1id': attackerId, 
                                        's2id': victimId, 
                                        's1type': 'pc', 
                                        's2type': 'npc', 
                                        'retaliated': 0
                                    }
                                    mud.send_message(id, 'Attacking <u><f21>' + npc['name'] + '<r>!')

                    if not targetFound:
                        mud.send_message(id, 'You cannot see ' + target + ' anywhere nearby.')
                else:
                    mud.send_message(id, 
                        'You attempt hitting yourself and realise this might not be the most productive way of using your time.')
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
            rm = rooms[player_room_id]

            # if the specified exit is found in the room's exits list
            if ex in rm['exits']:
                # go through all the players in the game
                for (pid, pl) in get_players_in_room(player_room_id):
                    # if player is in the same room and isn't the player
                    # sending the command
                    if pid != id:
                        # send them a message telling them that the player
                        # left the room
                        mud.send_message(pid, '<f32>{}<r> left via exit {}'.format(current_player['name'], ex))

                # update the player's current room to the one the exit leads to
                current_player['room'] = rm['exits'][ex]
                player_room_id = current_player['room']
                rm = rooms[player_room_id]

                # go through all the players in the game
                for (pid, pl) in get_players_in_room(player_room_id):
                    # if player is in the same (new) room and isn't the player
                    # sending the command
                    if pid != id:
                        # send them a message telling them that the player
                        # entered the room
                        # mud.send_message(pid, '{} arrived via exit {}|'.format(players[id]['name'], ex))
                        mud.send_message(pid, '<f32>{}<r> has arrived.'.format(current_player['name'], ex))

                # send the player a message telling them where they are now
                #mud.send_message(id, 'You arrive at {}'.format(players[id]['room']))
                mud.send_message(id, 'You arrive at <f106>{}'.format(rooms[player_room_id]['name']))
            else:
            # the specified exit wasn't found in the current room
                # send back an 'unknown exit' message
                mud.send_message(id, "Unknown exit <f226>'{}''".format(ex))

        elif command.lower() == 'check':
        # 'check' command
            if params.lower() == 'inventory' or params.lower() == 'inv':
                mud.send_message(id, 'You check your inventory.')
                if len(current_player['inv']) > 0:
                    mud.send_message(id, 'You are currently in possession of: ')
                    for item in current_player['inv']:
                        mud.send_message(id, '<b234>' + item['name'])
                else:
                    mud.send_message(id, 'You haven`t got any items on you.')
            elif params.lower() == 'stats':
                mud.send_message(id, 'You check your character sheet.')
            else:
                mud.send_message(id, 'Check what?')

        # 'drop' command
        elif command.lower() == 'drop':

            for item in current_player['inv']:
                if item['id'].lower() == str(params).lower():
                    current_player['inv'].remove(item)
                    rooms[player_room_id]['items'].append(item)
                    mud.send_message(id, 'You drop ' + item['article'] + ' ' + item['name'] + ' on the floor.')
                    break
            else:
                mud.send_message(id, 'You don`t have that!')


        # take command
        elif command.lower() == 'take':

            for item in rooms[player_room_id]['items']:
                if item['name'].lower() == str(params).lower():
                    rooms[player_room_id]['items'].remove(item)
                    current_player['inv'].append(item)
                    mud.send_message(id, 'You pick up and place ' + item['article'] + 
                        ' ' + item['name'] + ' in your inventory.')
                    break
            else:
                mud.send_message(id, 'You cannot see ' + str(params) + ' anywhere.')

        else:
            # some other, unrecognised command
            # send back an 'unknown command' message
            mud.send_message(id, "Unknown command '{}'".format(command))

