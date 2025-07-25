import discord
from datetime import datetime
import requests
import random

# big brain file hosting :)
rank_assets = {
    "UNRANKED": "https://cdn.discordapp.com/attachments/989905618494181386/989936020013334628/unranked.png",
    "IRON": "https://cdn.discordapp.com/attachments/989905618494181386/989905732445036614/iron.png",
    "BRONZE": "https://cdn.discordapp.com/attachments/989905618494181386/989905730805047356/bronze.png",
    "SILVER": "https://cdn.discordapp.com/attachments/989905618494181386/989905733128687626/silver.png",
    "GOLD": "https://cdn.discordapp.com/attachments/989905618494181386/989905731933311027/gold.png",
    "PLATINUM": "https://cdn.discordapp.com/attachments/989905618494181386/989905732856053851/platinum.png",
    "DIAMOND": "https://cdn.discordapp.com/attachments/989905618494181386/989905731463577600/diamond.png",
    "EMERALD": "https://cdn.discordapp.com/attachments/989905618494181386/1132067774584324096/emerald.png",
    "MASTER": "https://cdn.discordapp.com/attachments/989905618494181386/989905732654739516/master.png",
    "GRANDMASTER": "https://cdn.discordapp.com/attachments/989905618494181386/989905732176592956/grandmaster.png",
    "CHALLENGER": "https://cdn.discordapp.com/attachments/989905618494181386/989905731186749470/challenger.png",
}

league_patch = "14.3.1"

champion_info = requests.get(
    f"https://ddragon.leagueoflegends.com/cdn/{league_patch}/data/en_US/champion.json"
).json()
champion_name = {}
for champion in champion_info["data"]:
    champion_name[int(champion_info["data"][champion]["key"])] = champion


def icon_url(icon_id):
    return f"https://ddragon.leagueoflegends.com/cdn/{league_patch}/img/profileicon/{icon_id}.png"


def generate_match_embed(game_info, puuid):
    multikill_names = ["Doublekill", "Triplekill", "Quadrakill", "Pentakill"]
    blue_kills = 0
    red_kills = 0
    max_multikill = 0
    winner = False
    top_damage = 0
    for player in game_info.participants:
        if player.puuid == puuid:
            if player.team == game_info.winner:
                winner = True
        if player.team == "Blue":
            blue_kills += player.kills
        else:
            red_kills += player.kills
        for i in range(4):
            if player.multikills[i] > 0:
                max_multikill = max(i, max_multikill)
        if player.damage > top_damage:
            top_damage = player.damage
    m, s = divmod(game_info.duration, 60)

    status = "VICTORY" if winner else "DEFEAT"
    title = (
        "REMAKE"
        if game_info.duration < 300
        else f"{status} - {game_info.winner.upper()} TEAM WINS"
    )
    description = f"Type: **{game_info.queue_type}**, Score: **{blue_kills} - {red_kills}**, Time: **{m:02d}:{s:02d}**"
    color = 0xAFAEAE if game_info.duration < 300 else 0x53A8E8 if winner else 0xDA2D43

    embed = discord.Embed(title=title, description=description, color=color)

    embed.add_field(
        name=f":blue_circle: Blue Team",
        value=f"Total Kills: **{blue_kills}**",
        inline=False,
    )
    counter = 0
    for player in game_info.participants:
        last_char = ""
        if player.puuid == puuid:
            last_char = ":green_heart:"
        multikill = ""
        count = player.multikills[max_multikill]
        if count > 0:
            multikill = f"{multikill_names[max_multikill]} {'x' if count > 1 else ''}{count if count > 1 else ''}{':exclamation:' if max_multikill >= 2 else ''}"
        star = "\u2605" if player.damage == top_damage else ""
        embed.add_field(
            name=f"{player.name} - {repair_champ_name(player.champion_name)} {player.kills}/{player.deaths}/{player.assists} {last_char} {multikill}",
            value=f"KDA: **{player.kda()}**, CS: **{player.creep_score}** ({round(float(player.creep_score)/(float(game_info.duration)/60.0), 2)}), {star}DMG: **{player.damage}**, GOLD: **{player.gold}**",
            inline=False,
        )
        counter += 1
        if counter == 5:
            embed.add_field(
                name=f":red_circle: Red Team",
                value=f"Total Kills: **{red_kills}**",
                inline=False,
            )

    embed.timestamp = datetime.fromtimestamp(
        int(game_info.start_time / 1000) - 2 * 3600
    )
    return embed


