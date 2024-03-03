# League of Legends Discord bot

League Stats bot for Discord is a simple tool to check your last games, match history and profile. It's created to allow me and my friends to show our best games on our Discord server. Right now bot has three commands. First allows you to check your profile info, such as summoner level, rank and your favourite champs. Second one is designed to show detailed stats about one game. The third command allows user to see up to 20 previous matches of a player with basic stats of that summoner.

## List of commands:
```
/profile {player} {tag} {server?} - See your rank, mastery and favourite champs
/match {player} {tag} {1-100?} {server?} - Your game from history, if no ID given - last
/history {player} {tag} {1-20?} {server?} - Check your game history
```

## .env file:
```
DISCORD_TOKEN=YOUR_DICORD_TOKEN
RIOT_TOKEN=YOUR_RIOT_TOKEN
(Optional) SERVER=eun1
(Optional) REGION=europe
```

## Running the bot:
Your can run this bot using Docker
```bash
docker compose up -d 
```
or local Python interpreter
```bash
pip install -r requirements.txt
python ./src/main.py
```
`.env` file should be located in the root directory. Alternatively, you can use shell environment variables.

### Try it out!
https://discord.com/api/oauth2/authorize?client_id=989636329572810782&permissions=18432&scope=bot%20applications.commands
