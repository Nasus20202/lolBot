from turtle import position
import requests
from game_info import GameInfo, PlayerInfo

class RiotAPI:
    queueTypes = {400: "Draft", 420: "Solo/Duo", 430: "Blind", 440: "Flex", 450: "ARAM", 700: "Clash"}

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://eun1.api.riotgames.com/lol/'
        self.base_url_universal = 'https://europe.api.riotgames.com/lol/'

    def get_summoner_by_name(self, summoner_name):
        url = f"{self.base_url}summoner/v4/summoners/by-name/{summoner_name}"
        params = {'api_key': self.api_key}
        response = requests.get(url, params=params)
        data = response.json()
        if response.status_code == 200:
            data["status_code"] = response.status_code
            data["message"] = "Summoner found"
            return data
        return data["status"]
    
    def get_matches_ids_by_puuid(self, puuid, count=20, start=0):
        url = f"{self.base_url_universal}match/v5/matches/by-puuid/{puuid}/ids"
        params = {'api_key': self.api_key, 'count': count, 'start': start}
        response = requests.get(url, params=params)
        data = response.json()
        if response.status_code == 200:
            return data
        return []

    def get_raw_match_info_by_id(self, match_id):
        url = f"{self.base_url_universal}match/v5/matches/{match_id}"
        params = {'api_key': self.api_key}
        response = requests.get(url, params=params)
        data = response.json()
        if (response.status_code == 200):
            data["status_code"] = response.status_code
            data["message"] = "Match found"
            return data
        return data["status"]

    def get_recent_matches_ids(self, username, count=20):
        summoner_data = self.get_summoner_by_name(username)
        if(summoner_data["status_code"] != 200):
            return []
        summoner_puuid = summoner_data["puuid"]
        return self.get_matches_ids_by_puuid(summoner_puuid, count=count)

    def get_match_info_by_id(self, match_id):
        raw_data = self.get_raw_match_info_by_id(match_id)
        if(raw_data["status_code"] != 200):
            return None
        start_time = raw_data["info"]["gameStartTimestamp"]
        game_duration = raw_data["info"]["gameDuration"]
        queueId = raw_data["info"]["queueId"]
        queue_type = "Other"
        if queueId in self.queueTypes:
            queue_type = self.queueTypes[queueId]
        winner = "Blue"
        participants = []
        for participant in raw_data["info"]["participants"]:
            id = participant["summonerId"]
            summoner_name = participant["summonerName"]
            kills = participant["kills"]
            deaths = participant["deaths"]
            assists = participant["assists"]
            champion_name = participant["championName"]
            champion_id = participant["championId"]
            gold_earned = participant["goldEarned"]
            damage = participant["totalDamageDealtToChampions"]
            creep_score = participant["totalMinionsKilled"]
            vision_score = participant["visionScore"]
            team = "Red"
            if (participant["teamId"] == 100):
                team = "Blue"
            if(participant["win"] and team == "Red"):
                winner = "Red"
            multikills = [participant["doubleKills"], participant["tripleKills"], participant["quadraKills"], participant["pentaKills"]]
            position = participant["individualPosition"]
            player_info = PlayerInfo(id, summoner_name, kills, deaths, assists, champion_name, champion_id, gold_earned, damage, creep_score, vision_score, team, multikills, position)
            participants.append(player_info)
        game_info = GameInfo(id, start_time, game_duration, winner, participants, queue_type)
        return game_info
        
    def get_recent_matches_infos(self, username, count=20):
        matches_infos = []
        for match_id in self.get_recent_matches_ids(username, count):
            match_info = self.get_match_info_by_id(match_id)
            if(match_info is not None):
                matches_infos.append(match_info)
        return matches_infos

    def get_recent_match_info(self, username, id=0):
        match_ids = self.get_recent_matches_ids(username, id+1)
        if(len(match_ids) > id):
            return self.get_match_info_by_id(match_ids[id])
        return None

