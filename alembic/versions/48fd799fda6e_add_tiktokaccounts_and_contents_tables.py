"""Add TikTokAccounts and Contents tables

Revision ID: 48fd799fda6e
Revises: 71d2e5332185
Create Date: 2025-01-31 20:04:10.606259

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '48fd799fda6e'
down_revision: Union[str, None] = '3537c7ed3eb5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
