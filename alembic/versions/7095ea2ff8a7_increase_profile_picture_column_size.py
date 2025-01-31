"""Increase profile_picture column size

Revision ID: 7095ea2ff8a7
Revises: 48fd799fda6e
Create Date: 2025-01-31 22:56:17.040166

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '7095ea2ff8a7'
down_revision: Union[str, None] = '48fd799fda6e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

constraint_name = "tiktok_accounts_ibfk_1"

def upgrade():
    # Drop foreign key constraint first
    op.drop_constraint(constraint_name, "tiktok_accounts", type_="foreignkey")

    # Alter the column type
    op.alter_column("tiktok_accounts", "profile_picture",
                    existing_type=sa.String(255),
                    type_=sa.String(500),
                    nullable=True)

    # Re-add the foreign key constraint
    op.create_foreign_key(constraint_name, "tiktok_accounts", "users", ["user_id"], ["id"])

def downgrade():
    # Drop the foreign key constraint before altering the column
    op.drop_constraint(constraint_name, "tiktok_accounts", type_="foreignkey")

    # Revert the column size
    op.alter_column("tiktok_accounts", "profile_picture",
                    existing_type=sa.String(500),
                    type_=sa.String(255),
                    nullable=True)

    # Re-add the foreign key constraint
    op.create_foreign_key(constraint_name, "tiktok_accounts", "users", ["user_id"], ["id"])
