# Question Types
QUESTION_TYPES = [
    "MCQ",
    "True/False",
    "Fill in the Blank",
    "Short Answer",
    "Descriptive",
    "Mixed"
]

# Difficulty Levels
DIFFICULTY_LEVELS = [
    "Easy",
    "Medium",
    "Hard",
    "Mixed"
]

# Question Styles
QUESTION_STYLES = [
    "Normal",
    "Conceptual",
    "Twisted",
    "Scenario-Based",
    "Application-Based",
    "Mixed"
]

# File Types
ALLOWED_FILE_TYPES = ["pdf", "docx", "txt"]

# Quiz Status
QUIZ_STATUS = ["in_progress", "submitted", "timed_out"]

# User Roles
USER_ROLES = ["professor", "student"]

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Quiz Settings
DEFAULT_TIME_LIMIT = 30  # minutes
DEFAULT_PASSING_PERCENTAGE = 60
DEFAULT_MAX_ATTEMPTS = 1

# AI Settings
MAX_QUESTIONS_PER_REQUEST = 50
MIN_QUESTIONS_PER_REQUEST = 1
