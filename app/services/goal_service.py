"""
LifeOS - Goal Service
Gestion des objectifs personnels, professionnels et financiers avec jalons
"""
from typing import List, Optional
from app.database.connection import db, DatabaseManager
from app.repositories.goal_repository import GoalRepository
from app.models.goal import PersonalGoal, GoalMilestone
from app.core.constants import GOAL_CAT_PERSONAL
from app.core.exceptions import ValidationError, EntityNotFoundError
from app.utils.android_native import android_bridge


class GoalService:
    def __init__(self, db_manager: DatabaseManager = db):
        self.db = db_manager
        self.repo = GoalRepository(db_manager)

    def get_goals(self, category: Optional[str] = None, include_completed: bool = True) -> List[PersonalGoal]:
        return self.repo.get_all(category, include_completed)

    def get_goal(self, goal_id: int) -> PersonalGoal:
        g = self.repo.get_by_id(goal_id)
        if not g:
            raise EntityNotFoundError("Objectif", goal_id)
        return g

    def create_goal(
        self,
        title: str,
        description: str = "",
        category: str = GOAL_CAT_PERSONAL,
        target_date: Optional[str] = None,
        milestone_titles: List[str] = None
    ) -> PersonalGoal:
        if not title or not title.strip():
            raise ValidationError("Le titre de l'objectif est obligatoire.", "title")

        goal = PersonalGoal(
            title=title.strip(),
            description=description,
            category=category,
            target_date=target_date,
            progress_percent=0,
            is_completed=False
        )

        if milestone_titles:
            for m_title in milestone_titles:
                if m_title.strip():
                    goal.milestones.append(GoalMilestone(title=m_title.strip()))

        created = self.repo.create(goal)
        android_bridge.vibrate(30)
        return created

    def add_milestone(self, goal_id: int, title: str, target_date: Optional[str] = None) -> GoalMilestone:
        if not title or not title.strip():
            raise ValidationError("Le titre du jalon est obligatoire.", "title")
        goal = self.get_goal(goal_id)
        ms = GoalMilestone(goal_id=goal_id, title=title.strip(), target_date=target_date)
        created_ms = self.repo.add_milestone(ms)
        self._recompute_goal_progress(goal_id)
        return created_ms

    def toggle_milestone(self, goal_id: int, milestone_id: int, is_completed: bool) -> bool:
        res = self.repo.toggle_milestone(milestone_id, is_completed)
        self._recompute_goal_progress(goal_id)
        android_bridge.vibrate(30)
        return res

    def _recompute_goal_progress(self, goal_id: int):
        goal = self.get_goal(goal_id)
        if not goal.milestones:
            return

        total = len(goal.milestones)
        completed = sum(1 for m in goal.milestones if m.is_completed)
        progress = int((completed / total) * 100) if total > 0 else 0

        goal.progress_percent = progress
        goal.is_completed = (progress == 100)
        self.repo.update(goal)

        if goal.is_completed:
            android_bridge.send_notification("Objectif Atteint ! 🏆", f"Bravo ! Vous avez terminé : {goal.title}")

    def delete_goal(self, goal_id: int) -> bool:
        return self.repo.delete(goal_id)
