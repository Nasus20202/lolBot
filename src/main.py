import datetime
import discord
from dotenv import load_dotenv
import os
import embed_generator
import riot_api


def main():
    load_dotenv()
    intents = discord.Intents.default()

    # Riot API constants
    region = os.getenv("REGION", "europe")
    default_server = os.getenv("DEFAULT_SERVER", "EUNE")

    bot = discord.Client(intents=intents)
    command_tree = discord.app_commands.CommandTree(client=bot)
    riot_client = riot_api.RiotAPI(os.getenv("RIOT_TOKEN"), region)

    @bot.event
    async def on_ready():
        #await command_tree.sync()
        log(f"Logged in as {bot.user} (ID: {bot.user.id})")
        await bot.change_presence(
            status=discord.Status.online,
            activity=discord.CustomActivity(name="Check /help for more info"),
        )

    @command_tree.command(name="match", description="Shows n-th last match of a player")
    async def match(
        interaction: discord.Interaction,
        name: str,
        tag: str,
        id: int = 1,
        server: str = default_server,
    ):
        log_command(interaction)

        server_code = get_server_code(server)
        if server_code is None:
            await interaction.response.send_message(invalid_server(server))
            return

        puuid = await riot_client.get_riot_account_puuid(name, tag)
        if puuid is None:
            await interaction.response.send_message(riot_account_not_found(name, tag))
            return

        summoner = await riot_client.get_summoner_by_puuid(puuid, server_code)
        if summoner["status_code"] != 200:
            await interaction.response.send_message(
                summoner_not_found(name, tag, server.upper())
            )
            return

        if int(id) > 100 or int(id) < 1:
            await interaction.response.send_message(
                f"You can only see your last 100 matches!"
            )
            return
        match_info = await riot_client.get_recent_match_info(
            puuid, server_code, int(id) - 1
        )
        if match_info is None:
            await interaction.response.send_message(f"Match not found!")
            return
        embed = embed_generator.generate_match_embed(match_info, summoner["name"])
        await interaction.response.send_message(embed=embed)

    @command_tree.command(name="profile", description="Shows profile of a player")
    async def profile(
        interaction: discord.Interaction, name: str, tag: str, server: str = "EUNE"
    ):
        log_command(interaction)

        server_code = get_server_code(server)
        if server_code is None:
            await interaction.response.send_message(invalid_server(server))
            return

        puuid = await riot_client.get_riot_account_puuid(name, tag)
        if puuid is None:
            await interaction.response.send_message(riot_account_not_found(name, tag))
            return

        data = await riot_client.get_profile_info(puuid, server_code)
        if data["status_code"] != 200:
            await interaction.response.send_message(
                summoner_not_found(name, tag, server.upper())
            )
            return
        user = data["user"]
        embed = embed_generator.generate_user_embed(user)
        await interaction.response.send_message(embed=embed)

    @command_tree.command(
        name="history", description="Shows last n matches of a player"
    )
    async def history(
        interaction: discord.Interaction,
        name: str,
        tag: str,
        count: int = 5,
        server: str = default_server,
    ):
        log_command(interaction)

        await interaction.response.defer()  # this function run for quite a long time for higher match count

        server_code = get_server_code(server)
        if server_code is None:
            await interaction.response.send_message(invalid_server(server))
            return

        if count > 20 or count < 1:
            count = 5

        puuid = await riot_client.get_riot_account_puuid(name, tag)
        if puuid is None:
            await interaction.response.send_message(riot_account_not_found(name, tag))
            return

        data = await riot_client.get_recent_matches_infos(
            puuid, server_code, int(count)
        )
        if len(data[0]) <= 0:
            await interaction.response.send_message(
                f"No match history found for summoner {name}#{tag}"
            )
            return
        embed = embed_generator.generate_history_embed(data)
        await interaction.followup.send(embed=embed)

    @command_tree.command(name="help", description="Shows all available commands")
    async def help(interaction: discord.Interaction):
        log_command(interaction)

        embed = embed_generator.generate_help_embed(
            riot_client.server_names, default_server
        )
        await interaction.response.send_message(embed=embed)

    def get_server_code(server_name):
        server_name = server_name.upper()
        if server_name not in riot_client.server_names:
            return None
        return riot_client.server_names[server_name]

    def log_command(interaction: discord.Interaction):
        command = interaction.data["name"]
        options = ""
        if "options" in interaction.data:
            options = " ".join([str(x["value"]) for x in interaction.data["options"]])
        user = interaction.user
        guild = interaction.guild
        channel = interaction.channel
        log(
            f"Command [{command}] with options [{options}] from [{user}] in guild [{guild}], channel [{channel}]"
        )

    def log(message, level="INFO"):
        timestamp = datetime.datetime.now()
        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp_str} {level}\t{message}")

    def riot_account_not_found(gameName, tagLine):
        return f"Riot Account {gameName}#{tagLine} doesn't exist!"

    def summoner_not_found(gameName, tagLine, server):
        return f"Summoner {gameName}#{tagLine} doesn't exist on the {server} server!"

    def invalid_server(server):
        return f"Server {server} doesn't exsit! Please use one of the following: {', '.join(riot_client.server_names.keys())}"

    bot.run(os.environ.get("DISCORD_TOKEN"))


if __name__ == "__main__":
    main()
