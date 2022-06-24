import discord
from datetime import datetime

async def generate_match_embed(game_info, username):
        multikill_names=["Doublekill x", "Tripplekill x", "Quadrakill x", "Pentakill x"]
        blue_kills = 0
        red_kills = 0
        max_multikill = 0
        winner = False
        for player in game_info.participants:
            if player.summoner_name == username:
                if player.team == game_info.winner:
                    winner = True
            if player.team == "Blue":
                blue_kills += player.kills
            else:
                red_kills += player.kills
            for i in range(4):
                if(player.multikills[i] > 0):
                    max_multikill = max(i, max_multikill)
        m, s = divmod(game_info.duration, 60)
        status = "VICTORY" if winner else "DEFEAT"
        embed = discord.Embed(title=f"{status} - {game_info.winner.upper()} TEAM WINS", description=f"Type: **{game_info.queue_type}**, Score: **{blue_kills} - {red_kills}**, Time: **{m:02d}:{s:02d}**", color=0x53a8e8 if winner else 0xda2d43)
        x = 0
        embed.add_field(name=f":blue_circle: Blue Team", value=f"Total Kills: **{blue_kills}**", inline=False)
        for player in game_info.participants:
            last_char = ""
            if(player.summoner_name == username):
                last_char = ':green_heart:'
            multikill = ""
            count = player.multikills[max_multikill]
            if(count > 0):
                multikill = f"{multikill_names[max_multikill]}{count}"
            embed.add_field(name=f"{player.summoner_name} - {await repair_champ_name(player.champion_name)} {player.kills}/{player.deaths}/{player.assists} {last_char} {multikill}", value=f"KDA: **{player.kda()}**, CS: **{player.creep_score}** ({round(float(player.creep_score)/(float(game_info.duration)/60.0), 2)} cs/min), GOLD: **{player.gold}**", inline=False)
            x += 1
            if x == 5:
                embed.add_field(name=f":red_circle: Red Team", value=f"Total Kills: **{red_kills}**", inline=False)
                
        embed.timestamp = datetime.fromtimestamp(int(game_info.start_time/1000)-2*3600)
        return embed
    
async def repair_champ_name(champ_name):
    new_champ_name = ""
    for i in champ_name:
        if i <= 'Z' and new_champ_name != "":
            new_champ_name += " " + i
        else:
            new_champ_name += i
    return new_champ_name