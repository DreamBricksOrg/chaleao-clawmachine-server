from app.user.user_entity import User, UserStatus


class UserService:
    def __init__(self, repository):
        self.repository = repository

    def create_user(self, name, email, cpf, status=UserStatus.ACTIVE):
        user = User.create(name=name, email=email, cpf=cpf, status=status)
        self.repository.add(user)
        return user

    def create_blank_user(self, user_id, status=UserStatus.ACTIVE):
        user = User.create_blank(id=user_id, status=status)
        self.repository.add(user)
        return user

    def get_user(self, user_id):
        return self.repository.get_by_id(user_id)

    def list_users(self):
        return self.repository.list_all()

    def update_user(self, user_id, name=None, email=None, cpf=None, status=None, email_hash=None):
        user = self.repository.get_by_id(user_id)
        if user is None:
            return None

        user.update(name=name, email=email, cpf=cpf, status=status, email_hash=email_hash)
        self.repository.update(user)
        return user

    def register_match_result(self, user_id, result):
        user = self.repository.get_by_id(user_id)
        if user is None:
            return None

        user.register_match_result(result)
        self.repository.update(user)
        return user
