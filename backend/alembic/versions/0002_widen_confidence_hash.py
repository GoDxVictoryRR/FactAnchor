"""widen confidence_hash column to 64 chars

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-19 22:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None

def upgrade():
    # The confidence_hash column was created as VARCHAR(16) but it stores
    # a 64-character SHA-256 hex digest. Widen it to match the model.
    op.alter_column(
        'reports',
        'confidence_hash',
        type_=sa.String(length=64),
        existing_type=sa.String(length=16),
        existing_nullable=True,
    )

def downgrade():
    op.alter_column(
        'reports',
        'confidence_hash',
        type_=sa.String(length=16),
        existing_type=sa.String(length=64),
        existing_nullable=True,
    )
