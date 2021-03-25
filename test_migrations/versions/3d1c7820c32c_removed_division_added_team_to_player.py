"""removed division, added team to player

Revision ID: 3d1c7820c32c
Revises: 
Create Date: 2021-03-25 14:08:49.712253

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d1c7820c32c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('team',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('abbreviation', sa.String(length=45), nullable=True),
    sa.Column('name', sa.String(length=45), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_team_abbreviation'), 'team', ['abbreviation'], unique=False)
    op.create_index(op.f('ix_team_name'), 'team', ['name'], unique=False)
    op.create_table('player',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('team', sa.Integer(), nullable=True),
    sa.Column('first_name', sa.String(length=45), nullable=True),
    sa.Column('last_name', sa.String(length=45), nullable=True),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.Column('password', sa.String(length=100), nullable=True),
    sa.Column('admin', sa.Boolean(), nullable=True),
    sa.Column('subscribed', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['team'], ['team.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_player_admin'), 'player', ['admin'], unique=False)
    op.create_index(op.f('ix_player_email'), 'player', ['email'], unique=True)
    op.create_index(op.f('ix_player_first_name'), 'player', ['first_name'], unique=False)
    op.create_index(op.f('ix_player_last_name'), 'player', ['last_name'], unique=False)
    op.create_index(op.f('ix_player_subscribed'), 'player', ['subscribed'], unique=False)
    op.create_index(op.f('ix_player_team'), 'player', ['team'], unique=False)
    op.create_table('game',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('player_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('singles', sa.Integer(), nullable=True),
    sa.Column('doubles', sa.Integer(), nullable=True),
    sa.Column('triples', sa.Integer(), nullable=True),
    sa.Column('home_runs', sa.Integer(), nullable=True),
    sa.Column('strikeouts', sa.Integer(), nullable=True),
    sa.Column('outs', sa.Integer(), nullable=True),
    sa.Column('base_on_balls', sa.Integer(), nullable=True),
    sa.Column('hit_by_pitch', sa.Integer(), nullable=True),
    sa.Column('runs_batted_in', sa.Integer(), nullable=True),
    sa.Column('error', sa.Integer(), nullable=True),
    sa.Column('stolen_bases', sa.Integer(), nullable=True),
    sa.Column('caught_stealing', sa.Integer(), nullable=True),
    sa.Column('innings_pitched', sa.Integer(), nullable=True),
    sa.Column('earned_runs', sa.Integer(), nullable=True),
    sa.Column('runs', sa.Integer(), nullable=True),
    sa.Column('pitching_strikeouts', sa.Integer(), nullable=True),
    sa.Column('pitching_base_on_balls', sa.Integer(), nullable=True),
    sa.Column('saves', sa.Integer(), nullable=True),
    sa.Column('blown_saves', sa.Integer(), nullable=True),
    sa.Column('win', sa.Integer(), nullable=True),
    sa.Column('loss', sa.Integer(), nullable=True),
    sa.Column('opponent_id', sa.Integer(), nullable=True),
    sa.Column('captain', sa.Boolean(), nullable=True),
    sa.Column('game_won', sa.Boolean(), nullable=True),
    sa.Column('winner_score', sa.Integer(), nullable=True),
    sa.Column('loser_score', sa.Integer(), nullable=True),
    sa.Column('total_innings', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['opponent_id'], ['player.id'], ),
    sa.ForeignKeyConstraint(['player_id'], ['player.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_game_captain'), 'game', ['captain'], unique=False)
    op.create_index(op.f('ix_game_created_at'), 'game', ['created_at'], unique=False)
    op.create_index(op.f('ix_game_player_id'), 'game', ['player_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_game_player_id'), table_name='game')
    op.drop_index(op.f('ix_game_created_at'), table_name='game')
    op.drop_index(op.f('ix_game_captain'), table_name='game')
    op.drop_table('game')
    op.drop_index(op.f('ix_player_team'), table_name='player')
    op.drop_index(op.f('ix_player_subscribed'), table_name='player')
    op.drop_index(op.f('ix_player_last_name'), table_name='player')
    op.drop_index(op.f('ix_player_first_name'), table_name='player')
    op.drop_index(op.f('ix_player_email'), table_name='player')
    op.drop_index(op.f('ix_player_admin'), table_name='player')
    op.drop_table('player')
    op.drop_index(op.f('ix_team_name'), table_name='team')
    op.drop_index(op.f('ix_team_abbreviation'), table_name='team')
    op.drop_table('team')
    # ### end Alembic commands ###
