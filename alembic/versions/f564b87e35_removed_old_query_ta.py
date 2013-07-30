"""removed old query table

Revision ID: f564b87e35
Revises: 3b8142e32b92
Create Date: 2013-07-29 17:11:08.439076

"""

# revision identifiers, used by Alembic.
revision = 'f564b87e35'
down_revision = '3b8142e32b92'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table(u'queries')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table(u'queries',
    sa.Column(u'id', sa.INTEGER(), server_default="nextval('queries_id_seq'::regclass)", nullable=False),
    sa.Column(u'capture_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column(u'query', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column(u'result', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column(u'site_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['capture_id'], [u'captures.id'], name=u'queries_capture_id_fkey'),
    sa.PrimaryKeyConstraint(u'id', name=u'queries_pkey')
    )
    ### end Alembic commands ###
