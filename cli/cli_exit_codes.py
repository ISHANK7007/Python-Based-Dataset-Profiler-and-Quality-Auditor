from enum import Enum

class ExitCode(Enum):
    SUCCESS = 0
    WARNING = 1
    ERROR = 2
    CRITICAL = 3
    FAILURE = 4
