from itertools import count
from pydoc import cli
import requests

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
