from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum

class Platform(str, Enum):
    mobile = "mobile"
    desktop = "desktop"

class OSFamily(str, Enum):
    ios = "iOS"
    android = "Android"
    windows = "Windows"
    macos = "macOS"
    linux = "Linux"

class GameCategory(str, Enum):
    slots = "slots"
    poker = "poker"
    blackjack = "blackjack"
    roulette = "roulette"
    sports = "sports"
    other = "other"

class BonusType(str, Enum):
    welcome_bonus = "welcome_bonus"
    deposit_bonus = "deposit_bonus"
    free_spins = "free_spins"
    cashback = "cashback"
    loyalty_bonus = "loyalty_bonus"

# Player Schemas
class PlayerBase(BaseModel):
    player_id: str = Field(..., min_length=1, max_length=100)
    country: str = Field(..., min_length=2, max_length=2)
    platform: Platform
    os_family: OSFamily
    vip_level: int = Field(default=1, ge=1, le=10)

class PlayerCreate(PlayerBase):
    pass

class Player(PlayerBase):
    player_id: str
    registration_date: datetime
    first_deposit_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Session Schemas
class SessionBase(BaseModel):
    player_id: str
    session_start: datetime
    platform: Platform
    os_family: OSFamily
    country: str

class SessionCreate(SessionBase):
    session_end: Optional[datetime] = None
    session_length_minutes: Optional[float] = None

class Session(SessionBase):
    id: int
    session_end: Optional[datetime] = None
    session_length_minutes: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Bet Schemas
class BetBase(BaseModel):
    player_id: str
    game_name: str = Field(..., min_length=1, max_length=100)
    bet_amount: float = Field(..., gt=0)
    game_category: GameCategory
    platform: Platform
    os_family: OSFamily
    country: str

class BetCreate(BetBase):
    win_amount: float = Field(default=0.0)

class Bet(BetBase):
    id: int
    win_amount: float
    bet_timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True

# Deposit Schemas
class DepositBase(BaseModel):
    player_id: str
    amount: float = Field(..., gt=0)
    payment_method: str = Field(..., min_length=1, max_length=50)

class DepositCreate(DepositBase):
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    status: str = Field(default="completed")

class Deposit(DepositBase):
    id: int
    currency: str
    deposit_timestamp: datetime
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# Withdrawal Schemas
class WithdrawalBase(BaseModel):
    player_id: str
    amount: float = Field(..., gt=0)
    payment_method: str = Field(..., min_length=1, max_length=50)

class WithdrawalCreate(WithdrawalBase):
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    status: str = Field(default="completed")

class Withdrawal(WithdrawalBase):
    id: int
    currency: str
    withdrawal_timestamp: datetime
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# Bonus Schemas
class BonusBase(BaseModel):
    player_id: str
    bonus_type: BonusType
    bonus_amount: float = Field(..., gt=0)

class BonusCreate(BonusBase):
    bonus_currency: str = Field(default="EUR", min_length=3, max_length=3)
    campaign_id: Optional[str] = None

class Bonus(BonusBase):
    id: int
    bonus_currency: str
    is_redeemed: bool
    redeemed_at: Optional[datetime] = None
    bonus_timestamp: datetime
    campaign_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Player Features Schemas
class PlayerFeaturesBase(BaseModel):
    player_id: str
    feature_date: date

class PlayerFeaturesCreate(PlayerFeaturesBase):
    # Behavioral features
    days_active_last_30: int = Field(default=0, ge=0)
    sessions_last_30: int = Field(default=0, ge=0)
    avg_session_length: float = Field(default=0.0, ge=0)
    days_since_last_login: int = Field(default=0, ge=0)

    # Betting features
    total_bets: int = Field(default=0, ge=0)
    total_bet_amount: float = Field(default=0.0, ge=0)
    avg_bet_size: float = Field(default=0.0, ge=0)
    bets_per_session: float = Field(default=0.0, ge=0)
    unique_games_played: int = Field(default=0, ge=0)
    games_played_breakdown: Optional[Dict[str, int]] = None

    # Financial features
    total_deposit: float = Field(default=0.0, ge=0)
    total_withdrawal: float = Field(default=0.0, ge=0)
    net_ggr: float = Field(default=0.0)
    num_deposit_transactions: int = Field(default=0, ge=0)
    avg_deposit_amount: float = Field(default=0.0, ge=0)
    days_since_first_deposit: Optional[int] = Field(default=None, ge=0)

    # Engagement features
    friends_count: int = Field(default=0, ge=0)
    messages_sent: int = Field(default=0, ge=0)
    tournaments_participated: int = Field(default=0, ge=0)

    # Promotion features
    bonus_used: bool = Field(default=False)
    bonus_amount_used: float = Field(default=0.0, ge=0)
    num_offers_received_last_30: int = Field(default=0, ge=0)
    num_offers_redeemed_last_30: int = Field(default=0, ge=0)

    # Derived features
    trend_session_count: float = Field(default=0.0)
    trend_deposit_amount: float = Field(default=0.0)
    time_between_sessions_mean: float = Field(default=0.0, ge=0)
    time_between_sessions_std: float = Field(default=0.0, ge=0)

class PlayerFeatures(PlayerFeaturesBase):
    id: int
    churn_label: Optional[bool] = None
    churn_probability: Optional[float] = None
    predicted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Prediction Request/Response Schemas
class PredictionRequest(BaseModel):
    player_id: str
    feature_date: Optional[date] = None

class PredictionResponse(BaseModel):
    player_id: str
    churn_probability: float
    churn_label: bool
    confidence_score: Optional[float] = None
    feature_date: date
    predicted_at: datetime

# Batch Prediction Schemas
class BatchPredictionRequest(BaseModel):
    player_ids: List[str]
    feature_date: Optional[date] = None

class BatchPredictionResponse(BaseModel):
    predictions: List[PredictionResponse]
    total_processed: int
    processing_time_seconds: float

# Model Performance Schemas
class ModelMetrics(BaseModel):
    model_version: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    pr_auc: float
    created_at: datetime

class ModelMetricsResponse(BaseModel):
    current_metrics: ModelMetrics
    historical_metrics: Optional[List[ModelMetrics]] = None

# Health Check Schema
class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    database_connected: bool
    model_loaded: bool
