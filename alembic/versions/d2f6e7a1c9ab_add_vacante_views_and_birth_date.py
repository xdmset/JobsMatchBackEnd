"""Add vacancy view history and student birth date

Revision ID: d2f6e7a1c9ab
Revises: c4a9b5f1d2e3
Create Date: 2026-03-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d2f6e7a1c9ab"
down_revision: Union[str, Sequence[str], None] = "c4a9b5f1d2e3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


VIEW_TABLE = "vacantes_visualizaciones"
VIEW_UNIQUE_NAME = "uq_visualizacion_estudiante_vacante"


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    estudiante_columns = {column["name"] for column in inspector.get_columns("perfiles_estudiantes")}
    if "fecha_nacimiento" not in estudiante_columns:
        op.add_column("perfiles_estudiantes", sa.Column("fecha_nacimiento", sa.Date(), nullable=True))

    if VIEW_TABLE not in inspector.get_table_names():
        op.create_table(
            VIEW_TABLE,
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("estudiante_id", sa.Integer(), nullable=False),
            sa.Column("vacante_id", sa.Integer(), nullable=False),
            sa.Column(
                "primera_visualizacion",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.Column(
                "ultima_visualizacion",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.Column("total_visualizaciones", sa.Integer(), server_default="1", nullable=False),
            sa.ForeignKeyConstraint(["estudiante_id"], ["perfiles_estudiantes.usuario_id"]),
            sa.ForeignKeyConstraint(["vacante_id"], ["vacantes.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("estudiante_id", "vacante_id", name=VIEW_UNIQUE_NAME),
        )

    inspector = sa.inspect(bind)
    view_index_names = {index["name"] for index in inspector.get_indexes(VIEW_TABLE)}
    if op.f("ix_vacantes_visualizaciones_id") not in view_index_names:
        op.create_index(op.f("ix_vacantes_visualizaciones_id"), VIEW_TABLE, ["id"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if VIEW_TABLE in inspector.get_table_names():
        index_names = {index["name"] for index in inspector.get_indexes(VIEW_TABLE)}
        if op.f("ix_vacantes_visualizaciones_id") in index_names:
            op.drop_index(op.f("ix_vacantes_visualizaciones_id"), table_name=VIEW_TABLE)
        op.drop_table(VIEW_TABLE)

    estudiante_columns = {column["name"] for column in inspector.get_columns("perfiles_estudiantes")}
    if "fecha_nacimiento" in estudiante_columns:
        op.drop_column("perfiles_estudiantes", "fecha_nacimiento")
