"""modified ed_staff table

Revision ID: fc323acf9a17
Revises: be9061c89b96
Create Date: 2023-11-06 13:56:57.877904

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc323acf9a17'
down_revision = 'be9061c89b96'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ed_staff', schema=None) as batch_op:
        batch_op.add_column(sa.Column('displayname', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('initial_creation_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('update_date', sa.DateTime(), nullable=True))
        batch_op.drop_constraint('ed_staff_username_key', type_='unique')
        batch_op.create_unique_constraint(None, ['displayname'])

    with op.batch_alter_table('shift_role_ref', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['role'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('shift_role_ref', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')

    with op.batch_alter_table('ed_staff', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.create_unique_constraint('ed_staff_username_key', ['username'])
        batch_op.drop_column('update_date')
        batch_op.drop_column('initial_creation_date')
        batch_op.drop_column('displayname')

    # ### end Alembic commands ###