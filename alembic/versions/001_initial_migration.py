"""Initial migration

Revision ID: 001
Revises: None
Create Date: 2024-10-21 22:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import json

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create players table
    op.create_table('players',
        sa.Column('player_id', sa.String(), nullable=False),
        sa.Column('registration_date', sa.DateTime(), nullable=True),
        sa.Column('country', sa.String(length=2), nullable=True),
        sa.Column('platform', sa.String(length=20), nullable=True),
        sa.Column('os_family', sa.String(length=20), nullable=True),
        sa.Column('vip_level', sa.Integer(), nullable=True),
        sa.Column('first_deposit_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('player_id')
    )
    op.create_index(op.f('ix_players_player_id'), 'players', ['player_id'], unique=False)

    # Create sessions table
    op.create_table('sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.String(), nullable=True),
        sa.Column('session_start', sa.DateTime(), nullable=False),
        sa.Column('session_end', sa.DateTime(), nullable=True),
        sa.Column('session_length_minutes', sa.Float(), nullable=True),
        sa.Column('platform', sa.String(length=20), nullable=True),
        sa.Column('os_family', sa.String(length=20), nullable=True),
        sa.Column('country', sa.String(length=2), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['player_id'], ['players.player_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sessions_id'), 'sessions', ['id'], unique=False)
    op.create_index(op.f('ix_sessions_player_id'), 'sessions', ['player_id'], unique=False)

    # Create bets table
    op.create_table('bets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.String(), nullable=True),
        sa.Column('game_name', sa.String(length=100), nullable=False),
        sa.Column('bet_amount', sa.Float(), nullable=False),
        sa.Column('win_amount', sa.Float(), nullable=True),
        sa.Column('bet_timestamp', sa.DateTime(), nullable=True),
        sa.Column('game_category', sa.String(length=50), nullable=True),
        sa.Column('platform', sa.String(length=20), nullable=True),
        sa.Column('os_family', sa.String(length=20), nullable=True),
        sa.Column('country', sa.String(length=2), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['player_id'], ['players.player_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bets_id'), 'bets', ['id'], unique=False)
    op.create_index(op.f('ix_bets_player_id'), 'bets', ['player_id'], unique=False)

    # Create deposits table
    op.create_table('deposits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.String(), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('deposit_timestamp', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['player_id'], ['players.player_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_deposits_id'), 'deposits', ['id'], unique=False)
    op.create_index(op.f('ix_deposits_player_id'), 'deposits', ['player_id'], unique=False)

    # Create withdrawals table
    op.create_table('withdrawals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.String(), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('withdrawal_timestamp', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['player_id'], ['players.player_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_withdrawals_id'), 'withdrawals', ['id'], unique=False)
    op.create_index(op.f('ix_withdrawals_player_id'), 'withdrawals', ['player_id'], unique=False)

    # Create bonuses table
    op.create_table('bonuses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.String(), nullable=True),
        sa.Column('bonus_type', sa.String(length=50), nullable=True),
        sa.Column('bonus_amount', sa.Float(), nullable=False),
        sa.Column('bonus_currency', sa.String(length=3), nullable=True),
        sa.Column('is_redeemed', sa.Boolean(), nullable=True),
        sa.Column('redeemed_at', sa.DateTime(), nullable=True),
        sa.Column('bonus_timestamp', sa.DateTime(), nullable=True),
        sa.Column('campaign_id', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['player_id'], ['players.player_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bonuses_id'), 'bonuses', ['id'], unique=False)
    op.create_index(op.f('ix_bonuses_player_id'), 'bonuses', ['player_id'], unique=False)

    # Create player_features table
    op.create_table('player_features',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.String(), nullable=True),
        sa.Column('feature_date', sa.Date(), nullable=False),
        sa.Column('days_active_last_30', sa.Integer(), nullable=True),
        sa.Column('sessions_last_30', sa.Integer(), nullable=True),
        sa.Column('avg_session_length', sa.Float(), nullable=True),
        sa.Column('days_since_last_login', sa.Integer(), nullable=True),
        sa.Column('total_bets', sa.Integer(), nullable=True),
        sa.Column('total_bet_amount', sa.Float(), nullable=True),
        sa.Column('avg_bet_size', sa.Float(), nullable=True),
        sa.Column('bets_per_session', sa.Float(), nullable=True),
        sa.Column('unique_games_played', sa.Integer(), nullable=True),
        sa.Column('games_played_breakdown', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('total_deposit', sa.Float(), nullable=True),
        sa.Column('total_withdrawal', sa.Float(), nullable=True),
        sa.Column('net_ggr', sa.Float(), nullable=True),
        sa.Column('num_deposit_transactions', sa.Integer(), nullable=True),
        sa.Column('avg_deposit_amount', sa.Float(), nullable=True),
        sa.Column('days_since_first_deposit', sa.Integer(), nullable=True),
        sa.Column('friends_count', sa.Integer(), nullable=True),
        sa.Column('messages_sent', sa.Integer(), nullable=True),
        sa.Column('tournaments_participated', sa.Integer(), nullable=True),
        sa.Column('bonus_used', sa.Boolean(), nullable=True),
        sa.Column('bonus_amount_used', sa.Float(), nullable=True),
        sa.Column('num_offers_received_last_30', sa.Integer(), nullable=True),
        sa.Column('num_offers_redeemed_last_30', sa.Integer(), nullable=True),
        sa.Column('trend_session_count', sa.Float(), nullable=True),
        sa.Column('trend_deposit_amount', sa.Float(), nullable=True),
        sa.Column('time_between_sessions_mean', sa.Float(), nullable=True),
        sa.Column('time_between_sessions_std', sa.Float(), nullable=True),
        sa.Column('churn_label', sa.Boolean(), nullable=True),
        sa.Column('churn_probability', sa.Float(), nullable=True),
        sa.Column('predicted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['player_id'], ['players.player_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_player_features_id'), 'player_features', ['id'], unique=False)
    op.create_index(op.f('ix_player_features_player_id'), 'player_features', ['player_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_player_features_player_id'), table_name='player_features')
    op.drop_index(op.f('ix_player_features_id'), table_name='player_features')
    op.drop_table('player_features')
    op.drop_index(op.f('ix_bonuses_player_id'), table_name='bonuses')
    op.drop_index(op.f('ix_bonuses_id'), table_name='bonuses')
    op.drop_table('bonuses')
    op.drop_index(op.f('ix_withdrawals_player_id'), table_name='withdrawals')
    op.drop_index(op.f('ix_withdrawals_id'), table_name='withdrawals')
    op.drop_table('withdrawals')
    op.drop_index(op.f('ix_deposits_player_id'), table_name='deposits')
    op.drop_index(op.f('ix_deposits_id'), table_name='deposits')
    op.drop_table('deposits')
    op.drop_index(op.f('ix_bets_player_id'), table_name='bets')
    op.drop_index(op.f('ix_bets_id'), table_name='bets')
    op.drop_table('bets')
    op.drop_index(op.f('ix_sessions_player_id'), table_name='sessions')
    op.drop_index(op.f('ix_sessions_id'), table_name='sessions')
    op.drop_table('sessions')
    op.drop_index(op.f('ix_players_player_id'), table_name='players')
    op.drop_table('players')
