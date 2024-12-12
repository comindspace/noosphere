from enum import Enum

class ReasoningType(Enum):
    MULTIPLE_CONSTRAINTS = "Multiple constraints"
    POST_PROCESSING = "Post processing"
    NUMERICAL_REASONING = "Numerical reasoning"
    TABULAR_REASONING = "Tabular reasoning"
    TEMPORAL_REASONING = "Temporal reasoning"
