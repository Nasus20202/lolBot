# League of Legends Discord bot

League Stats bot for Discord is a simple tool to check your last games, match history and profile. It's created to allow me and my friends to show our best games on our Discord server. Right now bot has three commands. First allows you to check your profile info, such as summoner level, rank and your favourite champs. Second one is designed to show detailed stats about one game. The third command allows user to see up to 20 previous matches of a player with basic stats of that summoner.

## List of commands:
```
!profile {player} - See your rank, mastery and favourite champs (!player, !rank, !user, !p, !r, !u)
!match {player} {1-100} - Your game, if no ID given - last (!m, !last, !l)
!history {player} {1-20} - Check your game history (!matches, !h)
```

## .env file:
```
DISCORD_TOKEN=YOUR_DICORD_TOKEN
RIOT_TOKEN=YOUR_RIOT_TOKEN
```
