from enum import Enum

class QuestionType(str, Enum):
    SINGLE_CHOICE = "SingleChoice"
    MULTIPLE_CHOICE = "MultipleChoice"
    TRUE_FALSE = "TrueFalse"