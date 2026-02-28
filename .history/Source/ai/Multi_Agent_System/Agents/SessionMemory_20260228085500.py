import uuid

class SessionMemory:

    def __init__(self):
        self.sessions = {}

    def create_session(self):
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = []
        return session_id

    def get_history(self, session_id):
        return self.sessions.get(session_id, [])

    def add_message(self, session_id, role, content):
        self.sessions.setdefault(session_id, []).append({
            "role": role,
            "content": content
        })