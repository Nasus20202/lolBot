import datetime
import discord
from dotenv import load_dotenv
import os
from discord.ext import commands
import embed_generator
import riot_api


def main():
    load_dotenv()
    intents = discord.Intents.all()
    intents.members = True
    intents.presences = True
    intents.guilds = True
    intents.messages = True

    # Riot API constants
    server = "eun1"
    region = "europe"
    defaultTagline = "EUNE"

    bot = commands.Bot(command_prefix='!', intents=intents)
    riot_client = riot_api.RiotAPI(os.getenv('RIOT_TOKEN'), server, region)

    @bot.event
    async def on_ready():
        log(f'Logged in as {bot.user} (ID: {bot.user.id})')
        await bot.change_presence(status=discord.Status.online, activity=discord.Game("League of Legends"))

    @bot.command()
    async def level(ctx, *, arg):
        log_command(ctx, arg)

        gameName, tagLine = split_gametag(arg)
        if(gameName is None or tagLine is None):
            await ctx.send(invalid_riot_id())
            return

        puuid = await riot_client.get_riot_account_puuid(gameName, tagLine)
        if(puuid is None):
            await ctx.send(riot_account_not_found(gameName, tagLine))
            return
        
        summoner = await riot_client.get_summoner_by_puuid(puuid)
        if(summoner["status_code"] == 200):
            await ctx.send(f'{summoner["name"]} is level {summoner["summonerLevel"]}')
        else:
            await ctx.send(summoner_not_found(gameName, tagLine))

    @bot.command(aliases=['last', 'm', 'l'])
    async def match(ctx, *, arg):
        log_command(ctx, arg)

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
        
        gameName, tagLine = split_gametag(summoner_name)
        puuid = await riot_client.get_riot_account_puuid(gameName, tagLine)
        if(puuid is None):
            await ctx.send(riot_account_not_found(gameName, tagLine))
            return
        
        summoner = await riot_client.get_summoner_by_puuid(puuid)
        if(summoner["status_code"] != 200):
            await ctx.send(summoner_not_found(gameName, tagLine))
            return

        if(int(id) > 100 or int(id) < 1):
            await ctx.send(f"You can only see your last 100 matches!")
            return
        match_info = await riot_client.get_recent_match_info(puuid, int(id)-1)
        if(match_info is None):
            await ctx.send(f"Match not found!")
            return
        embed = await embed_generator.generate_match_embed(match_info, summoner["name"])
        await ctx.send(embed=embed)

    @bot.command(aliases=['player', 'rank', 'user', 'p', 'r', 'u'])
    async def profile(ctx, *, arg):
        log_command(ctx, arg)

        gameName, tagLine = split_gametag(arg)
        if(gameName is None or tagLine is None):
            await ctx.send(invalid_riot_id())
            return
        puuid = await riot_client.get_riot_account_puuid(gameName, tagLine)
        if(puuid is None):
            await ctx.send(riot_account_not_found(gameName, tagLine))
            return

        data = await riot_client.get_profile_info(puuid)
        if(data["status_code"] != 200):
            await ctx.send(summoner_not_found(gameName, tagLine))
            return
        user = data["user"]
        embed = await embed_generator.generate_user_embed(user)
        await ctx.send(embed=embed)

    @bot.command(aliases=['matches', 'h'])
    async def history(ctx, *, arg):
        log_command(ctx, arg)

        count = arg.split(" ")[-1]
        isNumber = True
        for c in count:
            if(c < "0" or c > "9"):
                isNumber = False
        if(not isNumber or int(count) <= 0 or int(count) > 20):
            count = 5
            summoner_name = arg
        else:
            summoner_name = ""
            for i in arg.split(" ")[:-1]:
                summoner_name += i

        gameName, tagLine = split_gametag(summoner_name)
        puuid = await riot_client.get_riot_account_puuid(gameName, tagLine)
        if(puuid is None):
            await ctx.send(riot_account_not_found(gameName, tagLine))
            return
        
        data = await riot_client.get_recent_matches_infos(puuid, int(count))
        if (len(data[0]) <= 0):
            await ctx.send(f"Summoner {gameName}#{tagLine} doesn't exist, you can only see your last 20 games")
            return
        embed = await embed_generator.generate_history_embed(data)
        await ctx.send(embed=embed)

    def log_command(ctx, arg):
        log(f'Command: [{ctx.command} {arg}] from [{ctx.author}] in [{ctx.guild}]')

    def log(message, level="INFO"):
        timestamp = datetime.datetime.now()
        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        print(f'[{timestamp_str}\t{level}] {message}')

    def split_gametag(gametag):
        hashtags = gametag.count("#")
        if(gametag.count("#") > 1):
            return None, None
        if(hashtags == 0):
            return gametag, defaultTagline
        parts = gametag.split("#")
        return parts[0], parts[1]
    
    def invalid_riot_id():
        return f'Invalid Riot ID! (ex: username#tagline)'
    
    def riot_account_not_found(gameName, tagLine):
        return f'Riot Account {gameName}#{tagLine} doesn\'t exsit!'
    
    def summoner_not_found(gameName, tagLine):
        return f'Summoner {gameName}#{tagLine} doesn\'t exsit!'

    bot.run(os.environ.get('DISCORD_TOKEN'))
    

if __name__ == "__main__":
    main()

