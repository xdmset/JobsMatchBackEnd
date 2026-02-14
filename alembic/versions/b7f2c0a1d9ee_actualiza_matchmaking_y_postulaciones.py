"""Actualiza matchmaking y postulaciones

Revision ID: b7f2c0a1d9ee
Revises: 01cf01c545bd
Create Date: 2026-02-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7f2c0a1d9ee'
down_revision: Union[str, Sequence[str], None] = '01cf01c545bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # New table for company swipes
    op.create_table(
        'interacciones_swipe_empresa',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('empresa_id', sa.Integer(), nullable=False),
        sa.Column('estudiante_id', sa.Integer(), nullable=False),
        sa.Column('vacante_id', sa.Integer(), nullable=False),
        sa.Column('interes_empresa', sa.Boolean(), nullable=False),
        sa.Column('fecha', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['empresa_id'], ['perfiles_empresas.usuario_id']),
        sa.ForeignKeyConstraint(['estudiante_id'], ['perfiles_estudiantes.usuario_id']),
        sa.ForeignKeyConstraint(['vacante_id'], ['vacantes.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('empresa_id', 'estudiante_id', 'vacante_id', name='uq_swipe_empresa_tripleta')
    )
    op.create_index(op.f('ix_interacciones_swipe_empresa_id'), 'interacciones_swipe_empresa', ['id'], unique=False)

    # Unique constraints for existing tables
    op.create_unique_constraint('uq_swipe_estudiante_vacante', 'interacciones_swipe', ['estudiante_id', 'vacante_id'])
    op.create_unique_constraint('uq_match_estudiante_vacante', 'matches', ['estudiante_id', 'vacante_id'])
    op.create_unique_constraint('uq_retro_postulacion', 'retroalimentacion', ['postulacion_id'])

    # Update postulaciones table
    op.add_column('postulaciones', sa.Column('estudiante_id', sa.Integer(), nullable=False))
    op.add_column('postulaciones', sa.Column('vacante_id', sa.Integer(), nullable=False))
    op.add_column('postulaciones', sa.Column('empresa_id', sa.Integer(), nullable=False))
    op.add_column('postulaciones', sa.Column('source', sa.Enum('app_swipe', 'web_apply', name='source_postulacion'), nullable=False))
    op.add_column('postulaciones', sa.Column('fecha_creacion', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))

    op.create_foreign_key('fk_post_estudiante', 'postulaciones', 'perfiles_estudiantes', ['estudiante_id'], ['usuario_id'])
    op.create_foreign_key('fk_post_vacante', 'postulaciones', 'vacantes', ['vacante_id'], ['id'])
    op.create_foreign_key('fk_post_empresa', 'postulaciones', 'perfiles_empresas', ['empresa_id'], ['usuario_id'])

    # Extend estado enum and set defaults for fecha_actualizacion
    op.alter_column(
        'postulaciones',
        'estado',
        existing_type=sa.Enum('enviado', 'visto', 'en_proceso', 'rechazado', name='estado_postulacion'),
        type_=sa.Enum('enviado', 'visto', 'en_proceso', 'rechazado', 'aceptado', name='estado_postulacion'),
        existing_nullable=True,
        server_default='enviado'
    )
    op.alter_column(
        'postulaciones',
        'fecha_actualizacion',
        existing_type=sa.DateTime(timezone=True),
        server_default=sa.text('CURRENT_TIMESTAMP'),
        server_onupdate=sa.text('CURRENT_TIMESTAMP'),
        existing_nullable=True
    )

    # Indexes for performance
    op.create_index('idx_postulaciones_est_vac_estado', 'postulaciones', ['estudiante_id', 'vacante_id', 'estado', 'fecha_actualizacion'], unique=False)
    op.create_index('idx_postulaciones_empresa_estado', 'postulaciones', ['empresa_id', 'estado', 'fecha_actualizacion'], unique=False)
    op.create_index('idx_vacantes_empresa_estado', 'vacantes', ['empresa_id', 'estado'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_vacantes_empresa_estado', table_name='vacantes')
    op.drop_index('idx_postulaciones_empresa_estado', table_name='postulaciones')
    op.drop_index('idx_postulaciones_est_vac_estado', table_name='postulaciones')

    op.alter_column(
        'postulaciones',
        'fecha_actualizacion',
        existing_type=sa.DateTime(timezone=True),
        server_default=None,
        server_onupdate=None,
        existing_nullable=True
    )
    op.alter_column(
        'postulaciones',
        'estado',
        existing_type=sa.Enum('enviado', 'visto', 'en_proceso', 'rechazado', 'aceptado', name='estado_postulacion'),
        type_=sa.Enum('enviado', 'visto', 'en_proceso', 'rechazado', name='estado_postulacion'),
        existing_nullable=True,
        server_default=None
    )

    op.drop_constraint('fk_post_empresa', 'postulaciones', type_='foreignkey')
    op.drop_constraint('fk_post_vacante', 'postulaciones', type_='foreignkey')
    op.drop_constraint('fk_post_estudiante', 'postulaciones', type_='foreignkey')

    op.drop_column('postulaciones', 'fecha_creacion')
    op.drop_column('postulaciones', 'source')
    op.drop_column('postulaciones', 'empresa_id')
    op.drop_column('postulaciones', 'vacante_id')
    op.drop_column('postulaciones', 'estudiante_id')

    op.drop_constraint('uq_retro_postulacion', 'retroalimentacion', type_='unique')
    op.drop_constraint('uq_match_estudiante_vacante', 'matches', type_='unique')
    op.drop_constraint('uq_swipe_estudiante_vacante', 'interacciones_swipe', type_='unique')

    op.drop_index(op.f('ix_interacciones_swipe_empresa_id'), table_name='interacciones_swipe_empresa')
    op.drop_table('interacciones_swipe_empresa')
