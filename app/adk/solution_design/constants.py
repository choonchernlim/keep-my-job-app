from enum import StrEnum


class Field(StrEnum):
    TIMESTAMP = "timestamp"
    PROBLEM_FILENAME = "problem_filename"
    PROBLEM = "problem"
    ARCHITECTURE_SOLUTION = "architecture_solution"
    CRITICAL_FEEDBACK = "critical_feedback"
