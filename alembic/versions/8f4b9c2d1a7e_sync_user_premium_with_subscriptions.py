"""Sync user premium flag with subscriptions

Revision ID: 8f4b9c2d1a7e
Revises: 7c1e9f4a2b6d
Create Date: 2026-03-08 00:00:01.000000

"""
from datetime import date
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8f4b9c2d1a7e"
down_revision: Union[str, Sequence[str], None] = "7c1e9f4a2b6d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    user_rows = bind.execute(sa.text("SELECT id, es_premium FROM usuarios")).fetchall()
    existing_subscription_user_ids = {
        row[0]
        for row in bind.execute(sa.text("SELECT DISTINCT usuario_id FROM suscripciones")).fetchall()
    }

    today = date.today()
    for user_id, es_premium in user_rows:
        if user_id not in existing_subscription_user_ids:
            tipo_plan = "premium" if es_premium else "free"
            bind.execute(
                sa.text(
                    """
                    INSERT INTO suscripciones (usuario_id, tipo_plan, fecha_inicio, fecha_fin)
                    VALUES (:usuario_id, :tipo_plan, :fecha_inicio, :fecha_fin)
                    """
                ),
                {
                    "usuario_id": user_id,
                    "tipo_plan": tipo_plan,
                    "fecha_inicio": today,
                    "fecha_fin": None,
                },
            )

    premium_user_ids = {
        row[0]
        for row in bind.execute(
            sa.text(
                """
                SELECT DISTINCT usuario_id
                FROM suscripciones
                WHERE tipo_plan = 'premium'
                  AND (fecha_inicio IS NULL OR fecha_inicio <= CURRENT_DATE)
                  AND (fecha_fin IS NULL OR fecha_fin >= CURRENT_DATE)
                """
            )
        ).fetchall()
    }

    for user_id, _ in user_rows:
        bind.execute(
            sa.text("UPDATE usuarios SET es_premium = :es_premium WHERE id = :user_id"),
            {"user_id": user_id, "es_premium": user_id in premium_user_ids},
        )


def downgrade() -> None:
    pass
