-- 1. Players
CREATE TABLE players (
    player_id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    registration_date DATE NOT NULL,
    country VARCHAR(50),
    vip_level INT DEFAULT 0,
    gender VARCHAR(10),
    birth_year INT,
    is_active BOOLEAN DEFAULT TRUE
);

-- 2. Sessions
CREATE TABLE sessions (
    session_id SERIAL PRIMARY KEY,
    player_id INT REFERENCES players(player_id),
    login_time TIMESTAMP NOT NULL,
    logout_time TIMESTAMP,
    device_type VARCHAR(20),
    platform VARCHAR(20),
    country VARCHAR(50)
);

-- 3. Bets
CREATE TABLE bets (
    bet_id SERIAL PRIMARY KEY,
    player_id INT REFERENCES players(player_id),
    game_name VARCHAR(100),
    bet_amount NUMERIC(10,2),
    win_amount NUMERIC(10,2),
    bet_time TIMESTAMP NOT NULL
);

-- 4. Deposits
CREATE TABLE deposits (
    deposit_id SERIAL PRIMARY KEY,
    player_id INT REFERENCES players(player_id),
    deposit_time TIMESTAMP NOT NULL,
    amount NUMERIC(10,2),
    payment_method VARCHAR(50)
);

-- 5. Withdrawals
CREATE TABLE withdrawals (
    withdrawal_id SERIAL PRIMARY KEY,
    player_id INT REFERENCES players(player_id),
    withdrawal_time TIMESTAMP NOT NULL,
    amount NUMERIC(10,2),
    method VARCHAR(50)
);

-- 6. Bonuses
CREATE TABLE bonuses (
    bonus_id SERIAL PRIMARY KEY,
    player_id INT REFERENCES players(player_id),
    bonus_type VARCHAR(50),
    bonus_amount NUMERIC(10,2),
    issued_date TIMESTAMP,
    redeemed_date TIMESTAMP
);

-- 7. Derived Features (for ML)
CREATE TABLE player_features (
    player_id INT PRIMARY KEY REFERENCES players(player_id),
    days_active_last_30 INT,
    total_bets INT,
    total_bet_amount NUMERIC(12,2),
    avg_bet_size NUMERIC(12,2),
    total_deposit NUMERIC(12,2),
    total_withdrawal NUMERIC(12,2),
    win_rate NUMERIC(5,2),
    bonus_used BOOLEAN,
    sessions_per_week NUMERIC(5,2),
    days_since_last_login INT,
    churn_label BOOLEAN
);
