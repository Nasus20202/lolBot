import discord
from dotenv import load_dotenv
import os
from discord.ext import commands
import embed_generator
import riot_api


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
        summoner = await riot_client.get_summoner_by_name(arg)
        if(summoner["status_code"] == 200):
            await ctx.send(f'{summoner["name"]} is level {summoner["summonerLevel"]}')
        else:
            await ctx.send(f'Summoner {arg} doesn\'t exsit!')

    @bot.command()
    async def last(ctx, *, arg):
        summoner = await riot_client.get_summoner_by_name(arg)
        if(summoner["status_code"] != 200):
            await ctx.send(f"Summoner {arg} doesn't exist!")
            return
        match_info = await riot_client.get_recent_match_info(summoner["name"])
        if(match_info == None):
            await ctx.send(f"Match not found!")
            return
        embed = await embed_generator.generate_match_embed(match_info, summoner["name"])
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
        summoner = await riot_client.get_summoner_by_name(summoner_name)
        if(summoner["status_code"] != 200):
            await ctx.send(f"Summoner {arg} doesn't exist!")
            return
        if(int(id) > 100 or int(id) < 1):
            await ctx.send(f"You can only see your last 100 matches!")
            return
        match_info = await riot_client.get_recent_match_info(summoner["name"], int(id)-1)
        if(match_info == None):
            await ctx.send(f"Match not found!")
            return
        embed = await embed_generator.generate_match_embed(match_info, summoner["name"])
        await ctx.send(embed=embed)



    bot.run(os.environ.get('DISCORD_TOKEN'))

if __name__ == "__main__":
    main()

