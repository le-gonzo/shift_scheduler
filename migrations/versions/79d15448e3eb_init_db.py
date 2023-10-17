"""init db

Revision ID: 79d15448e3eb
Revises: 
Create Date: 2023-10-12 16:12:09.960813

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '79d15448e3eb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('password', sa.String(length=255), server_default='', nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('confirmed_at', sa.DateTime(), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default='0', nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.drop_table('users')
    op.drop_table('shift_codes')
    op.drop_table('assignments')
    op.drop_table('blocks')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blocks',
    sa.Column('block_name', sa.CHAR(length=50), autoincrement=False, nullable=False, comment='blocks names for unique locations or assigment types.  Prefressing a name with an underscore will result in a hidden label when displayed in shift scheduler'),
    sa.Column('block_id', sa.INTEGER(), sa.Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), autoincrement=True, nullable=False, comment='unique identifier for block'),
    sa.PrimaryKeyConstraint('block_id', name='blocks_pkey'),
    comment='Table `blocks` represents the distinct locations or assignment categories within the shift scheduler web application. Each record captures a unique location or category where an employee can be assigned during a shift. The primary key of this table is referenced in the assignments table, ensuring that every assignment is associated with a valid location or category.',
    postgresql_ignore_search_path=False
    )
    op.create_table('assignments',
    sa.Column('block_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('assignment_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('assignment_name', sa.CHAR(length=60), autoincrement=False, nullable=False),
    sa.Column('assigment_valid_startdate', sa.DATE(), server_default=sa.text("'1970-01-01'::date"), autoincrement=False, nullable=False),
    sa.Column('assigment_valid_enddate', sa.DATE(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['block_id'], ['blocks.block_id'], name='block_id'),
    sa.PrimaryKeyConstraint('assignment_id', name='assignments_pkey'),
    comment='`assignments` table lists all assignments active and inactive along with the block_id assignements should be listed under'
    )
    op.create_table('shift_codes',
    sa.Column('shift_code_id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('shift_name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('shift_start', postgresql.TIME(), autoincrement=False, nullable=True),
    sa.Column('shift_length', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('productive', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('randomize', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('dh12_only', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('shift_code_id', name='shift_codes_pkey')
    )
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('username', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('password', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='users_pkey'),
    sa.UniqueConstraint('username', name='users_username_key')
    )
    op.drop_table('user')
    # ### end Alembic commands ###
