"""Added report_id to report_file table

Revision ID: be009c2aad48
Revises: 9f50b93cd901
Create Date: 2023-08-28 13:09:05.364047

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'be009c2aad48'
down_revision: Union[str, None] = '9f50b93cd901'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('report_file', sa.Column('report_id', sa.BigInteger(), nullable=False))
    op.create_foreign_key(None, 'report_file', 'report', ['report_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'report_file', type_='foreignkey')
    op.drop_column('report_file', 'report_id')
    # ### end Alembic commands ###
