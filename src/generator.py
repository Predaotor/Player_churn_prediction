"""
generate_synthetic_casino_data.py
Generates synthetic casino event logs + aggregated player features for churn modelling.

Requirements:
    pip install pandas numpy faker sqlalchemy

Outputs (CSV):
    - players.csv
    - sessions.csv
    - bets.csv
    - deposits.csv
    - withdrawals.csv
    - bonuses.csv
    - player_features.csv
"""

import random
import uuid
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from faker import Faker

fake = Faker()
F = fake
from math import floor

# ---------- CONFIG ----------
N_PLAYERS = 4000     # adjust for scale (1k for dev, 100k+ for production)
START_DATE = datetime.now() - timedelta(days=180)
END_DATE = datetime.now()
CHURN_LOOKBACK_DAYS = 30    # window to compute features
CHURN_LABEL_THRESHOLD = 14  # days since last login -> churn
SEED = 42
OUTLIER_FRACTION = 0.005    # 0.5% extreme outliers
MISSING_FRACTION = 0.01     # fraction of fields to blank
DRIFT_FRACTION = 0.2        # fraction of players in test drift scenario
# ----------------------------

random.seed(SEED)
np.random.seed(SEED)

# helper utilities
def rand_dates(start, end, n):
    start_u = start.timestamp()
    end_u = end.timestamp()
    return [datetime.fromtimestamp(random.uniform(start_u, end_u)) for _ in range(n)]

def weighted_choice(choices, weights):
    return random.choices(choices, weights=weights, k=1)[0]

# ---------- 1. Players ----------
def generate_players(n):
    players = []
    countries = ['GE','UK','DE','FR','IT','ES','SE','NO']
    acquisition_sources = ['organic','ad_campaign','affiliate','email']
    for i in range(n):
        pid = i + 1
        reg_days_ago = random.randint(0, 400)
        registration_date = (datetime.now() - timedelta(days=reg_days_ago)).date()
        vip = int(np.clip(np.round(np.random.exponential(0.4)), 0, 5))
        country = random.choice(countries)
        acquisition = random.choice(acquisition_sources)
        # player archetype: casual / regular / whale / bot
        archetype = weighted_choice(['casual','regular','whale','bot'], [0.55,0.35,0.08,0.02])
        # social / engagement attributes
        if archetype == 'whale':
            friends_count = int(abs(np.random.normal(30, 20)))
            messages_sent = int(abs(np.random.normal(200, 150)))
        elif archetype == 'regular':
            friends_count = int(abs(np.random.normal(10, 8)))
            messages_sent = int(abs(np.random.normal(40, 60)))
        elif archetype == 'casual':
            friends_count = int(abs(np.random.normal(3, 4)))
            messages_sent = int(abs(np.random.normal(5, 10)))
        else:  # bot
            friends_count = int(abs(np.random.normal(0, 1)))
            messages_sent = int(abs(np.random.normal(0, 1)))
        players.append({
            'player_id': pid,
            'username': f'user_{pid}',
            'registration_date': registration_date,
            'country': country,
            'vip_level': vip if archetype!='casual' else 0,
            'acquisition': acquisition,
            'friends_count': friends_count,
            'messages_sent': messages_sent,
            'archetype': archetype
        })
    return pd.DataFrame(players)

players_df = generate_players(N_PLAYERS)

