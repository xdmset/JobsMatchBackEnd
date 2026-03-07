"""Add FastAPI Users columns to usuarios

Revision ID: e3a9d1f5c7b8
Revises: b7f2c0a1d9ee
Create Date: 2026-02-14 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e3a9d1f5c7b8"
down_revision: Union[str, Sequence[str], None] = "b7f2c0a1d9ee"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("1"), nullable=False),
    )
    op.add_column(
        "usuarios",
        sa.Column("is_superuser", sa.Boolean(), server_default=sa.text("0"), nullable=False),
    )
    op.add_column(
        "usuarios",
        sa.Column("is_verified", sa.Boolean(), server_default=sa.text("0"), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("usuarios", "is_verified")
    op.drop_column("usuarios", "is_superuser")
    op.drop_column("usuarios", "is_active")
