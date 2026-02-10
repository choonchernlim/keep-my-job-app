from enum import StrEnum


class Field(StrEnum):
    TIMESTAMP = "timestamp"
    PROBLEM_FILENAME = "problem_filename"
    PROBLEM = "problem"
    PROPOSED_SOLUTION = "proposed_solution"
    CRITICAL_FEEDBACK = "critical_feedback"