# ---------- 2. Event logs generation ----------
def generate_sessions(players_df, start, end):
    rows = []
    for _, p in players_df.iterrows():
        pid = p['player_id']
        archetype = p['archetype']
        # sessions per week base by archetype
        base = {'casual':1, 'regular':5, 'whale':8, 'bot':20}[archetype]
        # total sessions in period:
        weeks = (end - start).days / 7
        n_sessions = max(1, int(np.random.poisson(base * weeks)))
        # some variance
        session_dates = rand_dates(start, end, n_sessions)
        for sd in session_dates:
            # apply time-of-day and day-of-week seasonality
            login = sd
            # prefer evenings and weekends; bots skew to uniform/odd hours
            dow = login.weekday()  # 0=Mon .. 6=Sun
            if archetype == 'bot':
                hour = random.randint(0,23)
            else:
                # base hourly weights (more activity 18-23)
                evening = list(range(18,24))
                daytime = list(range(9,18))
                night = list(range(0,9))
                if dow >=5:  # weekend
                    hour = random.choices(evening + daytime + night, weights=[5]*len(evening) + [3]*len(daytime) + [1]*len(night), k=1)[0]
                else:
                    hour = random.choices(evening + daytime + night, weights=[6]*len(evening) + [2]*len(daytime) + [1]*len(night), k=1)[0]
            minute = random.randint(0,59)
            second = random.randint(0,59)
            login = login.replace(hour=hour, minute=minute, second=second)
            # session length minutes based on archetype
            length_min = max(1, int(np.random.normal(30 if archetype!='bot' else 5, 20)))
            logout = login + timedelta(minutes=length_min)
            rows.append({
                'session_id': str(uuid.uuid4()),
                'player_id': pid,
                'login_time': login,
                'logout_time': logout,
                'device_type': random.choice(['mobile','desktop','tablet']),
                'platform': random.choice(['iOS','Android','Windows','macOS']),
                'country': p.country
            })
    return pd.DataFrame(rows)

def generate_bets(players_df, start, end):
    rows = []
    games = ['slots','blackjack','roulette','poker','craps','baccarat']
    for _, p in players_df.iterrows():
        pid = p.player_id
        archetype = p['archetype']
        # bet frequency base
        base_bets_per_week = {'casual':3, 'regular':20, 'whale':150, 'bot':300}[archetype]
        weeks = (end - start).days / 7
        n_bets = max(0, int(np.random.poisson(base_bets_per_week * weeks)))
        bet_times = rand_dates(start, end, n_bets)
        for bt in bet_times:
            game = random.choice(games)
            # bet size distribution
            if archetype == 'whale':
                bet_amount = np.abs(np.random.normal(50, 200)) + 10
            elif archetype == 'bot':
                bet_amount = np.abs(np.random.normal(0.5, 0.5))
            else:
                bet_amount = np.abs(np.random.normal(5, 10))
            # win probability: small positive or negative
            win = np.random.binomial(1, 0.48)  # casino edge ~0.52
            win_amount = 0.0
            if win:
                win_amount = bet_amount * np.random.uniform(0.5, 2.0)
            rows.append({
                'bet_id': str(uuid.uuid4()),
                'player_id': pid,
                'game_name': game,
                'bet_amount': round(float(bet_amount),2),
                'win_amount': round(float(win_amount),2),
                'bet_time': bt
            })
    return pd.DataFrame(rows)

def generate_deposits(players_df, start, end):
    rows = []
    for _, p in players_df.iterrows():
        pid = p['player_id']
        archetype = p['archetype']
        # deposit frequency
        base_dep_per_month = {'casual':0.3, 'regular':1.2, 'whale':5, 'bot':0}[archetype]
        months = (end - start).days / 30
        n_deposits = np.random.poisson(base_dep_per_month * months)
        if n_deposits == 0 and archetype=='whale' and random.random() < 0.05:
            n_deposits = 1
        times = rand_dates(start, end, max(0, n_deposits))
        for t in times:
            if archetype == 'whale':
                amt = np.abs(np.random.normal(500, 1000)) + 50
            else:
                amt = np.abs(np.random.normal(50, 100))
            rows.append({
                'deposit_id': str(uuid.uuid4()),
                'player_id': pid,
                'deposit_time': t,
                'amount': round(float(amt),2),
                'payment_method': random.choice(['card','paypal','crypto','bank'])
            })
    return pd.DataFrame(rows)

