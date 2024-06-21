from dataclasses import dataclass
import datetime
import typing as tp


@dataclass
class UserChallenge:
    title: str
    description: str
    owner_id: int
    end_date: datetime.datetime
    username: tp.Optional[str] = None


@dataclass
class ActiveChallenge:
    active_challenge_id: int
    owner_id: int
    owner_username: str
    challenge_id: int
    end_date: datetime.datetime
    title: str


@dataclass
class ActiveChallengeParticipant:
    user_id: int
    challenge_id: int


class ChatTypes(tp.NamedTuple):
    PRIVATE = "private"
    GROUP = "group"
    SUPERGROUP = "supergroup"
    CHANNEL = "channel"


