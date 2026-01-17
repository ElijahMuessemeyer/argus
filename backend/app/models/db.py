"""SQLAlchemy ORM models for database persistence."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    Numeric,
    String,
    Text,
    JSON,
    Index,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class StockUniverse(Base):
    """Stock universe table - tracks which stocks to screen."""

    __tablename__ = "stock_universe"

    symbol = Column(String(10), primary_key=True)
    name = Column(String(255), nullable=False)
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    market_cap = Column(Integer, nullable=True)
    exchange = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SignalRecord(Base):
    """Signals table - stores detected trading signals."""

    __tablename__ = "signals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    symbol = Column(String(10), nullable=False, index=True)
    signal_type = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    details = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_signals_symbol_timestamp", "symbol", "timestamp"),
        Index("ix_signals_type_timestamp", "signal_type", "timestamp"),
    )


class ErrorLog(Base):
    """Error logs table - for debugging and monitoring."""

    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    level = Column(String(10), nullable=False)
    component = Column(String(50), nullable=False, index=True)
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    stack_trace = Column(Text, nullable=True)
