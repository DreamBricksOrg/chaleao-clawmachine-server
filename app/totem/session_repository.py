from app.totem.session_entity import SessionPhase, TotemSession


class TotemSessionRepository:
    def __init__(self, database):
        self.collection = database["totem_sessions"]

    def add(self, session):
        self.collection.insert_one(self._to_document(session))

    def get_by_id(self, session_id):
        document = self.collection.find_one({"_id": session_id})
        if document is None:
            return None
        return self._to_entity(document)

    def update(self, session):
        self.collection.update_one(
            {"_id": session.id},
            {"$set": self._to_document(session, include_id=False)},
        )

    @staticmethod
    def _to_document(session, include_id=True):
        document = {
            "user_id": session.user_id,
            "phase": session.phase.value,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
        }
        if include_id:
            document["_id"] = session.id
        return document

    @staticmethod
    def _to_entity(document):
        return TotemSession(
            id=document["_id"],
            user_id=document.get("user_id"),
            phase=SessionPhase(document["phase"]),
            created_at=document.get("created_at"),
            updated_at=document.get("updated_at"),
        )
