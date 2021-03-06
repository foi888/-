"""empty message

Revision ID: 6657b5df8f5f
Revises: 9f888a8ecb4d
Create Date: 2022-03-19 16:19:45.191553

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6657b5df8f5f'
down_revision = '9f888a8ecb4d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('likes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('post', sa.Column('likes_count', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('post', 'likes_count')
    op.drop_table('likes')
    # ### end Alembic commands ###
