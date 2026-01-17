"""Pytest configuration and fixtures."""

import pytest
from datetime import datetime, timedelta
from typing import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models.db import Base
from app.models.stock import OHLCV
from app.db.session import get_db


# Test database
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create test database tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create test client with overridden dependencies."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_ohlcv() -> list[OHLCV]:
    """Generate sample OHLCV data for testing."""
    base_date = datetime(2024, 1, 1)
    data = []

    for i in range(300):  # 300 days of data
        date = base_date + timedelta(days=i)
        base_price = 100 + (i * 0.1)  # Slight uptrend

        data.append(OHLCV(
            timestamp=date,
            open=base_price,
            high=base_price + 2,
            low=base_price - 1,
            close=base_price + 1,
            volume=1000000 + (i * 1000),
        ))

    return data


@pytest.fixture
def sample_ohlcv_with_crossover() -> list[OHLCV]:
    """Generate OHLCV data with a MA crossover."""
    base_date = datetime(2024, 1, 1)
    data = []

    # First 150 days: price above MA
    for i in range(150):
        date = base_date + timedelta(days=i)
        base_price = 150

        data.append(OHLCV(
            timestamp=date,
            open=base_price,
            high=base_price + 2,
            low=base_price - 1,
            close=base_price + 1,
            volume=1000000,
        ))

    # Next 50 days: price drops below MA
    for i in range(150, 200):
        date = base_date + timedelta(days=i)
        base_price = 100

        data.append(OHLCV(
            timestamp=date,
            open=base_price,
            high=base_price + 2,
            low=base_price - 1,
            close=base_price + 1,
            volume=1000000,
        ))

    return data
