"""
LifeOS - Core Exceptions
Exceptions personnalisées pour la gestion centralisée des erreurs
"""

class LifeOSError(Exception):
    """Exception racine pour l'application LifeOS."""
    def __init__(self, message: str, code: str = "GENERIC_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class ValidationError(LifeOSError):
    """Levée lorsqu'une validation de données échoue."""
    def __init__(self, message: str, field: str = None):
        super().__init__(message, code="VALIDATION_ERROR")
        self.field = field


class EntityNotFoundError(LifeOSError):
    """Levée lorsqu'une entité recherchée n'existe pas en base."""
    def __init__(self, entity_name: str, entity_id: any):
        super().__init__(f"{entity_name} avec l'identifiant {entity_id} introuvable.", code="NOT_FOUND")
        self.entity_name = entity_name
        self.entity_id = entity_id


class InsufficientFundsError(LifeOSError):
    """Levée lors d'un solde insuffisant dans un portefeuille."""
    def __init__(self, wallet_name: str, available_amount: int, required_amount: int):
        msg = f"Solde insuffisant dans '{wallet_name}' : disponible {available_amount}, requis {required_amount}."
        super().__init__(msg, code="INSUFFICIENT_FUNDS")
        self.wallet_name = wallet_name
        self.available_amount = available_amount
        self.required_amount = required_amount


class DatabaseError(LifeOSError):
    """Levée lors d'une erreur d'accès ou d'intégrité de la base SQLite."""
    def __init__(self, message: str, original_exception: Exception = None):
        super().__init__(message, code="DATABASE_ERROR")
        self.original_exception = original_exception


class AuthenticationError(LifeOSError):
    """Levée lors d'un échec d'authentification par code PIN."""
    def __init__(self, message: str = "Code PIN incorrect."):
        super().__init__(message, code="AUTH_ERROR")


class BudgetExceededWarning(LifeOSError):
    """Alerte émise lorsqu'un budget est dépassé."""
    def __init__(self, category_name: str, budget_limit: int, current_expense: int):
        msg = f"Alerte Budget : la catégorie '{category_name}' a atteint {current_expense} / {budget_limit}."
        super().__init__(msg, code="BUDGET_EXCEEDED")
        self.category_name = category_name
        self.budget_limit = budget_limit
        self.current_expense = current_expense
