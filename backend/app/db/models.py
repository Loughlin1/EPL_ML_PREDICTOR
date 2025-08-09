from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from datetime import date, time

from .database import Base


class Team(Base):
    """
    Represents a Premier League team.
    """
    __tablename__ = "teams"
    team_id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    # Relationships for easy access to matches
    home_matches = relationship("Match", back_populates="home_team", foreign_keys="Match.home_team_id")
    away_matches = relationship("Match", back_populates="away_team", foreign_keys="Match.away_team_id")

    def __repr__(self):
        return f"<Team(name='{self.name}')>"

class Match(Base):
    """
    Represents a Premier League match.
    """
    __tablename__ = "matches"
    match_id = Column(Integer, primary_key=True)
    season = Column(String, nullable=False)  # e.g., "2024-2025"
    week = Column(Integer, nullable=True)  # Wk (match week)
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

    home_team = relationship("Team", back_populates="home_matches", foreign_keys=[home_team_id])
    away_team = relationship("Team", back_populates="away_matches", foreign_keys=[away_team_id])

    def __repr__(self):
        return f"<Match(season='{self.season}', date='{self.date}', home_team='{self.home_team.name}', away_team='{self.away_team.name}')>"