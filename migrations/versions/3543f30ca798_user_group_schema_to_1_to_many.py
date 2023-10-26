""" user-group schema to 1 to many

Revision ID: 3543f30ca798
Revises: 21f83e8be7b8
Create Date: 2023-10-26 11:42:50.000976

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3543f30ca798'
down_revision = '21f83e8be7b8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_roles')
    with op.batch_alter_table('location', schema=None) as batch_op:
        batch_op.add_column(sa.Column('valid_start', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('valid_end', sa.Date(), nullable=True))

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('role_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'role', ['role_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('role_id')

    with op.batch_alter_table('location', schema=None) as batch_op:
        batch_op.drop_column('valid_end')
        batch_op.drop_column('valid_start')

    op.create_table('user_roles',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('role_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], name='user_roles_role_id_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='user_roles_user_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='user_roles_pkey')
    )
    # ### end Alembic commands ###
