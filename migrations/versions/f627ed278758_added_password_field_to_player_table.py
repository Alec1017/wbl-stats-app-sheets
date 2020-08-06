"""added password field to player table

Revision ID: f627ed278758
Revises: dcec842f1982
Create Date: 2020-08-05 16:04:47.337747

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f627ed278758'
down_revision = 'dcec842f1982'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('player', sa.Column('password', sa.String(length=100), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('player', 'password')
    # ### end Alembic commands ###
