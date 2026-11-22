"""
LifeOS - Dashboard Service
Agrégation centralisée des métriques de tous les modules pour le tableau de bord
"""
from typing import Dict, List
from datetime import datetime, date, timedelta
from app.database.connection import db, DatabaseManager
from app.services.finance_service import FinanceService
from app.services.task_service import TaskService
from app.services.habit_service import HabitService
from app.services.goal_service import GoalService
from app.services.calendar_service import CalendarService
from app.utils.date_utils import current_month_str, today_str, now_iso


class DashboardService:
    def __init__(self, db_manager: DatabaseManager = db):
        self.db = db_manager
        self.finance = FinanceService(db_manager)
        self.tasks = TaskService(db_manager)
        self.habits = HabitService(db_manager)
        self.goals = GoalService(db_manager)
        self.calendar = CalendarService(db_manager)

    def get_dashboard_data(self) -> Dict:
        """
        Génère l'état complet du tableau de bord unifié en une seule passe :
        - Solde total
        - Revenus & Dépenses du mois
        - Consommation du budget
        - Tâches prioritaires du jour
        - Habitudes du jour
        - Progression des objectifs actifs
        - Prochains événements (48h)
        - Dernières transactions
        - Score de productivité global
        """
        # 1. Finances
        total_balance = self.finance.get_total_balance_cents()
        month_status = self.finance.get_budget_status()
        report = self.finance.get_monthly_report()
        recent_txs = self.finance.transactions_repo.get_all(limit=5)

        # 2. Tâches
        today_tasks = self.tasks.get_today_tasks()
        task_stats = self.tasks.get_task_stats()

        # 3. Habitudes
        habits_status = self.habits.get_all_habits_with_today_status()
        habits_completed_today = sum(1 for h in habits_status if h["completed_today"])
        total_habits = len(habits_status)

        # 4. Objectifs
        active_goals = self.goals.get_goals(include_completed=False)[:3]

        # 5. Prochains événements (48 heures)
        now_str = now_iso()
        two_days_later = (datetime.now() + timedelta(days=2)).isoformat()
        upcoming_events = self.calendar.get_events(start_date=now_str, end_date=two_days_later)[:4]

        # 6. Score de productivité (combinaison tâches du jour + habitudes du jour)
        points_possible = 0
        points_earned = 0

        # Points tâches
        if today_tasks:
            for t in today_tasks:
                points_possible += 10
                if t.is_completed:
                    points_earned += 10

        # Points habitudes
        if total_habits > 0:
            points_possible += total_habits * 10
            points_earned += habits_completed_today * 10

        productivity_score = int((points_earned / points_possible) * 100) if points_possible > 0 else 100

        return {
            # Finances
            "total_balance_cents": total_balance,
            "month_income_cents": report["income_cents"],
            "month_expense_cents": report["expense_cents"],
            "month_budget_limit_cents": month_status["global_limit_cents"],
            "budget_consumed_percent": month_status["consumed_percent"],
            "is_budget_exceeded": month_status["is_exceeded"],
            "recent_transactions": recent_txs,
            # Tâches
            "today_tasks": today_tasks,
            "pending_tasks_count": len([t for t in today_tasks if not t.is_completed]),
            "task_stats": task_stats,
            # Habitudes
            "today_habits": habits_status,
            "habits_completed_count": habits_completed_today,
            "total_habits_count": total_habits,
            # Objectifs
            "active_goals": active_goals,
            # Agenda
            "upcoming_events": upcoming_events,
            # Score
            "productivity_score": productivity_score
        }
