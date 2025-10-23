from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

class GameStatus(Enum):
    STARTED = "started"
    ABORTED = "aborted"
    MATE = "mate"
    RESIGN = "resign"
    DRAW = "draw"

@dataclass
class GameState:
    moves: str
    wtime: float   # white time remaining in seconds
    btime: float   # black time remaining in seconds
    lastMove: str
    turn: str
    status: GameStatus



@dataclass
class GameInfo:
    gameid: str
    initialPosition: str
    wuser: str
    buser: str
    wrate: str
    brate: str
    wremote: bool
    bremote: bool


@dataclass
class BoardSync:
    aMove: str
    color: str


@dataclass
class CreateGameData:
    time_control: str
    minutes: int
    increment: int
    mode: str
    opponent: str
    username: str
    stockfish_level: int
