"""subclassed Query

Revision ID: 4faed277a3bf
Revises: 22ff3d9649ee
Create Date: 2013-08-08 15:50:01.958480

"""

# revision identifiers, used by Alembic.
revision = '4faed277a3bf'
down_revision = '22ff3d9649ee'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('queries', sa.Column('tag_name', sa.String(), nullable=True))
    op.add_column('queries', sa.Column('type', sa.String(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('queries', 'type')
    op.drop_column('queries', 'tag_name')
    ### end Alembic commands ###