def generate_withdrawals(players_df, start, end):
    rows = []
    for _, p in players_df.iterrows():
        pid = p['player_id']
        archetype = p['archetype']
        base_with_per_month = {'casual':0.1, 'regular':0.6, 'whale':2, 'bot':0}[archetype]
        months = (end - start).days / 30
        n_w = np.random.poisson(base_with_per_month * months)
        times = rand_dates(start, end, max(0, n_w))
        for t in times:
            amt = abs(np.random.normal(30, 80))
            rows.append({
                'withdrawal_id': str(uuid.uuid4()),
                'player_id': pid,
                'withdrawal_time': t,
                'amount': round(float(amt),2),
                'method': random.choice(['bank','card'])
            })
    return pd.DataFrame(rows)

def generate_bonuses(players_df, start, end):
    rows = []
    bonus_types = ['free_spin', 'match_deposit', 'cashback', 'no_deposit']
    for _, p in players_df.iterrows():
        pid = p['player_id']
        archetype = p['archetype']
        # probability of receiving bonus
        prob = {'casual':0.05, 'regular':0.15, 'whale':0.35, 'bot':0.0}[archetype]
        if random.random() < prob:
            t = random.choice(rand_dates(start, end, 1))
            b_amt = round(abs(np.random.normal(10 if archetype=='casual' else 100, 50)),2)
            redeemed = t + timedelta(days=random.randint(0,10)) if random.random() < 0.7 else None
            rows.append({
                'bonus_id': str(uuid.uuid4()),
                'player_id': pid,
                'bonus_type': random.choice(bonus_types),
                'bonus_amount': b_amt,
                'issued_date': t,
                'redeemed_date': redeemed
            })
            # sometimes send additional marketing offers (track offers_received separately)
            # we'll represent offers as additional rows with small probability
            if random.random() < 0.05:
                rows.append({
                    'bonus_id': str(uuid.uuid4()),
                    'player_id': pid,
                    'bonus_type': 'marketing_offer',
                    'bonus_amount': 0.0,
                    'issued_date': t + timedelta(days=random.randint(1,7)),
                    'redeemed_date': None
                })
    return pd.DataFrame(rows)

# ---------- Generate logs ----------
print(f"Generating data for {N_PLAYERS} players...")
print("1/6 Generating player profiles...")
players_df = generate_players(N_PLAYERS)
print("2/6 Generating sessions...")
sessions_df = generate_sessions(players_df, START_DATE, END_DATE)
print("3/6 Generating bets...")
bets_df = generate_bets(players_df, START_DATE, END_DATE)
print("4/6 Generating deposits...")
deposits_df = generate_deposits(players_df, START_DATE, END_DATE)
print("5/6 Generating withdrawals...")
withdrawals_df = generate_withdrawals(players_df, START_DATE, END_DATE)
print("6/6 Generating bonuses and promotions...")
bonuses_df = generate_bonuses(players_df, START_DATE, END_DATE)

print("Injecting data quality variations...")
# ---------- Inject outliers ----------
print("Adding outliers...")
def inject_outliers(bets_df, deposits_df, outlier_frac=OUTLIER_FRACTION):
    n = int(len(bets_df) * outlier_frac)
    if n > 0:  # only if we have enough data
        idx = np.random.choice(bets_df.index, size=max(1,n), replace=False)
        bets_df.loc[idx, 'bet_amount'] *= np.random.uniform(50, 500, size=len(idx))
    # deposit outliers
    m = int(len(deposits_df) * outlier_frac)
    if m > 0:  # only if we have enough data
        idxd = np.random.choice(deposits_df.index, size=m, replace=False)
        deposits_df.loc[idxd, 'amount'] *= np.random.uniform(50, 200, size=m)
    return bets_df, deposits_df

if not bets_df.empty and not deposits_df.empty:
    bets_df, deposits_df = inject_outliers(bets_df, deposits_df)

print("Adding missing values...")
# ---------- Inject missingness ----------
def inject_missingness(df, fraction=MISSING_FRACTION):
    if df.empty:  # skip if dataframe is empty
        return df
    df = df.copy()
    n = int(df.size * fraction)
    if n > 0:  # only if we have enough data
        for _ in range(n):
            i = random.choice(df.columns)
            ridx = random.choice(df.index)
            df.at[ridx, i] = None
    return df

