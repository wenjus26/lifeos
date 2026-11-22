"""
Tests pour le service d'objectifs (GoalService)
"""
import pytest
from app.services.goal_service import GoalService
from app.core.constants import GOAL_CAT_PROFESSIONAL


def test_goal_milestone_progression(temp_db):
    goal_svc = GoalService(temp_db)
    goal = goal_svc.create_goal(
        title="Lancer l'application LifeOS",
        category=GOAL_CAT_PROFESSIONAL,
        target_date="2026-12-31",
        milestone_titles=["Conception", "Développement", "Tests QA", "Déploiement APK"]
    )
    assert len(goal.milestones) == 4
    assert goal.progress_percent == 0
    assert not goal.is_completed

    # Complète 2 jalons sur 4 (50%)
    goal_svc.toggle_milestone(goal.id, goal.milestones[0].id, True)
    goal_svc.toggle_milestone(goal.id, goal.milestones[1].id, True)

    g_half = goal_svc.get_goal(goal.id)
    assert g_half.progress_percent == 50
    assert not g_half.is_completed

    # Complète les 2 derniers jalons (100% -> Objectif terminé)
    goal_svc.toggle_milestone(goal.id, goal.milestones[2].id, True)
    goal_svc.toggle_milestone(goal.id, goal.milestones[3].id, True)

    g_done = goal_svc.get_goal(goal.id)
    assert g_done.progress_percent == 100
    assert g_done.is_completed is True
