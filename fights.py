from random import randint


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
            