# Only inject missingness if we have data
if not sessions_df.empty:
    sessions_df = inject_missingness(sessions_df)
if not bets_df.empty:
    bets_df = inject_missingness(bets_df)
if not deposits_df.empty:
    deposits_df = inject_missingness(deposits_df)
if not withdrawals_df.empty:
    withdrawals_df = inject_missingness(withdrawals_df)
if not bonuses_df.empty:
    bonuses_df = inject_missingness(bonuses_df)

# ---------- 3. Aggregation: compute features for last CHURN_LOOKBACK_DAYS ----------
print("Aggregating features...")
agg_start = END_DATE - timedelta(days=CHURN_LOOKBACK_DAYS)

# filter events within lookback
s_recent = sessions_df[sessions_df['login_time'] >= agg_start]
b_recent = bets_df[bets_df['bet_time'] >= agg_start]
d_recent = deposits_df[deposits_df['deposit_time'] >= agg_start]
w_recent = withdrawals_df[withdrawals_df['withdrawal_time'] >= agg_start]
r_recent = bonuses_df[bonuses_df['issued_date'] >= agg_start]

# helpers to compute per-player stats
def make_features(players_df, sdf, bdf, ddf, wdf, rdf, reference_time=END_DATE):
    rows = []
    for _, p in players_df.iterrows():
        pid = p['player_id']
        ps = sdf[sdf['player_id'] == pid]
        pb = bdf[bdf['player_id'] == pid]
        pdep = ddf[ddf['player_id'] == pid]
        pw = wdf[wdf['player_id'] == pid]
        pr = rdf[rdf['player_id'] == pid]

        days_active = ps['login_time'].dt.date.nunique() if not ps.empty else 0
        total_bets = len(pb)
        total_bet_amount = pb['bet_amount'].sum() if not pb.empty else 0.0
        avg_bet_size = pb['bet_amount'].mean() if not pb.empty else 0.0
        total_deposit = pdep['amount'].sum() if not pdep.empty else 0.0
        total_withdrawal = pw['amount'].sum() if not pw.empty else 0.0
        win_rate = (pb['win_amount'] > 0).sum() / total_bets if total_bets > 0 else 0.0

        # net GGR for the casino in the lookback window: bets minus payouts
        net_ggr = (pb['bet_amount'] - pb['win_amount']).sum() if not pb.empty else 0.0
        unique_games = pb['game_name'].nunique() if not pb.empty else 0
        bonus_used = not pr.empty
        sessions_count = ps['session_id'].nunique() if not ps.empty else 0
        sessions_per_week = sessions_count / (CHURN_LOOKBACK_DAYS / 7.0)

        # last login
        if not ps.empty and ps['login_time'].notnull().any():
            last_login = ps['login_time'].max()
            days_since_last_login = (reference_time - last_login).days
        else:
            # if no session in lookback, compute days since last ever login (approx using full sessions)
            all_ps = sessions_df[sessions_df['player_id'] == pid]
            if not all_ps.empty and all_ps['login_time'].notnull().any():
                last_login = all_ps['login_time'].max()
                days_since_last_login = (reference_time - last_login).days
            else:
                days_since_last_login = 999

        churn_label = 1 if days_since_last_login > CHURN_LABEL_THRESHOLD else 0

        # weekly session trend: compute weekly counts for the lookback window (4 weeks)
        try:
            week_bins = [
                (reference_time - timedelta(days=i * 7 + 7), reference_time - timedelta(days=i * 7))
                for i in range(4)
            ]
            weekly_counts = []
            for start_w, end_w in reversed(week_bins):
                c = (
                    ps[(ps['login_time'] >= start_w) & (ps['login_time'] < end_w)]['session_id'].nunique()
                    if not ps.empty
                    else 0
                )
                weekly_counts.append(int(c))
            if len(weekly_counts) >= 2 and sum(weekly_counts) > 0:
                slope = float(np.polyfit(np.arange(len(weekly_counts)), weekly_counts, 1)[0])
            else:
                slope = 0.0
        except Exception:
            slope = 0.0

        offers_received = len(pr) if not pr.empty else 0
        offers_redeemed = int(pr['redeemed_date'].notnull().sum()) if not pr.empty else 0

        rows.append(
            {
                'player_id': pid,
                'days_active_last_30': int(days_active),
                'total_bets': int(total_bets),
                'total_bet_amount': round(float(total_bet_amount), 2),
                'avg_bet_size': round(float(avg_bet_size), 2) if not np.isnan(avg_bet_size) else 0.0,
                'total_deposit': round(float(total_deposit), 2),
                'total_withdrawal': round(float(total_withdrawal), 2),
                'win_rate': round(float(win_rate), 3),
                'net_ggr': round(float(net_ggr), 2),
                'unique_games_played': int(unique_games),
                'bonus_used': bool(bonus_used),
                'offers_received': int(offers_received),
                'offers_redeemed': int(offers_redeemed),
                'sessions_per_week': round(float(sessions_per_week), 2),
                'session_trend_weekly': round(float(slope), 3),
                'days_since_last_login': int(days_since_last_login),
                'friends_count': int(p['friends_count']),
                'messages_sent': int(p['messages_sent']),
                'churn_label': int(churn_label),
            }
        )

    return pd.DataFrame(rows)

