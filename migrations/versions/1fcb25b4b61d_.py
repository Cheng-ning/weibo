"""empty message

Revision ID: 1fcb25b4b61d
Revises: dca9b31941a3
Create Date: 2020-08-28 09:44:40.376704

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1fcb25b4b61d'
down_revision = 'dca9b31941a3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('article', sa.Column('n_thumb', sa.Integer(), nullable=False))
    op.drop_index('ix_thumb_aid', table_name='thumb')
    op.drop_index('ix_thumb_uid', table_name='thumb')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_thumb_uid', 'thumb', ['uid'], unique=False)
    op.create_index('ix_thumb_aid', 'thumb', ['aid'], unique=False)
    op.drop_column('article', 'n_thumb')
    # ### end Alembic commands ###
