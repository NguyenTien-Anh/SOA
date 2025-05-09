from enum import Enum

class QuestionType(str, Enum):
    SINGLE_CHOICE = "Single Choice"
    MULTIPLE_CHOICE = "Multiple Choice"
    TRUE_FALSE = "True False"