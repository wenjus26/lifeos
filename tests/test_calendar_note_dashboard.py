"""
Tests pour Calendrier, Notes, Dashboard unifié et Sécurité PIN
"""
import pytest
from app.services.calendar_service import CalendarService
from app.services.note_service import NoteService
from app.services.dashboard_service import DashboardService
from app.services.security_service import SecurityService
from app.services.backup_service import BackupService
from app.services.export_service import ExportService
from app.core.exceptions import ValidationError


def test_calendar_event_validation_and_agenda(temp_db):
    cal_svc = CalendarService(temp_db)

    # Validation ordre des dates
    with pytest.raises(ValidationError):
        cal_svc.create_event(
            title="Réunion",
            start_datetime="2026-11-25T14:00:00",
            end_datetime="2026-11-25T13:00:00"  # Antérieur !
        )

    ev = cal_svc.create_event(
        title="Point d'équipe LifeOS",
        start_datetime="2026-11-25T10:00:00",
        end_datetime="2026-11-25T11:00:00"
    )
    assert ev.id is not None

    agenda = cal_svc.get_daily_agenda("2026-11-25")
    assert len(agenda["events"]) == 1
    assert agenda["events"][0].title == "Point d'équipe LifeOS"


def test_notes_crud_and_search(temp_db):
    note_svc = NoteService(temp_db)
    n1 = note_svc.create_note("Idées Features", "Ajouter synchronisation offline-first et graphiques", "Travail", is_pinned=True)
    n2 = note_svc.create_note("Liste de courses", "Bananes, café, lait", "Personnel")

    # Recherche
    results = note_svc.get_notes(search_query="synchronisation")
    assert len(results) == 1
    assert results[0].id == n1.id

    # Favoris
    assert n1.is_pinned is True
    note_svc.toggle_pin(n1.id)
    assert note_svc.get_note(n1.id).is_pinned is False


def test_dashboard_aggregation(temp_db):
    dash_svc = DashboardService(temp_db)
    data = dash_svc.get_dashboard_data()

    assert "total_balance_cents" in data
    assert "month_income_cents" in data
    assert "month_expense_cents" in data
    assert "budget_consumed_percent" in data
    assert "today_tasks" in data
    assert "today_habits" in data
    assert "productivity_score" in data
    assert 0 <= data["productivity_score"] <= 100


def test_pin_security(temp_db):
    sec = SecurityService(temp_db)
    assert not sec.is_pin_enabled()

    # Définition du code PIN "1234"
    sec.set_pin("1234")
    assert sec.is_pin_enabled()

    # Vérification
    assert sec.verify_pin("1234") is True
    assert sec.verify_pin("9999") is False

    # Désactivation
    assert sec.disable_pin("1234") is True
    assert not sec.is_pin_enabled()


def test_backup_and_restore_cycle(temp_db):
    backup_svc = BackupService(temp_db)
    note_svc = NoteService(temp_db)
    note_svc.create_note("Note Test Sauvegarde", "Contenu persistant")

    # Création backup JSON
    backup_file = backup_svc.create_json_backup()
    assert backup_file is not None

    # Suppression de la note
    notes_before = note_svc.get_notes()
    for n in notes_before:
        note_svc.delete_note(n.id)
    assert len(note_svc.get_notes()) == 0

    # Restauration
    success = backup_svc.restore_from_json(backup_file)
    assert success is True
    restored_notes = note_svc.get_notes()
    assert len(restored_notes) >= 1
    assert any(n.title == "Note Test Sauvegarde" for n in restored_notes)
