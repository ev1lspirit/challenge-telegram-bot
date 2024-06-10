from dataclasses import dataclass
import datetime
from typing import NamedTuple


@dataclass
class UserChallenge:
    title: str
    description: str
    owner_id: int
    end_date: datetime.datetime

class ChatTypes(NamedTuple):
    PRIVATE = "private"
    GROUP = "group"
    SUPERGROUP = "supergroup"
    CHANNEL = "channel"


