from app.totem.session_entity import SessionPhase, TotemSession
from app.user.user_entity import UserStatus


class TotemSessionService:
    """Coordena a sessão do totem (o uuid do QR) com o usuário canônico.

    O totem sempre fala em id de sessão; este serviço resolve qual usuário
    está por trás (novo, do cookie ou do email já cadastrado).
    """

    def __init__(self, session_repository, user_service):
        self.session_repository = session_repository
        self.user_service = user_service

    # --- ciclo de vida da sessão ---

    def create_session(self):
        session = TotemSession()
        self.session_repository.add(session)
        return session

    def _get_or_create_session(self, session_id):
        session = self.session_repository.get_by_id(session_id)
        if session is None:
            session = TotemSession(id=session_id)
            self.session_repository.add(session)
        return session

    def _bind(self, session, user_id, phase):
        session.bind(user_id, phase)
        self.session_repository.update(session)
        return session

    # --- polling do totem (resolvido via sessão) ---

    def start_status(self, session_id):
        session = self.session_repository.get_by_id(session_id)
        if session is None or session.user_id is None:
            return "inactive"
        # bloqueado/concluído: totem continua no QR esperando o próximo válido
        if session.phase in (SessionPhase.CONNECTED, SessionPhase.READY):
            return "active"
        return "inactive"

    def play_status(self, session_id):
        session = self.session_repository.get_by_id(session_id)
        if session is None or session.user_id is None:
            return "inactive"
        if session.phase == SessionPhase.READY:
            return "form"
        if session.phase == SessionPhase.CONNECTED:
            return "active"
        return "inactive"

    def register_match_result(self, session_id, result):
        session = self.session_repository.get_by_id(session_id)
        if session is None or session.user_id is None:
            return None
        user = self.user_service.register_match_result(session.user_id, result)
        if user is None:
            return None
        session.phase = SessionPhase.DONE
        session.touch()
        self.session_repository.update(session)
        return user

    # --- fluxo do formulário (celular) ---

    def enter_form(self, session_id, cookie_user_id):
        """Decide o que acontece quando o celular abre /form/<session_id>.

        Retorna (action, user) com action em {"play", "blocked", "form"}.
        """
        session = self._get_or_create_session(session_id)

        if cookie_user_id:
            cookie_user = self.user_service.get_user(cookie_user_id)
            if cookie_user is not None:
                if cookie_user.can_play():
                    self.user_service.mark_play_again(cookie_user)
                    self._bind(session, cookie_user.id, SessionPhase.READY)
                    return "play", cookie_user
                self._bind(session, cookie_user.id, SessionPhase.BLOCKED)
                return "blocked", cookie_user

        # usuário novo (sem cookie válido): cria/reaproveita um usuário em branco
        user = self.user_service.get_user(session_id)
        if user is None:
            user = self.user_service.create_blank_user(session_id, status=UserStatus.ACTIVE)
        self._bind(session, user.id, SessionPhase.CONNECTED)
        return "form", user

    def complete_form(self, session_id, name, email, phone, email_hash):
        """Conclui o cadastro. Retorna (action, user) com action em
        {"play", "blocked", "form", "not_found"}.
        """
        session = self._get_or_create_session(session_id)

        existing = self.user_service.find_by_email_hash(email_hash)
        if existing is not None and existing.id != session_id:
            if not existing.can_play():
                self._bind(session, existing.id, SessionPhase.BLOCKED)
                return "blocked", existing
            self.user_service.mark_play_again(existing)
            self._bind(session, existing.id, SessionPhase.READY)
            self.user_service.delete_blank_user(session_id)
            return "play", existing

        user = self.user_service.update_user(
            session_id,
            name=name,
            email=email,
            phone=phone,
            status=UserStatus.FORM,
            email_hash=email_hash,
        )
        if user is None:
            return "not_found", None
        self._bind(session, user.id, SessionPhase.READY)
        return "form", user
