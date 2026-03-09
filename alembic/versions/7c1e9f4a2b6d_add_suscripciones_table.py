"""Add suscripciones table

Revision ID: 7c1e9f4a2b6d
Revises: e3a9d1f5c7b8
Create Date: 2026-03-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7c1e9f4a2b6d"
down_revision: Union[str, Sequence[str], None] = "e3a9d1f5c7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "suscripciones" not in inspector.get_table_names():
        op.create_table(
            "suscripciones",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("usuario_id", sa.Integer(), nullable=False),
            sa.Column(
                "tipo_plan",
                sa.Enum("free", "premium", name="tipo_plan_suscripcion"),
                nullable=False,
            ),
            sa.Column("fecha_inicio", sa.Date(), nullable=True),
            sa.Column("fecha_fin", sa.Date(), nullable=True),
            sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )

    index_names = {index["name"] for index in inspector.get_indexes("suscripciones")}
    if op.f("ix_suscripciones_id") not in index_names:
        op.create_index(op.f("ix_suscripciones_id"), "suscripciones", ["id"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "suscripciones" not in inspector.get_table_names():
        return

    index_names = {index["name"] for index in inspector.get_indexes("suscripciones")}
    if op.f("ix_suscripciones_id") in index_names:
        op.drop_index(op.f("ix_suscripciones_id"), table_name="suscripciones")

    op.drop_table("suscripciones")