def generate_user_embed(user_info):
    embed = discord.Embed(
        title=f"{user_info.level} level",
        description=f"",
        color=random.randint(0, 16777215),
    )
    embed.set_author(name=user_info.name, icon_url=icon_url(user_info.icon))
    embed.set_thumbnail(url=rank_assets[user_info.max_division.upper()])
    embed.add_field(
        name=f"Solo/Duo - {user_info.rank_solo}",
        value=f"{str(user_info.lp_solo) + ' LP, ' if user_info.rank_solo != 'UNRANKED' else ''}{user_info.wins_solo + user_info.losses_solo} games{f', {round(user_info.wins_solo/(user_info.losses_solo + user_info.wins_solo) * 100, 2)}% WR' if (user_info.losses_solo + user_info.wins_solo) > 0 else ''}",
    )
    embed.add_field(
        name=f"Flex - {user_info.rank_flex}",
        value=f"{str(user_info.lp_flex) + ' LP, ' if user_info.rank_flex != 'UNRANKED' else ''}{user_info.wins_flex + user_info.losses_flex} games{f', {round(user_info.wins_flex/(user_info.losses_flex + user_info.wins_flex) * 100, 2)}% WR' if (user_info.losses_flex + user_info.wins_flex) > 0 else ''}",
    )
    embed.add_field(
        name=f"Total Mastery: {user_info.total_mastery}",
        value=f" Total Points: {user_info.total_points:,}",
        inline=False,
    )
    for champion in user_info.top_champs[:3]:
        name = f"ID: {champion[0]}"
        if champion[0] in champion_name:
            name = repair_champ_name(champion_name[champion[0]])
        embed.add_field(
            name=f"{name} ({champion[1]} lvl)", value=f"{champion[2]:,} pts."
        )

    return embed


def generate_history_embed(match_history, nametag):
    embed = discord.Embed(
        title=f"Last {len(match_history[0])} Games",
        description=f"",
        color=random.randint(0, 16777215),
    )
    embed.set_author(
        name=f"{nametag} ({match_history[1]['summonerLevel']} lvl)",
        icon_url=icon_url(match_history[1]["profileIconId"]),
    )
    for i in range(len(match_history[0])):
        match = match_history[0][i]
        for participant in match.participants:
            if participant.puuid == match_history[1]["puuid"]:
                m, s = divmod(match.duration, 60)
                result_emoji = (
                    ":white_circle:"
                    if match.duration < 300
                    else (
                        ":blue_circle:"
                        if match.winner == participant.team
                        else ":red_circle:"
                    )
                )
                embed.add_field(
                    name=f"{result_emoji} {i+1} - {match.queue_type} - {repair_champ_name(participant.champion_name)} {participant.kills}/{participant.deaths}/{participant.assists} - {m:02d}:{s:02d}",
                    value=f"KDA: **{participant.kda()}**, CS: **{participant.creep_score}** ({round(float(participant.creep_score)/(float(match.duration)/60.0), 2)}), DMG: **{participant.damage}**, GOLD: **{participant.gold}**",
                    inline=False,
                )
    return embed


def generate_help_embed(server_names, default_server):
    embed = discord.Embed(
        title=f"Help",
        description=f"",
        color=random.randint(0, 16777215),
    )
    help_data = [
        {"name": "Commands", "value": ""},
        {
            "name": "/profile {name} {tag} {server?}",
            "value": "See your rank, mastery and favourite champs",
        },
        {
            "name": "/match {name} {tag} {id?} {server?}",
            "value": "Inspect game from your history, default last game. Your can use /history to get game id.",
        },
        {
            "name": "/history {name} {tag} {count?} {server?}",
            "value": "Check last 1-20 games of a player, default 5",
        },
        {"name": "", "value": ""},
        {
            "name": f"Avaiable game servers (default is {default_server})",
            "value": ", ".join(server_names.keys()),
        },
        {"name": "Github", "value": "https://github.com/Nasus20202/lolBot"},
    ]
    for data in help_data:
        embed.add_field(name=data["name"], value=data["value"], inline=False)
    return embed


def repair_champ_name(champ_name):
    new_champ_name = ""
    for i in champ_name:
        if i <= "Z" and new_champ_name != "":
            new_champ_name += " " + i
        else:
            new_champ_name += i
    return new_champ_name
