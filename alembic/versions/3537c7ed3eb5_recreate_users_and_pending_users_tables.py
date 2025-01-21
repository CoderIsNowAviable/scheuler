"""Recreate users and pending_users tables

Revision ID: 3537c7ed3eb5
Revises: b59f96b52dd1
Create Date: 2025-01-21 22:34:35.584270
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '3537c7ed3eb5'
down_revision: Union[str, None] = 'b59f96b52dd1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('full_name', sa.String(200), nullable=True),
        sa.Column('email', sa.String(255), unique=True, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('is_verified', sa.Boolean, default=False),
        sa.Column('verification_code', sa.String(5), nullable=True),
        sa.Column('profile_photo_url', sa.String(255), nullable=True),
    )
    op.create_table(
        'pending_users',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('email', sa.String(255), unique=True, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(200), nullable=True),
        sa.Column('verification_code', sa.String(5), nullable=True),
        sa.Column('verification_code_expiry', sa.DateTime, nullable=True),
        sa.Column('owner_id', sa.Integer, sa.ForeignKey('users.id'), nullable=True),
    )

def downgrade() -> None:
    op.drop_table('pending_users')
    op.drop_table('users')
