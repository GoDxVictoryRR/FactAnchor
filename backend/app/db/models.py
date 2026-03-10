import uuid
from datetime import datetime
from sqlalchemy import (
    Column, Text, Boolean, Integer, Numeric, String,
    ForeignKey, UniqueConstraint, Index, func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    email = Column(Text, unique=True, nullable=False)
    hashed_password = Column(Text, nullable=False)
    is_active = Column(Boolean, server_default="true", default=True)
    is_superuser = Column(Boolean, server_default="false", default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, onupdate=func.now())

    reports = relationship("Report", back_populates="submitter")
    api_keys = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    key_hash = Column(Text, unique=True, nullable=False)
    label = Column(Text, nullable=True)
    last_used_at = Column(TIMESTAMP(timezone=True), nullable=True)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="api_keys")


class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    title = Column(Text, nullable=True)
    raw_text = Column(Text, nullable=False)
    status = Column(Text, server_default="pending", nullable=False)
    confidence_score = Column(Numeric(precision=5, scale=2), nullable=True)
    confidence_hash = Column(String(64), nullable=True)
    full_hash = Column(String(64), nullable=True)
    total_claims = Column(Integer, server_default="0", default=0)
    verified_count = Column(Integer, server_default="0", default=0)
    flagged_count = Column(Integer, server_default="0", default=0)
    uncertain_count = Column(Integer, server_default="0", default=0)
    submitted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, onupdate=func.now())

    submitter = relationship("User", back_populates="reports")
    claims = relationship("Claim", back_populates="report", cascade="all, delete-orphan", order_by="Claim.sequence_num")

    __table_args__ = (
        Index("idx_reports_submitted_by", "submitted_by"),
        Index("idx_reports_status", "status", "created_at"),
    )


class Claim(Base):
    __tablename__ = "claims"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    sequence_num = Column(Integer, nullable=False)
    claim_text = Column(Text, nullable=False)
    claim_type = Column(Text, nullable=False)
    entities = Column(JSONB, nullable=True)
    char_start = Column(Integer, nullable=True)
    char_end = Column(Integer, nullable=True)
    status = Column(Text, server_default="pending", default="pending")
    db_expected_value = Column(Text, nullable=True)
    llm_generated_sql = Column(Text, nullable=True)
    similarity_score = Column(Numeric(precision=4, scale=3), nullable=True)
    error_message = Column(Text, nullable=True)
    verified_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, onupdate=func.now())

    report = relationship("Report", back_populates="claims")

    __table_args__ = (
        UniqueConstraint("report_id", "sequence_num"),
        Index("idx_claims_report_id", "report_id"),
        Index("idx_claims_status", "report_id", "status"),
    )
