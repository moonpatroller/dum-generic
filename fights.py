import random

from random import randint


def pump_npcs(fights, players, npcs, mud, now, set_fights, get_players_in_room):
    # Iterate through NPCs, check if its time to talk, then check if anyone is attacking it
    for (nid, npc) in npcs.items():
        # Check if any player is in the same room, then send a random message to them
        if now > npc['timeTalked'] + npc['talkDelay']:
            for (pid, pl) in get_players_in_room(npc['room']):
                if len(npc['vocabulary']) > 1:
                    msg = '<f21><u>' + npc['name'] + '<r> says: <f86>' + random.choice(npc['vocabulary'])
                    mud.send_message(pid, msg)
                else:
                    #mud.send_message(pid, npc['vocabulary'][0])
                    msg = '<f21><u>' + npc['name'] + '<r> says: <f86>' + npc['vocabulary'][0]
                    mud.send_message(pid, msg)
            npc['timeTalked'] =  now
        # Iterate through fights and see if anyone is attacking an NPC - 
        # if so, attack him too if not in combat (TODO: and isAggressive = true)
        for fight in fights.values():
            fs1id = fight['s1id']
            fs2id = fight['s2id']
            npc2 = npcs[fs2id]

            if fs2id == nid and npc2['isInCombat'] == 1 and fight['s1type'] == 'pc' and fight['retaliated'] == 0:
                # print('player is attacking npc')
                # BETA: set las combat action to now when attacking a player
                npc2['lastCombatAction'] = now
                fight['retaliated'] = 1
                npc2['isInCombat'] = 1

                new_fights = {
                    len(fights): {
                        's1': npc2['name'],
                        's2': players[fs1id]['name'],
                        's1id': nid,
                        's2id': fs1id,
                        's1type': 'npc',
                        's2type': 'pc',
                        'retaliated': 1
                    }
                }
                set_fights({**fights, **new_fights})

            elif fs2id == nid and npc2['isInCombat'] == 1 and fight['s1type'] == 'npc' and fight['retaliated'] == 0:
                # print('npc is attacking npc')
                # BETA: set las combat action to now when attacking a player
                npc2['lastCombatAction'] = now
                fight['retaliated'] = 1
                npc2['isInCombat'] = 1

                new_fights = {
                    len(fights): {
                        's1': npc2['name'],
                        's2': players[fs1id]['name'], 
                        's1id': nid, 
                        's2id': fs1id, 
                        's1type': 'npc', 
                        's2type': 'npc', 
                        'retaliated': 1
                    }
                }
                set_fights({**fights, **new_fights})

        # Check if NPC is still alive, if not, remove from room and create a corpse, set isInCombat to 0, 
        # set whenDied to now and remove any fights NPC was involved in
        if npc['hp'] <= 0:
            npc['isInCombat'] = 0
            npc['lastRoom'] = npc['room']
            npc['whenDied'] = now
            set_fights({
                fight_id: fight for fight_id, fight in fights.items() 
                if fight['s1id'] != nid and fight['s2id'] != nid
            })

            corpses.append(create_corpse(npc))

            for (pid, pl) in get_players_in_room(npc['room']):
                if pl['authenticated'] is not None:
                    mud.send_message(pid, "<f32><u>{}<r> <f88>has been killed.".format(npc['name']))
            npc['room'] = None
            npc['hp'] = npcsTemplate[nid]['hp']


