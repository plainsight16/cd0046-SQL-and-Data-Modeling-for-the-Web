"""empty message

Revision ID: 3629abd094f7
Revises: 9356267eed57
Create Date: 2022-06-06 13:31:29.122398

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3629abd094f7'
down_revision = '9356267eed57'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'Artist', ['name'])
    op.create_unique_constraint(None, 'Venue', ['name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'Venue', type_='unique')
    op.drop_constraint(None, 'Artist', type_='unique')
    # ### end Alembic commands ###
