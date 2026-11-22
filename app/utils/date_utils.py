"""
LifeOS - Date Utilities
Helpers pour la manipulation des dates, calendrier et calcul des séries (streaks)
"""
from datetime import datetime, date, timedelta
from typing import List, Tuple

MOIS_FR = [
    "", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
]

JOURS_FR = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]


def today_str() -> str:
    """Retourne la date du jour au format YYYY-MM-DD."""
    return date.today().isoformat()


def current_month_str() -> str:
    """Retourne le mois courant au format YYYY-MM."""
    return date.today().strftime("%Y-%m")


def now_iso() -> str:
    """Retourne le timestamp ISO actuel."""
    return datetime.now().isoformat()


def format_date_fr(date_str: str) -> str:
    """Formate une date YYYY-MM-DD en français (ex: 22 Nov 2026)."""
    if not date_str:
        return ""
    try:
        parts = date_str.split("T")[0].split("-")
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
        m_name = MOIS_FR[m][:4]
        return f"{d} {m_name} {y}"
    except (ValueError, IndexError):
        return date_str


def format_month_fr(month_str: str) -> str:
    """Formate un mois YYYY-MM en français (ex: Novembre 2026)."""
    if not month_str:
        return ""
    try:
        parts = month_str.split("-")
        y, m = int(parts[0]), int(parts[1])
        return f"{MOIS_FR[m]} {y}"
    except (ValueError, IndexError):
        return month_str


def get_month_date_range(month_str: str) -> Tuple[str, str]:
    """Retourne le premier et dernier jour d'un mois au format YYYY-MM-DD."""
    parts = month_str.split("-")
    y, m = int(parts[0]), int(parts[1])
    start_date = date(y, m, 1)
    if m == 12:
        end_date = date(y + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(y, m + 1, 1) - timedelta(days=1)
    return start_date.isoformat(), end_date.isoformat()


def calculate_streaks(completed_dates: List[str]) -> Tuple[int, int]:
    """
    Calcule la série actuelle (current streak) et la plus longue série (longest streak)
    à partir d'une liste de dates YYYY-MM-DD.
    """
    if not completed_dates:
        return 0, 0

    sorted_dates = sorted(set(completed_dates))
    date_objs = [datetime.strptime(d, "%Y-%m-%d").date() for d in sorted_dates]

    # Plus longue série
    longest_streak = 0
    current_run = 0
    prev_d = None

    for d in date_objs:
        if prev_d is None:
            current_run = 1
        elif d == prev_d + timedelta(days=1):
            current_run += 1
        else:
            current_run = 1
        if current_run > longest_streak:
            longest_streak = current_run
        prev_d = d

    # Série actuelle
    today = date.today()
    yesterday = today - timedelta(days=1)
    date_set = set(date_objs)

    current_streak = 0
    check_day = today if today in date_set else yesterday

    while check_day in date_set:
        current_streak += 1
        check_day -= timedelta(days=1)

    return current_streak, longest_streak
