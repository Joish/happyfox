"""Create email table

Revision ID: 9267a77b40d9
Revises: 
Create Date: 2024-03-01 19:21:26.296185

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '9267a77b40d9'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('emails',
                    sa.Column('id', sa.String(), nullable=False),
                    sa.Column('from_address', sa.String(), nullable=True),
                    sa.Column('to_address', sa.String(), nullable=True),
                    sa.Column('subject', sa.String(), nullable=True),
                    sa.Column('date_received', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('emails')
    # ### end Alembic commands ###