player_features_df = make_features(players_df, s_recent, b_recent, d_recent, w_recent, r_recent, reference_time=END_DATE)

# ---------- 4. Simulate concept drift for a test set ----------
# Create a holdout group with changed behavior (e.g., after a product change)
def apply_drift_to_subset(players_df, fraction=DRIFT_FRACTION):
    n = int(len(players_df) * fraction)
    idx = np.random.choice(players_df.index, size=n, replace=False)
    return players_df.loc[idx, 'player_id'].tolist()

drift_player_ids = apply_drift_to_subset(players_df, fraction=DRIFT_FRACTION)
# For players in drift set, artificially reduce deposits and increase inactivity in next period
# We will create a test_features with drift
test_end = END_DATE + timedelta(days=30)
test_start = END_DATE - timedelta(days=CHURN_LOOKBACK_DAYS)
# generate a second period with lower engagement for drift players
players_drift_df = players_df[players_df['player_id'].isin(drift_player_ids)]
sessions_drift = generate_sessions(players_drift_df, test_start, test_end)
# downscale sessions and deposits for drift players
sessions_drift = sessions_drift.sample(frac=0.3, random_state=SEED)  # strong drop
bets_drift = generate_bets(players_drift_df, test_start, test_end).sample(frac=0.4, random_state=SEED)
deposits_drift = generate_deposits(players_drift_df, test_start, test_end).sample(frac=0.2, random_state=SEED)
withdrawals_drift = generate_withdrawals(players_drift_df, test_start, test_end)
bonuses_drift = generate_bonuses(players_drift_df, test_start, test_end)

# aggregate test features
print("Aggregating test features...")
s_recent_test = sessions_drift
b_recent_test = bets_drift
d_recent_test = deposits_drift
w_recent_test = withdrawals_drift
r_recent_test = bonuses_drift

test_player_features = make_features(players_drift_df, s_recent_test, b_recent_test, d_recent_test, w_recent_test, r_recent_test, reference_time=test_end)

# ---------- 5. Save CSVs ----------
print("Saving CSVs...")
players_df.to_csv('players.csv', index=False)
sessions_df.to_csv('sessions.csv', index=False)
bets_df.to_csv('bets.csv', index=False)
deposits_df.to_csv('deposits.csv', index=False)
withdrawals_df.to_csv('withdrawals.csv', index=False)
bonuses_df.to_csv('bonuses.csv', index=False)
player_features_df.to_csv('player_features.csv', index=False)
test_player_features.to_csv('player_features_test_drift.csv', index=False)

print("Done. Files saved: players.csv, sessions.csv, bets.csv, deposits.csv, withdrawals.csv, bonuses.csv, player_features.csv, player_features_test_drift.csv")
