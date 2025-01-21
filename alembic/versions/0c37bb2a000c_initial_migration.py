"""Initial migration

Revision ID: 0c37bb2a000c
Revises: 
Create Date: 2024-12-21 10:58:16.800160

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c37bb2a000c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    # Add the profile_photo_url column to the users table
    op.add_column('users', sa.Column('profile_photo_url', sa.String(), nullable=True, default=None))

    # Add the verification_code_expiry column to the pending_users table
    op.add_column('pending_users', sa.Column('verification_code_expiry', sa.DateTime(), nullable=True))


def downgrade() -> None:
    # Remove the profile_photo_url column from the users table
    op.drop_column('users', 'profile_photo_url')

    # Remove the verification_code_expiry column from the pending_users table
    op.drop_column('pending_users', 'verification_code_expiry')
