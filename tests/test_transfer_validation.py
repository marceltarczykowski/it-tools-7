"""
Testy funkcjonalności C: System do sprawdzania przelewów.
"""

import pytest
from src.models import Parameters, Transfer
from src.manager import Manager


@pytest.fixture
def manager():
    return Manager(Parameters())


def test_validate_transfer_valid(manager):
    """Przelew poprawny - brak błędów."""
    transfer = Transfer(
        amount_pln=1500.0,
        date="2024-05-10",
        settlement_year=2024,
        settlement_month=5,
        tenant="tenant-1"
    )
    errors = manager.validate_transfer(transfer)
    assert errors == []


def test_validate_transfer_nonexistent_tenant(manager):
    """Przelew do nieistniejącego najemcy."""
    transfer = Transfer(
        amount_pln=1500.0,
        date="2024-05-10",
        settlement_year=2024,
        settlement_month=5,
        tenant="tenant-999"
    )
    errors = manager.validate_transfer(transfer)
    assert len(errors) > 0


def test_validate_transfer_outside_agreement(manager):
    """Przelew poza okresem umowy (tenant-1: 2024-01-01 do 2024-12-31)."""
    transfer = Transfer(
        amount_pln=1500.0,
        date="2025-01-10",
        settlement_year=2025,
        settlement_month=1,
        tenant="tenant-1"
    )
    errors = manager.validate_transfer(transfer)
    assert len(errors) > 0


def test_validate_all_transfers(manager):
    """Walidacja wszystkich przelewów - zwraca dict {indeks: błędy}."""
    manager.transfers = [
        Transfer(amount_pln=1500.0, date="2024-05-10", settlement_year=2024, settlement_month=5, tenant="tenant-1"),
        Transfer(amount_pln=1400.0, date="2024-06-10", settlement_year=2024, settlement_month=6, tenant="tenant-999"),
    ]
    result = manager.validate_all_transfers()
    assert isinstance(result, dict)
    assert 1 in result
    assert 0 not in result


def test_get_invalid_transfers(manager):
    """Pobiera listę (indeks, transfer, błędy) dla niepoprawnych przelewów."""
    manager.transfers = [
        Transfer(amount_pln=1500.0, date="2024-05-10", settlement_year=2024, settlement_month=5, tenant="tenant-1"),
        Transfer(amount_pln=1400.0, date="2024-06-10", settlement_year=2024, settlement_month=6, tenant="tenant-999"),
    ]
    result = manager.get_invalid_transfers()
    assert len(result) == 1
    assert result[0][0] == 1
    assert isinstance(result[0][2], list)
