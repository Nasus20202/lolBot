import discord
from dotenv import load_dotenv
import os
from discord.ext import commands
from game_info import GameInfo, PlayerInfo
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

    @bot.command()
    async def summoner(ctx, *, arg):
        summoner = riot_client.get_summoner_by_name(arg)
        if(summoner["status_code"] == 200):
            await ctx.send(f'{summoner["name"]} is level {summoner["summonerLevel"]}')
        else:
            await ctx.send(f'{summoner["message"]}')

    bot.run(os.environ.get('DISCORD_TOKEN'))

if __name__ == "__main__":
    main()

