from sqlalchemy import Column, Integer, Float, String, Boolean, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from datetime import date, time

from .database import Base


class Player(Base):
    """
    Represents a unique football player.
    """

    __tablename__ = "players"
    player_id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    initials = Column(String, unique=True, nullable=False)

    ratings = relationship("PlayerRating", back_populates="player")

    def __repr__(self):
        return f"<Player(name='{self.name}')>"

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Team(Base):
    """
    Represents a Premier League team.
    """

    __tablename__ = "teams"
    team_id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    fullname = Column(String, unique=True, nullable=False)
    fbref_team_id = Column(String, unique=True, nullable=False)

    # Relationships for easy access to matches
    home_matches = relationship(
        "Match", back_populates="home_team", foreign_keys="Match.home_team_id"
    )
    away_matches = relationship(
        "Match", back_populates="away_team", foreign_keys="Match.away_team_id"
    )
    lineups = relationship("Lineup", back_populates="team")
    shooting_stats = relationship("MatchShootingStat", back_populates="team")

    def __repr__(self):
        return f"<Team(name='{self.name}', fullname='{self.fullname}')>"

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class PlayerRating(Base):
    """
    Represents FIFA ratings for a player in a specific season.
    """

    __tablename__ = "player_ratings"
    rating_id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.player_id"), nullable=False)
    season = Column(String, nullable=False)  # e.g., "2024-2025"
    rating = Column(Integer, nullable=True)  # Overall rating
    position = Column(String, nullable=True)  # Position
    version = Column(String, nullable=True)  # Version
    psprice = Column(Integer, nullable=True)  # Pace stat
    skill = Column(Integer, nullable=True)  # Skill moves
    weakfoot = Column(Integer, nullable=True)  # Weak foot
    workrate = Column(String, nullable=True)  # Work rate
    pace = Column(Integer, nullable=True)  # Pace
    shooting = Column(Integer, nullable=True)  # Shooting
    passing = Column(Integer, nullable=True)  # Passing
    dribbling = Column(Integer, nullable=True)  # Dribbling
    defense = Column(Integer, nullable=True)  # Defense (def is reserved keyword)
    physical = Column(Integer, nullable=True)  # Physical
    basestats = Column(Integer, nullable=True)  # Base stats
    ingamestats = Column(Integer, nullable=True)  # In-game stats

    player = relationship("Player", back_populates="ratings")

    def __repr__(self):
        return f"<PlayerRating(player='{self.player.name}', season='{self.season}')>"

    def to_dict(self):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        data["player_name"] = self.player.name if self.player else None
        return data


class Match(Base):
    """
    Represents a Premier League match.
    """

    __tablename__ = "matches"
    match_id = Column(Integer, primary_key=True)
    season = Column(String, nullable=False)  # e.g., "2024-2025"
    week = Column(Integer, nullable=True)  # week (match week)
    day = Column(String, nullable=True)  # e.g., "Sat"
    date = Column(Date, nullable=False)  # Match date
    time = Column(Time, nullable=True)  # e.g., "15:00"
    home_team_id = Column(Integer, ForeignKey("teams.team_id"), nullable=False)
    away_team_id = Column(Integer, ForeignKey("teams.team_id"), nullable=False)
    home_goals = Column(Integer, nullable=True)  # From Score (e.g., "2" from "2–1")
    away_goals = Column(Integer, nullable=True)  # From Score (e.g., "1" from "2–1")
    result = Column(String, nullable=True)  # Derived: "H", "A", "D"
    attendance = Column(Integer, nullable=True)
    venue = Column(String, nullable=True)
    referee = Column(String, nullable=True)
    match_report = Column(String, nullable=True)  # URL or identifier
    notes = Column(String, nullable=True)  # e.g., postponed matches

    home_team = relationship(
        "Team", back_populates="home_matches", foreign_keys=[home_team_id]
    )
    away_team = relationship(
        "Team", back_populates="away_matches", foreign_keys=[away_team_id]
    )
    lineups = relationship("Lineup", back_populates="match")
    shooting_stats = relationship("MatchShootingStat", back_populates="match")

    def __repr__(self):
        return f"<Match(season='{self.season}', date='{self.date}', home_team='{self.home_team.name}', away_team='{self.away_team.name}')>"

    def to_dict(self):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        # Add foreign attributes
        data["home_team"] = self.home_team.name if self.home_team else None
        data["away_team"] = self.away_team.name if self.away_team else None
        data["home_team_fullname"] = self.home_team.fullname if self.home_team else None
        data["away_team_fullname"] = self.away_team.fullname if self.away_team else None
        data["Score"] = f"{self.home_goals}-{self.away_goals}"
        data["FTHG"] = self.home_goals
        data["FTAG"] = self.away_goals
        return data


class MatchShootingStat(Base):
    """
    Represents shooting statistics for a team in a specific match.
    """

    __tablename__ = "match_shooting_stats"
    stat_id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.match_id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.team_id"), nullable=False)
    round = Column(String, nullable=True)  # e.g., "Matchweek 1"
    day = Column(String, nullable=True)
    venue = Column(String, nullable=True)  # "Home" or "Away"
    result = Column(String, nullable=True)  # "W", "L", "D"
    gf = Column(Integer, nullable=True)  # Goals for
    ga = Column(Integer, nullable=True)  # Goals against
    opponent = Column(String, nullable=True)
    sh = Column(Integer, nullable=True)  # Shots
    sot = Column(Integer, nullable=True)  # Shots on target
    sot_percent = Column(Float, nullable=True)  # SoT%
    g_per_sh = Column(Float, nullable=True)  # G/Sh
    g_per_sot = Column(Float, nullable=True)  # G/SoT
    dist = Column(Float, nullable=True)  # Average shot distance
    pk = Column(Integer, nullable=True)  # Penalty kicks scored
    pkatt = Column(Integer, nullable=True)  # Penalty kick attempts
    fk = Column(Integer, nullable=True)  # Free kicks

    match = relationship("Match", back_populates="shooting_stats")
    team = relationship("Team", back_populates="shooting_stats")

    def to_dict(self):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        data["team_name"] = self.team.name if self.team else None
        data["time"] = self.match.time if self.match else None
        data["week"] = self.match.week if self.match else None
        data["date"] = self.match.date if self.match else None
        return data

class Lineup(Base):
    """
    Represents a player's participation in a match lineup.
    """

    __tablename__ = "lineups"
    lineup_id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.match_id"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.player_id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.team_id"), nullable=False)
    is_starter = Column(Boolean, nullable=False, default=True)

    match = relationship("Match", back_populates="lineups")
    team = relationship("Team", back_populates="lineups")

    def __repr__(self):
        return f"<Lineup(match_id='{self.match_id}', player='{self.player.name}', team='{self.team.name}')>"

    def to_dict(self):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        data["team_name"] = self.team.name if self.team else None
        data["player_name"] = self.player.name if self.player else None
        return data
