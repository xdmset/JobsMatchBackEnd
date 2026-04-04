"""Split premium plans by role

Revision ID: b3c4d5e6f7a8
Revises: a1d4f8b2c3e7
Create Date: 2026-04-04 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b3c4d5e6f7a8"
down_revision: Union[str, Sequence[str], None] = "a1d4f8b2c3e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "planes",
        "codigo",
        existing_type=sa.Enum("mensual", "semestral", "anual", name="codigo_plan_paypal"),
        type_=sa.String(length=64),
        existing_nullable=False,
    )

    op.add_column(
        "planes",
        sa.Column(
            "rol_objetivo",
            sa.Enum("estudiante", "empresa", name="rol_objetivo_plan"),
            nullable=True,
        ),
    )
    op.add_column(
        "planes",
        sa.Column(
            "periodicidad",
            sa.Enum("mensual", "semestral", "anual", name="periodicidad_plan_paypal"),
            nullable=True,
        ),
    )
    op.add_column(
        "suscripciones",
        sa.Column(
            "rol_objetivo",
            sa.Enum("estudiante", "empresa", name="rol_objetivo_suscripcion"),
            nullable=True,
        ),
    )
    op.add_column("suscripciones", sa.Column("codigo_plan", sa.String(length=64), nullable=True))

    op.execute(
        """
        UPDATE planes
        SET periodicidad = codigo,
            rol_objetivo = 'estudiante',
            codigo = CASE codigo
                WHEN 'mensual' THEN 'premium_estudiante_mensual'
                WHEN 'semestral' THEN 'premium_estudiante_semestral'
                WHEN 'anual' THEN 'premium_estudiante_anual'
                ELSE codigo
            END
        """
    )

    op.execute(
        """
        UPDATE suscripciones s
        JOIN usuarios u ON u.id = s.usuario_id
        JOIN roles r ON r.id = u.rol_id
        SET s.rol_objetivo = CASE r.nombre
            WHEN 'empresa' THEN 'empresa'
            ELSE 'estudiante'
        END
        """
    )

    op.execute(
        """
        UPDATE suscripciones
        SET codigo_plan = CASE tipo_plan
            WHEN 'free' THEN CONCAT('free_', rol_objetivo)
            WHEN 'premium' THEN CONCAT('premium_', rol_objetivo)
            ELSE codigo_plan
        END
        """
    )

    op.execute(
        """
        UPDATE suscripciones s
        JOIN planes p ON p.paypal_plan_id = s.paypal_plan_id
        SET s.codigo_plan = p.codigo,
            s.rol_objetivo = p.rol_objetivo
        WHERE s.paypal_plan_id IS NOT NULL
        """
    )

    op.alter_column(
        "planes",
        "rol_objetivo",
        existing_type=sa.Enum("estudiante", "empresa", name="rol_objetivo_plan"),
        nullable=False,
    )
    op.alter_column(
        "planes",
        "periodicidad",
        existing_type=sa.Enum("mensual", "semestral", "anual", name="periodicidad_plan_paypal"),
        nullable=False,
    )
    op.alter_column(
        "suscripciones",
        "rol_objetivo",
        existing_type=sa.Enum("estudiante", "empresa", name="rol_objetivo_suscripcion"),
        nullable=False,
    )


def downgrade() -> None:
    op.drop_column("suscripciones", "codigo_plan")
    op.drop_column("suscripciones", "rol_objetivo")
    op.drop_column("planes", "periodicidad")
    op.drop_column("planes", "rol_objetivo")
    op.alter_column(
        "planes",
        "codigo",
        existing_type=sa.String(length=64),
        type_=sa.Enum("mensual", "semestral", "anual", name="codigo_plan_paypal"),
        existing_nullable=False,
    )
