"""back populating all tables

Revision ID: b9ab0e1bdafe
Revises: 
Create Date: 2021-03-28 23:51:27.971756

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b9ab0e1bdafe'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('player',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('first_name', sa.String(length=45), nullable=True),
    sa.Column('last_name', sa.String(length=45), nullable=True),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.Column('password', sa.String(length=100), nullable=True),
    sa.Column('captain', sa.Boolean(), nullable=True),
    sa.Column('admin', sa.Boolean(), nullable=True),
    sa.Column('subscribed', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('id')
    )
    op.create_table('team',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('abbreviation', sa.String(length=45), nullable=True),
    sa.Column('name', sa.String(length=45), nullable=True),
    sa.Column('wins', sa.Integer(), nullable=True),
    sa.Column('losses', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('game',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('team_winner_id', sa.Integer(), nullable=True),
    sa.Column('team_loser_id', sa.Integer(), nullable=True),
    sa.Column('score_winner', sa.Integer(), nullable=True),
    sa.Column('score_loser', sa.Integer(), nullable=True),
    sa.Column('total_innings', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['team_loser_id'], ['team.id'], ),
    sa.ForeignKeyConstraint(['team_winner_id'], ['team.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('player_game',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('player_id', sa.Integer(), nullable=True),
    sa.Column('game_id', sa.Integer(), nullable=True),
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
    sa.ForeignKeyConstraint(['game_id'], ['game.id'], ),
    sa.ForeignKeyConstraint(['player_id'], ['player.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('player_game')
    op.drop_table('game')
    op.drop_table('team')
    op.drop_table('player')
    # ### end Alembic commands ###