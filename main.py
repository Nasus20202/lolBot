from tokenize import Number
import discord
from dotenv import load_dotenv
import os
from discord.ext import commands
from game_info import GameInfo, PlayerInfo
import riot_api
from datetime import datetime


def main():
    load_dotenv()
    intents = discord.Intents.default()
    intents.members = True
    intents.presences = True
    intents.guilds = True
    intents.messages = True

    bot = commands.Bot(command_prefix='!', intents=intents)
    riot_client = riot_api.RiotAPI(os.getenv('RIOT_TOKEN'))

    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user} (ID: {bot.user.id})')
        await bot.change_presence(status=discord.Status.online, activity=discord.Game("League of Legends"))

    @bot.command()
    async def level(ctx, *, arg):
        summoner = riot_client.get_summoner_by_name(arg)
        if(summoner["status_code"] == 200):
            await ctx.send(f'{summoner["name"]} is level {summoner["summonerLevel"]}')
        else:
            await ctx.send(f'{summoner["message"]}')

    @bot.command()
    async def last(ctx, *, arg):
        summoner = riot_client.get_summoner_by_name(arg)
        if(summoner["status_code"] != 200):
            await ctx.send(f"Summoner {arg} doesn't exist!")
            return
        match_info = riot_client.get_recent_match_info(summoner["name"])
        if(match_info == None):
            await ctx.send(f"Match not found!")
            return
        embed = generate_embed(match_info, summoner["name"])
        await ctx.send(embed=embed)

    @bot.command()
    async def match(ctx, *, arg):
        id = arg.split(" ")[-1]
        isNumber = True
        for c in id:
            if(c < "0" or c > "9"):
                isNumber = False
        if(not isNumber):
            id = 1
        summoner_name = ""
        for i in arg.split(" ")[:-1]:
            summoner_name += i
        if(not isNumber):
            summoner_name = arg
        summoner = riot_client.get_summoner_by_name(summoner_name)
        if(summoner["status_code"] != 200):
            await ctx.send(f"Summoner {arg} doesn't exist!")
            return
        if(int(id) > 100 or int(id) < 1):
            await ctx.send(f"You can only see your last 100 matches!")
            return
        match_info = riot_client.get_recent_match_info(summoner["name"], int(id)-1)
        if(match_info == None):
            await ctx.send(f"Match not found!")
            return
        embed = generate_embed(match_info, summoner["name"])
        await ctx.send(embed=embed)

    def repair_champ_name(champ_name):
        new_champ_name = ""
        for i in champ_name:
            if i <= 'Z' and new_champ_name != "":
                new_champ_name += " " + i
            else:
                new_champ_name += i
        return new_champ_name

    def generate_embed(game_info, username):
        blue_kills = 0
        red_kills = 0
        winner = False
        for player in game_info.participants:
            if player.summoner_name == username:
                if player.team == game_info.winner:
                    winner = True
            if player.team == "Blue":
                blue_kills += player.kills
            else:
                red_kills += player.kills
        m, s = divmod(game_info.duration, 60)
        status = "VICTORY" if winner else "DEFEAT"
        embed = discord.Embed(title=f"{status} - {game_info.winner.upper()} TEAM WINS", description=f"Type: **{game_info.queue_type}**, Score: **{blue_kills} - {red_kills}**, Time: **{m:02d}:{s:02d}**", color=0x53a8e8 if winner else 0xda2d43)
        x = 0
        embed.add_field(name=f":blue_circle: Blue Team", value=f"Total Kills: **{blue_kills}**", inline=False)
        for player in game_info.participants:
            last_char = ""
            if(player.summoner_name == username):
                last_char = ':green_heart:'
            embed.add_field(name=f"{player.summoner_name} - {repair_champ_name(player.champion_name)} {player.kills}/{player.deaths}/{player.assists} {last_char} ", value=f"KDA: **{player.kda()}**, CS: **{player.creep_score}** ({round(float(player.creep_score)/(float(game_info.duration)/60.0), 2)} cs/min), GOLD: **{player.gold}**", inline=False)
            x += 1
            if x == 5:
                embed.add_field(name=f":red_circle: Red Team", value=f"Total Kills: **{red_kills}**", inline=False)
                
        embed.timestamp = datetime.fromtimestamp(int(game_info.start_time/1000)-2*3600)
        return embed
        


    bot.run(os.environ.get('DISCORD_TOKEN'))

if __name__ == "__main__":
    main()

