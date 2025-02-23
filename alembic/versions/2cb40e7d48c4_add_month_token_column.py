from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = '2cb40e7d48c4'
down_revision: Union[str, None] = '7095ea2ff8a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    # Check if 'month_token' column exists in the 'users' table
    if 'month_token' not in [column['name'] for column in inspector.get_columns('users')]:
        op.add_column('users', sa.Column('month_token', sa.String(255), nullable=True))

def downgrade():
    op.drop_column('users', 'month_token')
