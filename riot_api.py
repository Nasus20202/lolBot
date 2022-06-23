import requests
from game_info import GameInfo, PlayerInfo

class RiotAPI:
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

    def get_match_info_by_id(self, match_id):
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

    def get_latest_match_id(self, username):
        matches = self.get_recent_matches(username, 1)
        if(len(matches) > 0):
            return matches[0]
        return ''
