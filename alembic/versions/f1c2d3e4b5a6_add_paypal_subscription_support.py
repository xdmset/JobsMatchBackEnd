"""Add PayPal subscription support

Revision ID: f1c2d3e4b5a6
Revises: d2f6e7a1c9ab
Create Date: 2026-04-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f1c2d3e4b5a6"
down_revision: Union[str, Sequence[str], None] = "d2f6e7a1c9ab"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    existing_columns = {column["name"] for column in inspector.get_columns("suscripciones")}
    if "origen_pago" not in existing_columns:
        op.add_column(
            "suscripciones",
            sa.Column(
                "origen_pago",
                sa.Enum("manual", "paypal", name="origen_pago_suscripcion"),
                nullable=False,
                server_default="manual",
            ),
        )
    if "paypal_plan_id" not in existing_columns:
        op.add_column("suscripciones", sa.Column("paypal_plan_id", sa.String(length=64), nullable=True))
    if "paypal_subscription_id" not in existing_columns:
        op.add_column(
            "suscripciones",
            sa.Column("paypal_subscription_id", sa.String(length=64), nullable=True),
        )
    if "estado_externo" not in existing_columns:
        op.add_column("suscripciones", sa.Column("estado_externo", sa.String(length=64), nullable=True))
    if "moneda" not in existing_columns:
        op.add_column("suscripciones", sa.Column("moneda", sa.String(length=3), nullable=True))
    if "monto" not in existing_columns:
        op.add_column("suscripciones", sa.Column("monto", sa.Numeric(10, 2), nullable=True))
    if "detalle_externo" not in existing_columns:
        op.add_column("suscripciones", sa.Column("detalle_externo", sa.Text(), nullable=True))

    index_names = {index["name"] for index in inspector.get_indexes("suscripciones")}
    if "ix_suscripciones_paypal_subscription_id" not in index_names:
        op.create_index(
            "ix_suscripciones_paypal_subscription_id",
            "suscripciones",
            ["paypal_subscription_id"],
            unique=True,
        )

    if "planes" not in inspector.get_table_names():
        op.create_table(
            "planes",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column(
                "codigo",
                sa.Enum("mensual", "semestral", "anual", name="codigo_plan_paypal"),
                nullable=False,
            ),
            sa.Column("nombre", sa.String(length=100), nullable=False),
            sa.Column("paypal_product_id", sa.String(length=64), nullable=False),
            sa.Column("paypal_plan_id", sa.String(length=64), nullable=False),
            sa.Column("moneda", sa.String(length=3), nullable=False),
            sa.Column("precio", sa.Numeric(10, 2), nullable=False),
            sa.Column("intervalo_unidad", sa.String(length=16), nullable=False),
            sa.Column("intervalo_conteo", sa.Integer(), nullable=False),
            sa.Column("activo", sa.Boolean(), nullable=False, server_default="1"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("codigo"),
            sa.UniqueConstraint("paypal_plan_id"),
        )
        op.create_index(op.f("ix_planes_id"), "planes", ["id"], unique=False)
        op.create_index(
            op.f("ix_planes_paypal_plan_id"),
            "planes",
            ["paypal_plan_id"],
            unique=True,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "planes" in inspector.get_table_names():
        index_names = {index["name"] for index in inspector.get_indexes("planes")}
        if op.f("ix_planes_paypal_plan_id") in index_names:
            op.drop_index(op.f("ix_planes_paypal_plan_id"), table_name="planes")
        if op.f("ix_planes_id") in index_names:
            op.drop_index(op.f("ix_planes_id"), table_name="planes")
        op.drop_table("planes")

    if "suscripciones" not in inspector.get_table_names():
        return

    index_names = {index["name"] for index in inspector.get_indexes("suscripciones")}
    if "ix_suscripciones_paypal_subscription_id" in index_names:
        op.drop_index("ix_suscripciones_paypal_subscription_id", table_name="suscripciones")

    existing_columns = {column["name"] for column in inspector.get_columns("suscripciones")}
    for column_name in [
        "detalle_externo",
        "monto",
        "moneda",
        "estado_externo",
        "paypal_subscription_id",
        "paypal_plan_id",
        "origen_pago",
    ]:
        if column_name in existing_columns:
            op.drop_column("suscripciones", column_name)
