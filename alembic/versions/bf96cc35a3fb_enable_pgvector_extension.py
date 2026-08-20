"""enable pgvector extension

Revision ID: bf96cc35a3fb
Revises: e9b48e90b3cb
Create Date: 2026-08-20 09:54:52.633904

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bf96cc35a3fb'
down_revision: Union[str, Sequence[str], None] = 'e9b48e90b3cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
