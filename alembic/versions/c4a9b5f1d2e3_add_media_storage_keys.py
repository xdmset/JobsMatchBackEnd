"""Add media storage keys

Revision ID: c4a9b5f1d2e3
Revises: 9a2c7d5e4b11
Create Date: 2026-03-09 00:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c4a9b5f1d2e3"
down_revision: Union[str, Sequence[str], None] = "9a2c7d5e4b11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("perfiles_estudiantes", sa.Column("cv_storage_key", sa.String(length=512), nullable=True))
    op.add_column(
        "perfiles_estudiantes",
        sa.Column("foto_perfil_storage_key", sa.String(length=512), nullable=True),
    )
    op.add_column(
        "perfiles_empresas",
        sa.Column("foto_perfil_storage_key", sa.String(length=512), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("perfiles_empresas", "foto_perfil_storage_key")
    op.drop_column("perfiles_estudiantes", "foto_perfil_storage_key")
    op.drop_column("perfiles_estudiantes", "cv_storage_key")
