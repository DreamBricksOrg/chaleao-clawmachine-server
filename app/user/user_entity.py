import uuid
from enum import Enum


class UserStatus(str, Enum):
    ACTIVE = "active"
    FORM = "form"
    PLAY = "play"
    COMPLETE = "complete"


class User:
    def __init__(self, name, email, cpf, status=UserStatus.ACTIVE, id=None):
        if not name:
            raise ValueError("name is required")
        if not email:
            raise ValueError("email is required")
        if not cpf:
            raise ValueError("cpf is required")

        self.id = id or str(uuid.uuid4())
        self.name = name
        self.email = email
        self.cpf = cpf
        self.status = UserStatus(status)

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

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "cpf": self.cpf,
            "status": self.status.value,
        }
