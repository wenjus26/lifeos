"""
LifeOS - Currency Utility
Gestion précise des montants sans perte de précision flottante.
Devise principale : FCFA (XOF).
"""
from typing import Union
from app.core.constants import DEFAULT_CURRENCY, SUPPORTED_CURRENCIES


def format_currency(amount_cents: Union[int, str], currency: str = DEFAULT_CURRENCY) -> str:
    """
    Formate un montant entier en devise lisible.
    Exemples :
      - 500000 XOF -> "500 000 FCFA"
      - 2550 EUR (25.50€) -> "25,50 €"
    """
    try:
        amount_int = int(amount_cents)
    except (ValueError, TypeError):
        amount_int = 0

    curr_info = SUPPORTED_CURRENCIES.get(currency, SUPPORTED_CURRENCIES[DEFAULT_CURRENCY])
    decimals = curr_info.get("decimals", 0)
    symbol = curr_info.get("symbol", "FCFA")

    if decimals == 0:
        # Devise sans décimales (ex: FCFA / XOF)
        formatted_num = f"{amount_int:,}".replace(",", " ")
        return f"{formatted_num} {symbol}"
    else:
        # Devise à décimales (ex: EUR, USD)
        units = amount_int // (10 ** decimals)
        cents = abs(amount_int) % (10 ** decimals)
        formatted_units = f"{units:,}".replace(",", " ")
        cents_str = str(cents).zfill(decimals)
        return f"{formatted_units},{cents_str} {symbol}"


def parse_currency_input(value: Union[str, int, float], currency: str = DEFAULT_CURRENCY) -> int:
    """
    Convertit une chaîne saisie par l'utilisateur en entier stockable.
    Exemples :
      - "5000" ou "5 000" XOF -> 5000
      - "25.50" EUR -> 2550
    """
    if isinstance(value, int):
        return value

    if isinstance(value, float):
        # Conversion prudente via string pour éviter l'imprécision float
        str_val = f"{value:.2f}"
    else:
        str_val = str(value).strip().replace(" ", "").replace(",", ".")

    if not str_val:
        return 0

    curr_info = SUPPORTED_CURRENCIES.get(currency, SUPPORTED_CURRENCIES[DEFAULT_CURRENCY])
    decimals = curr_info.get("decimals", 0)

    try:
        if decimals == 0:
            # Traite comme entier direct
            if "." in str_val:
                str_val = str_val.split(".")[0]
            return int(str_val)
        else:
            if "." in str_val:
                parts = str_val.split(".")
                units = int(parts[0]) if parts[0] else 0
                cents_part = parts[1][:decimals].ljust(decimals, "0")
                cents = int(cents_part)
                sign = -1 if units < 0 or str_val.startswith("-") else 1
                return sign * (abs(units) * (10 ** decimals) + cents)
            else:
                return int(str_val) * (10 ** decimals)
    except ValueError:
        return 0


def format_compact_amount(amount_cents: int, currency: str = DEFAULT_CURRENCY) -> str:
    """
    Format compact pour affichage dans les graphiques ou en-têtes (ex: 1.5M FCFA, 250k FCFA).
    """
    abs_amt = abs(amount_cents)
    sign = "-" if amount_cents < 0 else ""
    curr_info = SUPPORTED_CURRENCIES.get(currency, SUPPORTED_CURRENCIES[DEFAULT_CURRENCY])
    symbol = curr_info.get("symbol", "FCFA")

    if abs_amt >= 1_000_000_000:
        val = abs_amt / 1_000_000_000
        return f"{sign}{val:.1f}B {symbol}"
    elif abs_amt >= 1_000_000:
        val = abs_amt / 1_000_000
        return f"{sign}{val:.1f}M {symbol}"
    elif abs_amt >= 10_000:
        val = abs_amt / 1_000
        return f"{sign}{val:.0f}k {symbol}"
    else:
        return format_currency(amount_cents, currency)
