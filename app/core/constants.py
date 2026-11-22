"""
LifeOS - Core Constants
Constantes globales du système LifeOS
"""

# Devises supportées
DEFAULT_CURRENCY = "XOF"  # Franc CFA BCEAO (devise principale)
SUPPORTED_CURRENCIES = {
    "XOF": {"name": "Franc CFA (XOF)", "symbol": "FCFA", "decimals": 0},
    "EUR": {"name": "Euro", "symbol": "€", "decimals": 2},
    "USD": {"name": "Dollar Américain", "symbol": "$", "decimals": 2},
    "CAD": {"name": "Dollar Canadien", "symbol": "CA$", "decimals": 2},
    "GBP": {"name": "Livre Sterling", "symbol": "£", "decimals": 2},
}

# Types de transactions financières
TX_INCOME = "income"
TX_EXPENSE = "expense"
TX_TRANSFER = "transfer"
TX_TYPES = [TX_INCOME, TX_EXPENSE, TX_TRANSFER]

# Types de portefeuilles
WALLET_CASH = "cash"
WALLET_BANK = "bank"
WALLET_MOBILE_MONEY = "mobile_money"  # Wave, Orange Money, MTN MoMo
WALLET_SAVINGS = "savings"
WALLET_TYPES = [WALLET_CASH, WALLET_BANK, WALLET_MOBILE_MONEY, WALLET_SAVINGS]

# Types de dettes / créances
DEBT_OWED_BY_ME = "debt"         # Dette : argent que je dois
DEBT_OWED_TO_ME = "receivable"   # Créance : argent qu'on me doit
DEBT_TYPES = [DEBT_OWED_BY_ME, DEBT_OWED_TO_ME]

DEBT_STATUS_PENDING = "pending"
DEBT_STATUS_PARTIAL = "partial"
DEBT_STATUS_PAID = "paid"
DEBT_STATUSES = [DEBT_STATUS_PENDING, DEBT_STATUS_PARTIAL, DEBT_STATUS_PAID]

# Priorités des tâches
PRIORITY_LOW = "low"
PRIORITY_MEDIUM = "medium"
PRIORITY_HIGH = "high"
PRIORITY_URGENT = "urgent"
TASK_PRIORITIES = [PRIORITY_LOW, PRIORITY_MEDIUM, PRIORITY_HIGH, PRIORITY_URGENT]

# Statuts des tâches
TASK_STATUS_TODO = "todo"
TASK_STATUS_IN_PROGRESS = "in_progress"
TASK_STATUS_COMPLETED = "completed"
TASK_STATUS_ARCHIVED = "archived"
TASK_STATUSES = [TASK_STATUS_TODO, TASK_STATUS_IN_PROGRESS, TASK_STATUS_COMPLETED, TASK_STATUS_ARCHIVED]

# Fréquences des habitudes et tâches récurrentes
FREQ_NONE = "none"
FREQ_DAILY = "daily"
FREQ_WEEKDAYS = "weekdays"
FREQ_WEEKENDS = "weekends"
FREQ_WEEKLY = "weekly"
FREQ_MONTHLY = "monthly"

# Catégories d'objectifs
GOAL_CAT_PERSONAL = "personal"
GOAL_CAT_PROFESSIONAL = "professional"
GOAL_CAT_FINANCIAL = "financial"
GOAL_CATEGORIES = [GOAL_CAT_PERSONAL, GOAL_CAT_PROFESSIONAL, GOAL_CAT_FINANCIAL]

# Types d'événements de calendrier
EVENT_TYPE_APPOINTMENT = "appointment"
EVENT_TYPE_EVENT = "event"
EVENT_TYPE_REMINDER = "reminder"
EVENT_TYPE_DEADLINE = "deadline"
EVENT_TYPES = [EVENT_TYPE_APPOINTMENT, EVENT_TYPE_EVENT, EVENT_TYPE_REMINDER, EVENT_TYPE_DEADLINE]

# Thèmes d'affichage
THEME_DARK = "dark"
THEME_LIGHT = "light"
THEME_SYSTEM = "system"

# Catégories par défaut
DEFAULT_CATEGORIES = [
    # Dépenses
    {"name": "Alimentation", "type": TX_EXPENSE, "icon": "food", "color": "#FF7043"},
    {"name": "Transport", "type": TX_EXPENSE, "icon": "car", "color": "#42A5F5"},
    {"name": "Logement & Factures", "type": TX_EXPENSE, "icon": "home", "color": "#7E57C2"},
    {"name": "Santé & Bien-être", "type": TX_EXPENSE, "icon": "medical-bag", "color": "#26A69A"},
    {"name": "Loisirs & Sorties", "type": TX_EXPENSE, "icon": "movie", "color": "#EC407A"},
    {"name": "Éducation", "type": TX_EXPENSE, "icon": "school", "color": "#5C6BC0"},
    {"name": "Famille & Cadeaux", "type": TX_EXPENSE, "icon": "gift", "color": "#AB47BC"},
    {"name": "Shopping", "type": TX_EXPENSE, "icon": "shopping", "color": "#FFA726"},
    {"name": "Autre dépense", "type": TX_EXPENSE, "icon": "dots-horizontal", "color": "#78909C"},
    # Revenus
    {"name": "Salaire", "type": TX_INCOME, "icon": "cash-multiple", "color": "#66BB6A"},
    {"name": "Business & Freelance", "type": TX_INCOME, "icon": "briefcase", "color": "#26C6DA"},
    {"name": "Investissements", "type": TX_INCOME, "icon": "chart-line", "color": "#9CCC65"},
    {"name": "Cadeau reçu", "type": TX_INCOME, "icon": "gift-outline", "color": "#D4E157"},
    {"name": "Autre revenu", "type": TX_INCOME, "icon": "plus-circle", "color": "#8D6E63"},
]
