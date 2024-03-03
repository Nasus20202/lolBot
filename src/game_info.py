from dataclasses import dataclass


@dataclass
class GameInfo:
    id: int
    start_time: int
    duration: int
    winner: str
    participants: list
    queue_type: str


@dataclass
class PlayerInfo:
    id: int
    summoner_name: str
    kills: int
    deaths: int
    assists: int
    champion_name: str
    champion_id: int
    gold: int
    damage: int
    creep_score: int
    vision_score: int
    team: str
    multikills: int
    position: str

    def kda(self):
        if self.deaths == 0:
            return "Perfect"
        return str(round((self.kills + self.assists) / self.deaths, 2))


@dataclass
class UserInfo:
    id: int
    summoner_name: str
    level: int
    icon: str
    rank_solo: str
    rank_flex: str
    lp_solo: int
    lp_flex: int
    wins_solo: int
    losses_solo: int
    wins_flex: int
    losses_flex: int
    max_division: str
    top_champs: list
    total_points: int
    total_mastery: int
