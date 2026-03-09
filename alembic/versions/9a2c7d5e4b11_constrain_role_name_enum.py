"""Constrain role name values

Revision ID: 9a2c7d5e4b11
Revises: 8f4b9c2d1a7e
Create Date: 2026-03-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9a2c7d5e4b11"
down_revision: Union[str, Sequence[str], None] = "8f4b9c2d1a7e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ROLE_CHECK_NAME = "nombre_rol"


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    bind.execute(
        sa.text(
            """
            UPDATE roles
            SET nombre = CASE
                WHEN lower(nombre) = 'student' THEN 'estudiante'
                WHEN lower(nombre) = 'company' THEN 'empresa'
                ELSE lower(nombre)
            END
            """
        )
    )

    check_names = {constraint["name"] for constraint in inspector.get_check_constraints("roles")}
    if ROLE_CHECK_NAME not in check_names:
        op.create_check_constraint(
            ROLE_CHECK_NAME,
            "roles",
            "nombre IN ('admin', 'estudiante', 'empresa')",
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    check_names = {constraint["name"] for constraint in inspector.get_check_constraints("roles")}

    if ROLE_CHECK_NAME in check_names:
        op.drop_constraint(ROLE_CHECK_NAME, "roles", type_="check")
