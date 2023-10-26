"""Renamed confirmed_at to email_confirmed_at

Revision ID: c0d9222819a0
Revises: 3543f30ca798
Create Date: 2023-10-26 12:43:36.794511

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c0d9222819a0'
down_revision = '3543f30ca798'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'confirmed_at', new_column_name='email_confirmed_at')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
     op.alter_column('user', 'email_confirmed_at', new_column_name='confirmed_at')

    # ### end Alembic commands ###
