"""adding foreign keys

Revision ID: 94d028f1d5ec
Revises: cfcde3da5a0c
Create Date: 2021-03-29 00:02:36.507628

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '94d028f1d5ec'
down_revision = 'cfcde3da5a0c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('player', sa.Column('team_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'player', 'team', ['team_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'player', type_='foreignkey')
    op.drop_column('player', 'team_id')
    # ### end Alembic commands ###
