"""Added end_date nullable on report table

Revision ID: 2e7ab6e06a41
Revises: ec0ea32fb2c8
Create Date: 2023-08-25 16:16:21.702333

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '2e7ab6e06a41'
down_revision: Union[str, None] = 'ec0ea32fb2c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('report', 'end_date',
               existing_type=mysql.DATETIME(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('report', 'end_date',
               existing_type=mysql.DATETIME(),
               nullable=False)
    # ### end Alembic commands ###