"""empty message

Revision ID: ca63fffe629f
Revises: 7068fde85053
Create Date: 2021-09-05 13:48:28.009147

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ca63fffe629f'
down_revision = '7068fde85053'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('Gallery_photo_id_fkey', 'Gallery', type_='foreignkey')
    op.drop_column('Gallery', 'photo_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Gallery', sa.Column('photo_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('Gallery_photo_id_fkey', 'Gallery', 'Photo', ['photo_id'], ['id'])
    # ### end Alembic commands ###
