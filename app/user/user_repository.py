from app.user.user_entity import User, UserStatus


class UserRepository:
    def __init__(self, database):
        self.collection = database["users"]

    def add(self, user):
        self.collection.insert_one(self._to_document(user))

    def get_by_id(self, user_id):
        document = self.collection.find_one({"_id": user_id})
        if document is None:
            return None
        return self._to_entity(document)

    def list_all(self):
        return [self._to_entity(document) for document in self.collection.find()]

    def update(self, user):
        self.collection.update_one(
            {"_id": user.id},
            {"$set": self._to_document(user, include_id=False)},
        )

    @staticmethod
    def _to_document(user, include_id=True):
        document = {
            "name": user.name,
            "email": user.email,
            "cpf": user.cpf,
            "status": user.status.value,
        }
        if include_id:
            document["_id"] = user.id
        return document

    @staticmethod
    def _to_entity(document):
        return User(
            id=document["_id"],
            name=document["name"],
            email=document["email"],
            cpf=document["cpf"],
            status=UserStatus(document["status"]),
        )
