"""Initial database setup

Revision ID: 83f61b291922
Revises:
Create Date: 2025-09-16 11:44:01.083413

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "83f61b291922"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
