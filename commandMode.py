from enum import Enum

class CommandMode(Enum):
    MOVE = 1
    GRIP = 2
    SAVEPOINT = 3
    SETTINGS = 4
    CHANGEMODE = 9