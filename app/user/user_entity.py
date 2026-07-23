import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum

REPLAY_COOLDOWN = timedelta(hours=12)


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
        phone=None,
        created_at=None,
        last_plays=None,
        email_hash=None,
    ):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.email = email
        self.phone = phone
        self.status = UserStatus(status)
        self.created_at = created_at or datetime.now(timezone.utc)
        self.last_plays = [self._normalize_play(play) for play in last_plays] if last_plays else []
        self.email_hash = email_hash if email_hash is not None else self.hash_email(email)

    @staticmethod
    def hash_email(email):
        if not email:
            return None
        return hashlib.sha256(email.encode("utf-8")).hexdigest()

    @staticmethod
    def _ensure_aware_utc(value):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value

    @classmethod
    def _normalize_play(cls, play):
        if isinstance(play, dict):
            return {"played_at": cls._ensure_aware_utc(play["played_at"]), "won": play.get("won")}
        return {"played_at": cls._ensure_aware_utc(play), "won": None}

    @classmethod
    def create(cls, name, email, phone, status=UserStatus.ACTIVE, id=None):
        if not name:
            raise ValueError("name is required")
        if not email:
            raise ValueError("email is required")
        if not phone:
            raise ValueError("phone is required")
        return cls(id=id, name=name, email=email, phone=phone, status=status)

    @classmethod
    def create_blank(cls, status=UserStatus.ACTIVE, id=None):
        return cls(id=id, status=status)

    def update(self, name=None, email=None, phone=None, status=None, email_hash=None):
        if name is not None:
            if not name:
                raise ValueError("name is required")
            self.name = name
        if email is not None:
            if not email:
                raise ValueError("email is required")
            self.email = email
            self.email_hash = email_hash if email_hash is not None else self.hash_email(email)
        if phone is not None:
            if not phone:
                raise ValueError("phone is required")
            self.phone = phone
        if status is not None:
            self.status = UserStatus(status)

    def register_match_result(self, result):
        if result == "win":
            self.status = UserStatus.COMPLETE
            won = True
        elif result == "lose":
            if self.status != UserStatus.COMPLETE:
                self.status = UserStatus.PLAY_AGAIN
            won = False
        else:
            raise ValueError("result must be 'win' or 'lose'")
        self.last_plays.append({"played_at": datetime.now(timezone.utc), "won": won})

    def last_play_at(self):
        if not self.last_plays:
            return None
        return max(play["played_at"] for play in self.last_plays)

    def can_play(self, cooldown=REPLAY_COOLDOWN):
        last_play_at = self.last_play_at()
        if last_play_at is None:
            return True
        return datetime.now(timezone.utc) - last_play_at >= cooldown

    def mark_play_again(self):
        self.status = UserStatus.PLAY_AGAIN

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "email_hash": self.email_hash,
            "phone": self.phone,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_plays": [
                {"played_at": play["played_at"].isoformat(), "won": play["won"]}
                for play in self.last_plays
            ],
        }
