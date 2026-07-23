import uuid
from datetime import datetime, timezone
from enum import Enum


class SessionPhase(str, Enum):
    WAITING = "waiting"      # sessão criada, nenhum usuário vinculado
    CONNECTED = "connected"  # usuário vinculado, preenchendo o formulário
    READY = "ready"          # pronto para jogar (form completo ou retornante elegível)
    BLOCKED = "blocked"      # usuário vinculado, mas ainda no cooldown de 12h
    DONE = "done"            # partida registrada


class TotemSession:
    def __init__(self, id=None, user_id=None, phase=SessionPhase.WAITING, created_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.phase = SessionPhase(phase)
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or self.created_at

    def bind(self, user_id, phase):
        self.user_id = user_id
        self.phase = SessionPhase(phase)
        self.touch()

    def touch(self):
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "phase": self.phase.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
