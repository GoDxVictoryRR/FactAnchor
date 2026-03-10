"""initial_schema

Revision ID: 0001
Revises: 
Create Date: 2026-02-23 21:55:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('email', sa.Text(), nullable=False),
        sa.Column('hashed_password', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=True),
        sa.Column('is_superuser', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # API Keys table
    op.create_table(
        'api_keys',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('key_hash', sa.Text(), nullable=False),
        sa.Column('label', sa.Text(), nullable=True),
        sa.Column('last_used_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key_hash')
    )

    # Reports table
    op.create_table(
        'reports',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('raw_text', sa.Text(), nullable=False),
        sa.Column('status', sa.Text(), server_default='pending', nullable=False),
        sa.Column('confidence_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('confidence_hash', sa.String(length=16), nullable=True),
        sa.Column('full_hash', sa.String(length=64), nullable=True),
        sa.Column('total_claims', sa.Integer(), server_default='0', nullable=True),
        sa.Column('verified_count', sa.Integer(), server_default='0', nullable=True),
        sa.Column('flagged_count', sa.Integer(), server_default='0', nullable=True),
        sa.Column('uncertain_count', sa.Integer(), server_default='0', nullable=True),
        sa.Column('submitted_by', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['submitted_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Claims table
    op.create_table(
        'claims',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('report_id', sa.UUID(), nullable=False),
        sa.Column('sequence_num', sa.Integer(), nullable=False),
        sa.Column('claim_text', sa.Text(), nullable=False),
        sa.Column('claim_type', sa.Text(), nullable=False),
        sa.Column('entities', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('char_start', sa.Integer(), nullable=True),
        sa.Column('char_end', sa.Integer(), nullable=True),
        sa.Column('status', sa.Text(), server_default='pending', nullable=True),
        sa.Column('db_expected_value', sa.Text(), nullable=True),
        sa.Column('llm_generated_sql', sa.Text(), nullable=True),
        sa.Column('similarity_score', sa.Numeric(precision=4, scale=3), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('verified_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['report_id'], ['reports.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('report_id', 'sequence_num')
    )

    # Indexes
    op.create_index('idx_claims_report_id', 'claims', ['report_id'])
    op.create_index('idx_claims_status', 'claims', ['report_id', 'status'])
    op.create_index('idx_reports_submitted_by', 'reports', ['submitted_by'])
    op.create_index('idx_reports_status', 'reports', ['status', 'created_at'])

def downgrade():
    op.drop_table('claims')
    op.drop_table('reports')
    op.drop_table('api_keys')
    op.drop_table('users')
