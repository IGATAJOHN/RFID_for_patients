"""initial migrate.

Revision ID: b53f1a5b0044
Revises: 
Create Date: 2023-07-22 05:40:58.868769

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b53f1a5b0044'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('card_entry', schema=None) as batch_op:
        batch_op.add_column(sa.Column('timestamp', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('card_entry', schema=None) as batch_op:
        batch_op.drop_column('timestamp')

    # ### end Alembic commands ###