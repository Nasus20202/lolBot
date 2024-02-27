class GameInfo:
    def __init__(self, id, start_time, duration, winner, participants, queue_type):
        self.id = id
        self.start_time = start_time
        self.duration = duration
        self.winner = winner
        self.participants = participants
        self.queue_type = queue_type


class PlayerInfo:
    def __init__(
        self,
        id,
        summoner_name,
        kills,
        deaths,
        assists,
        champion_name,
        champion_id,
        gold,
        damage,
        creep_score,
        vision_score,
        team,
        multikills,
        position,
    ):
        self.id = id
        self.summoner_name = summoner_name
        self.kills = kills
        self.deaths = deaths
        self.assists = assists
        self.champion_name = champion_name
        self.champion_id = champion_id
        self.gold = gold
        self.damage = damage
        self.creep_score = creep_score
        self.vision_score = vision_score
        self.team = team
        self.multikills = multikills
        self.position = position

    def kda(self):
        if self.deaths == 0:
            return "Perfect"
        return str(round((self.kills + self.assists) / self.deaths, 2))


class UserInfo:
    def __init__(
        self,
        id,
        summoner_name,
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
    ):
        self.id = id
        self.summoner_name = summoner_name
        self.level = level
        self.icon = icon
        self.rank_solo = rank_solo
        self.rank_flex = rank_flex
        self.lp_solo = lp_solo
        self.lp_flex = lp_flex
        self.wins_solo = wins_solo
        self.losses_solo = losses_solo
        self.wins_flex = wins_flex
        self.losses_flex = losses_flex
        self.max_division = max_division
        self.top_champs = top_champs
        self.total_points = total_points
        self.total_mastery = total_mastery
