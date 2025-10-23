from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, Date, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

Base = declarative_base()

class Player(Base):
    """Static player information"""
    __tablename__ = "players"

    player_id = Column(String, primary_key=True, index=True)
<<<<<<< HEAD
<<<<<<< HEAD
    registration_date = Column(DateTime, default=datetime.now(timezone.utc))
=======
    registration_date = Column(DateTime, default=datetime.utcnow)
>>>>>>> d2b9430 (feat: Initialize database schema and models for player churn prediction system)
=======
    registration_date = Column(DateTime, default=datetime.now(timezone.utc))
>>>>>>> 7926cd2 (feat(data): generate and aggregate full synthetic casino dataset)
    country = Column(String(2))  # ISO country code
    platform = Column(String(20))  # mobile/desktop
    os_family = Column(String(20))  # iOS/Android/Windows
    vip_level = Column(Integer, default=1)
    first_deposit_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Relationships
    sessions = relationship("Session", back_populates="player")
    bets = relationship("Bet", back_populates="player")
    deposits = relationship("Deposit", back_populates="player")
    withdrawals = relationship("Withdrawal", back_populates="player")
    bonuses = relationship("Bonus", back_populates="player")
    features = relationship("PlayerFeatures", back_populates="player")

class Session(Base):
    """Player session data"""
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String, ForeignKey("players.player_id"), index=True)
    session_start = Column(DateTime, nullable=False)
    session_end = Column(DateTime, nullable=True)
    session_length_minutes = Column(Float, nullable=True)
    platform = Column(String(20))
    os_family = Column(String(20))
    country = Column(String(2))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    # Relationships
    player = relationship("Player", back_populates="sessions")

class Bet(Base):
    """Individual betting transactions"""
    __tablename__ = "bets"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String, ForeignKey("players.player_id"), index=True)
    game_name = Column(String(100), nullable=False)
    bet_amount = Column(Float, nullable=False)
    win_amount = Column(Float, default=0.0)
    bet_timestamp = Column(DateTime, default=datetime.now(timezone.utc))
    game_category = Column(String(50))  # slots, poker, etc.
    platform = Column(String(20))
    os_family = Column(String(20))
    country = Column(String(2))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    # Relationships
    player = relationship("Player", back_populates="bets")

class Deposit(Base):
    """Player deposit events"""
    __tablename__ = "deposits"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String, ForeignKey("players.player_id"), index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="EUR")
    payment_method = Column(String(50))
    deposit_timestamp = Column(DateTime, default=datetime.now(timezone.utc))
    status = Column(String(20), default="completed")  # pending, completed, failed
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    # Relationships
    player = relationship("Player", back_populates="deposits")

class Withdrawal(Base):
    """Player withdrawal events"""
    __tablename__ = "withdrawals"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String, ForeignKey("players.player_id"), index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="EUR")
    payment_method = Column(String(50))
    withdrawal_timestamp = Column(DateTime, default=datetime.now(timezone.utc))
    status = Column(String(20), default="completed")  # pending, completed, failed
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    # Relationships
    player = relationship("Player", back_populates="withdrawals")

class Bonus(Base):
    """Bonus and promotion events"""
    __tablename__ = "bonuses"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String, ForeignKey("players.player_id"), index=True)
    bonus_type = Column(String(50))  # welcome_bonus, deposit_bonus, etc.
    bonus_amount = Column(Float, nullable=False)
    bonus_currency = Column(String(3), default="EUR")
    is_redeemed = Column(Boolean, default=False)
    redeemed_at = Column(DateTime, nullable=True)
    bonus_timestamp = Column(DateTime, default=datetime.now(timezone.utc))
    campaign_id = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    # Relationships
    player = relationship("Player", back_populates="bonuses")

class PlayerFeatures(Base):
    """Derived features for ML model"""
    __tablename__ = "player_features"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String, ForeignKey("players.player_id"), index=True, unique=True)
    feature_date = Column(Date, nullable=False)  # Date for which features are calculated

    # Behavioral features (last 30 days)
    days_active_last_30 = Column(Integer, default=0)
    sessions_last_30 = Column(Integer, default=0)
    avg_session_length = Column(Float, default=0.0)
    days_since_last_login = Column(Integer, default=0)

    # Betting features
    total_bets = Column(Integer, default=0)
    total_bet_amount = Column(Float, default=0.0)
    avg_bet_size = Column(Float, default=0.0)
    bets_per_session = Column(Float, default=0.0)
    unique_games_played = Column(Integer, default=0)
    games_played_breakdown = Column(JSON)  # JSON object with game counts

    # Financial features
    total_deposit = Column(Float, default=0.0)
    total_withdrawal = Column(Float, default=0.0)
    net_ggr = Column(Float, default=0.0)  # Gross Gaming Revenue
    num_deposit_transactions = Column(Integer, default=0)
    avg_deposit_amount = Column(Float, default=0.0)
    days_since_first_deposit = Column(Integer, nullable=True)

    # Engagement features
    friends_count = Column(Integer, default=0)
    messages_sent = Column(Integer, default=0)
    tournaments_participated = Column(Integer, default=0)

    # Promotion features
    bonus_used = Column(Boolean, default=False)
    bonus_amount_used = Column(Float, default=0.0)
    num_offers_received_last_30 = Column(Integer, default=0)
    num_offers_redeemed_last_30 = Column(Integer, default=0)

    # Derived features
    trend_session_count = Column(Float, default=0.0)  # Slope of sessions over time
    trend_deposit_amount = Column(Float, default=0.0)
    time_between_sessions_mean = Column(Float, default=0.0)
    time_between_sessions_std = Column(Float, default=0.0)

    # Churn prediction
    churn_label = Column(Boolean, nullable=True)  # Target variable
    churn_probability = Column(Float, nullable=True)  # Model prediction
    predicted_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Relationships
    player = relationship("Player", back_populates="features")
