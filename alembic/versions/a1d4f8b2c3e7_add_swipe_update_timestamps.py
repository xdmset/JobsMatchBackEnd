"""Add swipe update timestamps

Revision ID: a1d4f8b2c3e7
Revises: 8f4b9c2d1a7e
Create Date: 2026-04-03 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "a1d4f8b2c3e7"
down_revision: Union[str, Sequence[str], None] = "f1c2d3e4b5a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    swipe_columns = {column["name"] for column in inspector.get_columns("interacciones_swipe")}
    if "fecha_actualizacion" not in swipe_columns:
        op.add_column(
            "interacciones_swipe",
            sa.Column(
                "fecha_actualizacion",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=True,
            ),
        )

    empresa_swipe_columns = {
        column["name"] for column in inspector.get_columns("interacciones_swipe_empresa")
    }
    if "fecha_actualizacion" not in empresa_swipe_columns:
        op.add_column(
            "interacciones_swipe_empresa",
            sa.Column(
                "fecha_actualizacion",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=True,
            ),
        )

    op.execute(
        "UPDATE interacciones_swipe "
        "SET fecha_actualizacion = COALESCE(fecha_actualizacion, fecha)"
    )
    op.execute(
        "UPDATE interacciones_swipe_empresa "
        "SET fecha_actualizacion = COALESCE(fecha_actualizacion, fecha)"
    )

    op.alter_column(
        "interacciones_swipe",
        "fecha_actualizacion",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )
    op.alter_column(
        "interacciones_swipe_empresa",
        "fecha_actualizacion",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    empresa_swipe_columns = {
        column["name"] for column in inspector.get_columns("interacciones_swipe_empresa")
    }
    if "fecha_actualizacion" in empresa_swipe_columns:
        op.drop_column("interacciones_swipe_empresa", "fecha_actualizacion")

    swipe_columns = {column["name"] for column in inspector.get_columns("interacciones_swipe")}
    if "fecha_actualizacion" in swipe_columns:
        op.drop_column("interacciones_swipe", "fecha_actualizacion")
