"""add notificaciones table

Revision ID: g1h2i3j4k5l6
Revises: e8b1c2d3f4a5
Create Date: 2026-04-15 10:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "g1h2i3j4k5l6"
down_revision = "e8b1c2d3f4a5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notificaciones",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column(
            "tipo",
            sa.Enum("like_recibido", "match", "postulacion_estado", name="tipo_notificacion"),
            nullable=False,
        ),
        sa.Column("titulo", sa.String(length=255), nullable=False),
        sa.Column("mensaje", sa.Text(), nullable=False),
        sa.Column("vacante_id", sa.Integer(), nullable=True),
        sa.Column("postulacion_id", sa.Integer(), nullable=True),
        sa.Column("estudiante_id", sa.Integer(), nullable=True),
        sa.Column("leida", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("fecha_creacion", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("fecha_leida", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["vacante_id"], ["vacantes.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["postulacion_id"], ["postulaciones.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["estudiante_id"], ["perfiles_estudiantes.usuario_id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notificaciones_id"), "notificaciones", ["id"], unique=False)
    op.create_index(op.f("ix_notificaciones_usuario_id"), "notificaciones", ["usuario_id"], unique=False)
    op.create_index(op.f("ix_notificaciones_leida"), "notificaciones", ["leida"], unique=False)
    op.create_index(op.f("ix_notificaciones_fecha_creacion"), "notificaciones", ["fecha_creacion"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_notificaciones_fecha_creacion"), table_name="notificaciones")
    op.drop_index(op.f("ix_notificaciones_leida"), table_name="notificaciones")
    op.drop_index(op.f("ix_notificaciones_usuario_id"), table_name="notificaciones")
    op.drop_index(op.f("ix_notificaciones_id"), table_name="notificaciones")
    op.drop_table("notificaciones")
    op.execute("DROP TYPE IF EXISTS tipo_notificacion")
