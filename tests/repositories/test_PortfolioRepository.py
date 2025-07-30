import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from repositories.portfolio_repository import PortfolioRepository
from models.portfolio import Portfolio


@pytest.fixture
def mock_db_session():
    with patch("services.db.db.DB.get_connection") as mock_get_connection:
        mock_session = MagicMock()
        context_manager = MagicMock()
        context_manager.__enter__.return_value = mock_session
        mock_get_connection.return_value = context_manager
        yield mock_session


def test_create_success(mock_db_session):
    repo = PortfolioRepository()
    mock_portfolio = Portfolio(user_id=1, title="New Portfolio", content=[], uuid="test-uuid")
    
    def refresh_side_effect(portfolio):
        portfolio.uuid = "test-uuid"
    mock_db_session.refresh.side_effect = refresh_side_effect

    result = repo.create(user_id=1)

    assert result.uuid == "test-uuid"
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called()


def test_create_retry_on_integrity_error(mock_db_session):
    repo = PortfolioRepository()

    call_count = {"count": 0}

    def side_effect_add(portfolio):
        if call_count["count"] == 0:
            call_count["count"] += 1
            raise IntegrityError("duplicate", {}, None)

    def refresh_side_effect(portfolio):
        portfolio.uuid = "test-uuid"

    mock_db_session.add.side_effect = side_effect_add
    mock_db_session.commit.side_effect = [None, None]
    mock_db_session.refresh.side_effect = refresh_side_effect

    result = repo.create(user_id=1)
    assert result.uuid == "test-uuid"


def test_get_by_uuid_found(mock_db_session):
    repo = PortfolioRepository()
    portfolio = Portfolio(uuid="abc123", user_id=1, title="Test", content=[])
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = portfolio

    result = repo.get_by_uuid("abc123")

    assert result == portfolio


def test_get_by_uuid_not_found(mock_db_session):
    repo = PortfolioRepository()
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None

    with pytest.raises(HTTPException) as exc:
        repo.get_by_uuid("invalid")
    assert exc.value.status_code == 404


def test_update_success(mock_db_session):
    repo = PortfolioRepository()
    portfolio = Portfolio(uuid="abc123", user_id=1, title="Old", content=[])
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = portfolio

    update_data = MagicMock()
    update_data.dict.return_value = {"title": "Updated"}

    result = repo.update("abc123", update_data)

    assert result.title == "Updated"
    mock_db_session.commit.assert_called_once()


def test_update_not_found(mock_db_session):
    repo = PortfolioRepository()
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None

    with pytest.raises(HTTPException) as exc:
        repo.update("missing", MagicMock())
    assert exc.value.status_code == 404


def test_delete_success(mock_db_session):
    repo = PortfolioRepository()

    repo.delete("abc123")

    mock_db_session.execute.assert_called_once()
    mock_db_session.commit.assert_called_once()


def test_delete_raises_500_on_exception(mock_db_session):
    repo = PortfolioRepository()
    mock_db_session.execute.side_effect = Exception("DB error")

    with pytest.raises(HTTPException) as exc:
        repo.delete("abc123")
    assert exc.value.status_code == 500


def test_create_retries_and_changes_uuid_on_integrity_error(mock_db_session, monkeypatch):
    repo = PortfolioRepository()
    uuids = ["uuid1", "uuid2"]

    def fake_ulid():
        return uuids.pop(0)
    
    monkeypatch.setattr("repositories.portfolio_repository.ulid", fake_ulid)

    call_count = {"count": 0}
    def side_effect_add(portfolio):
        if call_count["count"] == 0:
            call_count["count"] += 1
            raise IntegrityError("duplicate", {}, None)
        else:
            # On second call, succeed
            portfolio.uuid = "uuid2"

    mock_db_session.add.side_effect = side_effect_add
    mock_db_session.commit.side_effect = [None, None]

    result = repo.create(user_id=1)
    assert result.uuid == "uuid2"