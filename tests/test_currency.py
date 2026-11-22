"""
Tests unitaires pour la gestion monétaire et devises (FCFA XOF, etc.)
"""
import pytest
from app.utils.currency import format_currency, parse_currency_input, format_compact_amount


def test_format_currency_xof():
    assert format_currency(500000, "XOF") == "500 000 FCFA"
    assert format_currency(0, "XOF") == "0 FCFA"
    assert format_currency(-15000, "XOF") == "-15 000 FCFA"


def test_format_currency_eur():
    assert format_currency(2550, "EUR") == "25,50 €"
    assert format_currency(100000, "EUR") == "1 000,00 €"


def test_parse_currency_input_xof():
    assert parse_currency_input("50000", "XOF") == 50000
    assert parse_currency_input("50 000", "XOF") == 50000
    assert parse_currency_input(12500, "XOF") == 12500
    assert parse_currency_input("invalid", "XOF") == 0


def test_parse_currency_input_eur():
    assert parse_currency_input("25.50", "EUR") == 2550
    assert parse_currency_input("25,50", "EUR") == 2550
    assert parse_currency_input("100", "EUR") == 10000


def test_format_compact_amount():
    assert format_compact_amount(1500000, "XOF") == "1.5M FCFA"
    assert format_compact_amount(25000, "XOF") == "25k FCFA"
    assert format_compact_amount(500, "XOF") == "500 FCFA"
