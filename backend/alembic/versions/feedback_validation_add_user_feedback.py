"""Add user feedback table for MVP validation

Revision ID: feedback_validation
Revises: bc1724eaace5
Create Date: 2025-11-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'feedback_validation'
down_revision = 'bc1724eaace5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_feedback table
    op.create_table(
        'user_feedback',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('feature', sa.String(length=100), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('page', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_feedback_user_id'), 'user_feedback', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_feedback_feature'), 'user_feedback', ['feature'], unique=False)
    op.create_index(op.f('ix_user_feedback_created_at'), 'user_feedback', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_feedback_created_at'), table_name='user_feedback')
    op.drop_index(op.f('ix_user_feedback_feature'), table_name='user_feedback')
    op.drop_index(op.f('ix_user_feedback_user_id'), table_name='user_feedback')
    op.drop_table('user_feedback')
