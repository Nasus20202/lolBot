import aiohttp
import time

from logger import log
from game_info import NameTag, GameInfo, PlayerInfo, UserInfo


def ttl_cache(ttl=60, max_size=128):
    def wrapper(func):
        cache = {}

        async def wrapped(*args, **kwargs):
            key = (args, frozenset(kwargs.items()))
            if key in cache:
                if ttl == -1 or cache[key]["time"] + ttl > time.time():
                    log(
                        f"Cache hit for {func.__name__} with args: {args}, kwargs: {kwargs}",
                        "TRACE",
                    )
                    return cache[key]["value"]
            result = await func(*args, **kwargs)
            if len(cache) > max_size:
                log(
                    f"Cache size {max_size} exceeded, removing oldest entry for {func.__name__}",
                    "TRACE",
                )
                cache.pop(next(iter(cache)))
            log(
                f"Caching result for {func.__name__} with args: {args}, kwargs: {kwargs}",
                "TRACE",
            )
            cache[key] = {"value": result, "time": time.time()}
            return result

        return wrapped

    return wrapper


class RiotAPI:
    queue_types = {
        400: "Draft",
        420: "Solo/Duo",
        430: "Blind",
        440: "Flex",
        450: "ARAM",
        700: "Clash",
    }
    queue_weight = {
        "UNRANKED": -1,
        "IRON": 0,
        "BRONZE": 1,
        "SILVER": 2,
        "GOLD": 3,
        "PLATINUM": 4,
        "EMERALD": 5,
        "DIAMOND": 6,
        "MASTER": 7,
        "GRANDMASTER": 8,
        "CHALLENGER": 9,
    }
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
        "SEA": "SG2",
        "TW": "TW2",
        "VN": "VN2",
    }

    def __init__(self, api_key, region):
        self.api_key = api_key
        self.region = region.upper()
        self.universal_api_url = f"https://{region}.api.riotgames.com/"

    def __str__(self):
        return f"RiotAPI(api_key={self.api_key[:16] + '...'}, region={self.region})"

    def __repr__(self):
        return str(self)

    async def _make_request(self, url, params):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()

                if response.status < 200 or response.status >= 300:
                    log(
                        f"Request failed: received {response.status} for {url}", "ERROR"
                    )
                return data, response.status

    def get_server_url(self, server):
        return f"https://{server}.api.riotgames.com/"

    @ttl_cache(ttl=3600 * 24, max_size=1024)
    async def get_riot_account_puuid(self, gameName, tagLine):
        log(f"Fetching PUUID for {gameName}#{tagLine} on {self.region}", "DEBUG")

        url = f"{self.universal_api_url}riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}"
        params = {"api_key": self.api_key}
        data, status = await self._make_request(url, params)
        if status == 200:
            return data["puuid"]
        log(f"Failed to get PUUID for {gameName}#{tagLine}, status: {status}", "ERROR")
        return None

    @ttl_cache(ttl=3600 * 24, max_size=1024)
    async def get_riot_nametag_by_puuid(self, puuid):
        log(f"Fetching NameTag for PUUID {puuid} on {self.region}", "DEBUG")

        url = f"{self.universal_api_url}riot/account/v1/accounts/by-puuid/{puuid}"
        params = {"api_key": self.api_key}
        data, status = await self._make_request(url, params)
        if status == 200:
            return NameTag(data["gameName"], data["tagLine"])
        log(f"Failed to get nametag for PUUID {puuid}, status: {status}", "ERROR")
        return None

    @ttl_cache(ttl=3600 * 24, max_size=1024)
    async def get_summoner_by_puuid(self, puuid, server):
        log(f"Fetching summoner for PUUID {puuid} on {server}", "DEBUG")

        url = f"{self.get_server_url(server)}lol/summoner/v4/summoners/by-puuid/{puuid}"
        params = {"api_key": self.api_key}
        data, status = await self._make_request(url, params)
        if status == 200:
            data["status_code"] = status
            data["message"] = "Summoner found"
            return data
        log(
            f"Failed to get summoner for PUUID {puuid} on {server}, status: {status}",
            "ERROR",
        )
        return data.get("status", status)

    @ttl_cache()
    async def get_matches_ids_by_puuid(self, puuid, count=20, start=0):
        log(
            f"Fetching match IDs for PUUID {puuid} with count {count} on {self.region}",
            "DEBUG",
        )

        url = f"{self.universal_api_url}lol/match/v5/matches/by-puuid/{puuid}/ids"
        params = {"api_key": self.api_key, "count": count, "start": start}
        data, status = await self._make_request(url, params)
        if status == 200:
            return data
        log(f"Failed to get match IDs for PUUID {puuid}, status: {status}", "ERROR")
        return []

    @ttl_cache(ttl=3600 * 24)
    async def get_raw_match_info_by_id(self, match_id):
        log(
            f"Fetching raw match info for match ID {match_id} on {self.region}", "DEBUG"
        )

        url = f"{self.universal_api_url}lol/match/v5/matches/{match_id}"
        params = {"api_key": self.api_key}
        data, status = await self._make_request(url, params)
        if status == 200:
            data["status_code"] = status
            data["message"] = "Match found"
            return data
        log(f"Failed to get match info for {match_id}, status: {status}", "ERROR")
        return data.get("status", status)

    @ttl_cache()
    async def get_ranked_info(self, puuid, server):
        log(f"Fetching ranked info for PUUID {puuid} on {server}", "DEBUG")

        url = f"{self.get_server_url(server)}lol/league/v4/entries/by-puuid/{puuid}"
        params = {"api_key": self.api_key}
        ranks = []
        data, status = await self._make_request(url, params)
        if status == 200:
            for rankData in data:
                if "rank" not in rankData:
                    continue
                queue = rankData["queueType"]
                tier = rankData["tier"]
                rank = rankData["rank"]
                lp = rankData["leaguePoints"]
                wins = rankData["wins"]
                losses = rankData["losses"]
                rankArray = [queue, tier, rank, lp, wins, losses]
                ranks.append(rankArray)
        else:
            log(
                f"Failed to get ranked info for PUUID {puuid} on {server}, status: {status}",
                "ERROR",
            )
        return ranks

    @ttl_cache()
    async def get_mastery_info(self, puuid, server):
        log(f"Fetching mastery info for PUUID {puuid} on {server}", "DEBUG")

        url = f"{self.get_server_url(server)}lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}"
        params = {"api_key": self.api_key}
        champions = []
        data, status = await self._make_request(url, params)
        if status == 200:
            for champion in data:
                id = champion["championId"]
                level = champion["championLevel"]
                points = champion["championPoints"]
                last_play = champion["lastPlayTime"]
                champions.append([id, level, points, last_play])
        else:
            log(
                f"Failed to get mastery info for PUUID {puuid} on {server}, status: {status}",
                "ERROR",
            )
        return champions

    async def get_recent_matches_ids(self, puuid, server, count=20):
        summoner_data = await self.get_summoner_by_puuid(puuid, server)
        if (
            not isinstance(summoner_data, dict)
            or summoner_data.get("status_code") != 200
        ):
            return [[], summoner_data]
        summoner_puuid = summoner_data["puuid"]
        return [
            await self.get_matches_ids_by_puuid(summoner_puuid, count=count),
            summoner_data,
        ]

    async def get_match_info_by_id(self, match_id, load_name_tags=False):
        raw_data = await self.get_raw_match_info_by_id(match_id)
        if not isinstance(raw_data, dict) or raw_data.get("status_code") != 200:
            return None
        start_time = raw_data["info"]["gameStartTimestamp"]
        game_duration = raw_data["info"]["gameDuration"]
        queueId = raw_data["info"]["queueId"]
        queue_type = "Other"
        if queueId in self.queue_types:
            queue_type = self.queue_types[queueId]
        winner = "Blue"
        participants = []
        for participant in raw_data["info"]["participants"]:
            puuid = participant["puuid"]
            name = (
                await self.get_riot_nametag_by_puuid(puuid) if load_name_tags else None
            )
            kills = participant["kills"]
            deaths = participant["deaths"]
            assists = participant["assists"]
            champion_name = participant["championName"]
            champion_id = participant["championId"]
            gold_earned = participant["goldEarned"]
            damage = participant["totalDamageDealtToChampions"]
            creep_score = (
                participant["totalMinionsKilled"] + participant["neutralMinionsKilled"]
            )
            vision_score = participant["visionScore"]
            team = "Red"
            if participant["teamId"] == 100:
                team = "Blue"
            if participant["win"] and team == "Red":
                winner = "Red"
            multikills = [
                participant["doubleKills"],
                participant["tripleKills"],
                participant["quadraKills"],
                participant["pentaKills"],
            ]
            position = participant["individualPosition"]
            player_info = PlayerInfo(
                puuid,
                name,
                kills,
                deaths,
                assists,
                champion_name,
                champion_id,
                gold_earned,
                damage,
                creep_score,
                vision_score,
                team,
                multikills,
                position,
            )
            participants.append(player_info)
        game_info = GameInfo(
            match_id, start_time, game_duration, winner, participants, queue_type
        )
        return game_info

    async def get_recent_matches_infos(self, puuid, server, count=20):
        matches_infos = []
        data = await self.get_recent_matches_ids(puuid, server, count)
        for match_id in data[0]:
            match_info = await self.get_match_info_by_id(match_id)
            if match_info is not None:
                matches_infos.append(match_info)
        return [matches_infos, data[1]]

    async def get_recent_match_info(self, puuid, server, id=0):
        match_data = await self.get_recent_matches_ids(puuid, server, id + 1)
        if len(match_data[0]) > id:
            return await self.get_match_info_by_id(
                match_data[0][id], load_name_tags=True
            )
        return None

    async def get_profile_info(self, puuid, server):
        summoner = await self.get_summoner_by_puuid(puuid, server)
        if not isinstance(summoner, dict) or summoner.get("status_code") != 200:
            return {"status_code": 404, "message": "Summoner not found"}
        puuid = summoner["puuid"]
        name = await self.get_riot_nametag_by_puuid(puuid)
        level = summoner["summonerLevel"]
        icon = summoner["profileIconId"]
        ranks = await self.get_ranked_info(puuid, server)
        rank_solo = "UNRANKED"
        rank_flex = "UNRANKED"
        lp_solo = 0
        lp_flex = 0
        wins_solo = 0
        losses_solo = 0
        wins_flex = 0
        losses_flex = 0
        max_division = "UNRANKED"
        for rank in ranks:
            if rank[0] == "RANKED_SOLO_5x5":
                rank_solo = f"{rank[1]} {rank[2]}"
                lp_solo = rank[3]
                wins_solo = rank[4]
                losses_solo = rank[5]
            elif rank[0] == "RANKED_FLEX_SR":
                rank_flex = f"{rank[1]} {rank[2]}"
                lp_flex = rank[3]
                wins_flex = rank[4]
                losses_flex = rank[5]
            if (
                self.queue_weight[max_division.upper()]
                < self.queue_weight[rank[1].upper()]
            ):
                max_division = rank[1].upper()

        champions = await self.get_mastery_info(puuid, server)
        top_champs = champions[:3]
        total_mastery = 0
        total_points = 0
        for champion in champions:
            total_mastery += champion[1]
            total_points += champion[2]
        user = UserInfo(
            puuid,
            name,
            level,
            icon,
            rank_solo,
            rank_flex,
            lp_solo,
            lp_flex,
            wins_solo,
            losses_solo,
            wins_flex,
            losses_flex,
            max_division,
            top_champs,
            total_points,
            total_mastery,
        )
        return {"status_code": 200, "user": user}
