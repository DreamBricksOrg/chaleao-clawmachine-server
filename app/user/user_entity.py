import uuid
from datetime import datetime, timezone
from enum import Enum


class UserStatus(str, Enum):
    ACTIVE = "active"
    FORM = "form"
    PLAY = "play"
    COMPLETE = "complete"
    PLAY_AGAIN = "play_again"


class User:
    def __init__(
        self,
        status=UserStatus.ACTIVE,
        id=None,
        name=None,
        email=None,
        cpf=None,
        created_at=None,
        last_plays=None,
    ):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.email = email
        self.cpf = cpf
        self.status = UserStatus(status)
        self.created_at = created_at or datetime.now(timezone.utc)
        self.last_plays = list(last_plays) if last_plays else []

    @classmethod
    def create(cls, name, email, cpf, status=UserStatus.ACTIVE, id=None):
        if not name:
            raise ValueError("name is required")
        if not email:
            raise ValueError("email is required")
        if not cpf:
            raise ValueError("cpf is required")
        return cls(id=id, name=name, email=email, cpf=cpf, status=status)

    @classmethod
    def create_blank(cls, status=UserStatus.ACTIVE, id=None):
        return cls(id=id, status=status)

    def update(self, name=None, email=None, cpf=None, status=None):
        if name is not None:
            if not name:
                raise ValueError("name is required")
            self.name = name
        if email is not None:
            if not email:
                raise ValueError("email is required")
            self.email = email
        if cpf is not None:
            if not cpf:
                raise ValueError("cpf is required")
            self.cpf = cpf
        if status is not None:
            self.status = UserStatus(status)

    def register_match_result(self, result):
        if result == "win":
            self.status = UserStatus.COMPLETE
        elif result == "lose":
            self.status = UserStatus.PLAY_AGAIN
        else:
            raise ValueError("result must be 'win' or 'lose'")
        self.last_plays.append(datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "cpf": self.cpf,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_plays": [played_at.isoformat() for played_at in self.last_plays],
        }
