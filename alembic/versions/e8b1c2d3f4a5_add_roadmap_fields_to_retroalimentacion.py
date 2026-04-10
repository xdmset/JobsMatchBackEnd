"""add roadmap fields to retroalimentacion

Revision ID: e8b1c2d3f4a5
Revises: b3c4d5e6f7a8
Create Date: 2026-04-07 10:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e8b1c2d3f4a5"
down_revision = "b3c4d5e6f7a8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("retroalimentacion", sa.Column("roadmap_json", sa.JSON(), nullable=True))
    op.add_column(
        "retroalimentacion",
        sa.Column(
            "roadmap_estado",
            sa.String(length=50),
            nullable=False,
            server_default="pendiente",
        ),
    )
    op.add_column("retroalimentacion", sa.Column("roadmap_generado_en", sa.DateTime(timezone=True), nullable=True))
    op.add_column("retroalimentacion", sa.Column("roadmap_error", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("retroalimentacion", "roadmap_error")
    op.drop_column("retroalimentacion", "roadmap_generado_en")
    op.drop_column("retroalimentacion", "roadmap_estado")
    op.drop_column("retroalimentacion", "roadmap_json")