def handle_fights(fights, players, npcs, mud, now, set_fights):
    for fighter in fights.values():
        # PC -> PC
        s1id = fighter['s1id']
        s2id = fighter['s2id']
        player_1 = players[s1id]
        player_2 = players[s2id]

        if fighter['s1type'] == 'pc' and fighter['s2type'] == 'pc':
            if player_1['room'] == player_2['room']:
                if now >= player_1['lastCombatAction'] + 10 - player_1['agi']:
                    if player_2['isAttackable'] == 1:
                        player_1['isInCombat'] = 1
                        player_2['isInCombat'] = 1
                        # Do damage to the PC here
                        if randint(0, 1) == 1:
                            modifier = randint(0, 10)
                            if player_1['hp'] > 0:
                                player_2['hp'] -= player_1['str'] + modifier
                                player_1['lastCombatAction'] = now
                                mud.send_message(s1id, 'You manage to hit <f32><u>' + player_2['name'] + '<r> for <f0><b2>' + 
                                    str(player_1['str'] + modifier) + '<r> points of damage.')
                                mud.send_message(s2id, '<f32>' + player_1['name'] + '<r> has managed to hit you for <f15><b88>' + 
                                    str(player_1['str'] + modifier) + '<r> points of damage.')
                                # print('----------')
                                # print(player_1['name'] + ': ' + str(player_1['hp']))
                                # print(player_2['name'] + ': ' + str(player_2['hp']))
                        else:
                            player_1['lastCombatAction'] = now
                            mud.send_message(s1id, 'You miss trying to hit <f32><u>' + player_2['name'] + '')
                            mud.send_message(s2id, '<f32><u>' + player_1['name'] + '<r> missed while trying to hit you!')
                    else:
                        mud.send_message(s1id, '<f225>Suddnely you stop. It wouldn`t be a good idea to attack <f32>' + 
                            player_2['name'] + ' at this time.')

                        set_fights({
                            fight_id: fight for fight_id, fight in fights.items() 
                            if fight['s1id'] != s1id or fight['s2id'] != s2id
                        })

        # PC -> NPC
        elif fighter['s1type'] == 'pc' and fighter['s2type'] == 'npc':
            npc_2 = npcs[s2id]
            if player_1['room'] == npc_2['room']:
                if now >= player_1['lastCombatAction'] + 10 - player_1['agi']:
                    if npc_2['isAttackable'] == 1:
                        player_1['isInCombat'] = 1
                        npc_2['isInCombat'] = 1
                        # Do damage to the NPC here
                        if randint(0, 1) == 1:
                            modifier = randint(0, 10)
                            if player_1['hp'] > 0:
                                npc_2['hp'] -= player_1['str'] + modifier
                                player_1['lastCombatAction'] = now
                                mud.send_message(s1id, 'You manage to hit <f21><u>' + npc_2['name'] + '<r> for <b2><f0>' + 
                                    str(player_1['str'] + modifier)  + '<r> points of damage')
                                # print(npc_2['hp'])
                        else:
                            player_1['lastCombatAction'] = now
                            mud.send_message(s1id, 'You miss <u><f21>' + npc_2['name'] + '<r> completely!')
                    else:
                        mud.send_message(s1id, '<f225>Suddenly you stop. It wouldn`t be a good idea to attack <u><f21>' + 
                            npc_2['name'] + '<r> at this time.')

                        set_fights({
                            fight_id: fight for fight_id, fight in fights.items() 
                            if fight['s1id'] != s1id or fight['s2id'] != s2id
                        })

        # NPC -> PC
        elif fighter['s1type'] == 'npc' and fighter['s2type'] == 'pc':
            npc_1 = npcs[s1id]
            if npc_1['room'] == player_2['room']:
                if now >= npc_1['lastCombatAction'] + 10 - npc_1['agi']:
                    npc_1['isInCombat'] = 1
                    player_2['isInCombat'] = 1
                    # Do the damage to PC here
                    if randint(0, 1) == 1:
                        modifier = randint(0, 10)
                        if npc_1['hp'] > 0:
                            player_2['hp'] -= npc_1['str'] + modifier
                            npc_1['lastCombatAction'] = now
                            mud.send_message(s2id, '<f21><u>' + npc_1['name'] + '<r> has managed to hit you for <f15><b88>' + 
                                str(npc_1['str'] + modifier) + '<r> points of damage.')
                    else:
                        npc_1['lastCombatAction'] = now
                        mud.send_message(s2id, '<f21><u>' + npc_1['name'] + '<r> has missed you completely!')
        # NPC -> NPC
        # elif fighter['s1type'] == 'npc' and fighter['s2type'] == 'npc':
        #     test = 1
            
