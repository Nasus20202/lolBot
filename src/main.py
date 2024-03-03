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

    server_names = {
        "BR": "BR1",
        "EUNE": "EUN1",
        "EUW": "EUW1",
        "LAN": "LA1",
        "LAS": "LA2",
        "NA": "NA1",
        "OCE": "OC1",
        "RU": "RU",
        "TR": "TR1",
        "JP": "JP1",
        "KR": "KR",
        "PH": "PH2",
        "SG": "SG2",
        "TW": "TW2",
        "TH": "TH2",
        "VN": "VN2",
    }

    bot = discord.Client(intents=intents)
    command_tree = discord.app_commands.CommandTree(client=bot)
    riot_client = riot_api.RiotAPI(os.getenv("RIOT_TOKEN"), region)

    @bot.event
    async def on_ready():
        await command_tree.sync()
        log(f"Logged in as {bot.user} (ID: {bot.user.id})")
        await bot.change_presence(
            status=discord.Status.online, activity=discord.Game("League of Legends")
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
            await interaction.response.send_message(summoner_not_found(name, tag))
            return

        if int(id) > 100 or int(id) < 1:
            await interaction.response.send_message(
                f"You can only see your last 100 matches!"
            )
            return
        match_info = await riot_client.get_recent_match_info(puuid, server_code, int(id) - 1)
        if match_info is None:
            await interaction.response.send_message(f"Match not found!")
            return
        embed = await embed_generator.generate_match_embed(match_info, summoner["name"])
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
            await interaction.response.send_message(summoner_not_found(name, tag))
            return
        user = data["user"]
        embed = await embed_generator.generate_user_embed(user)
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

        data = await riot_client.get_recent_matches_infos(puuid, server_code, int(count))
        if len(data[0]) <= 0:
            await interaction.response.send_message(
                f"No match history found for summoner {name}#{tag}"
            )
            return
        embed = await embed_generator.generate_history_embed(data)
        await interaction.followup.send(embed=embed)

    def get_server_code(server_name):
        server_name = server_name.upper()
        if server_name not in server_names:
            return None
        return server_names[server_name]

    def log_command(interaction: discord.Interaction):
        command = interaction.data["name"]
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
        return f"Riot Account {gameName}#{tagLine} doesn't exsit!"

    def summoner_not_found(gameName, tagLine):
        return f"Summoner {gameName}#{tagLine} doesn't exsit!"

    def invalid_server(server):
        return f"Server {server} doesn't exsit! Please use one of the following: {', '.join(server_names.keys())}"

    bot.run(os.environ.get("DISCORD_TOKEN"))


if __name__ == "__main__":
    main()
