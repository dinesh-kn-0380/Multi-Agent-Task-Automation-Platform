import time
from typing import Dict, List, Optional

class ConversationMemory:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.messages: List[Dict[str, str]] = []
        self.last_updated = time.time()

    def add(self, role: str, content: str, metadata: Optional[Dict] = None):
        msg = {"role": role, "content": content}
        if metadata:
            msg["metadata"] = metadata
        self.messages.append(msg)
        self.last_updated = time.time()

    def get_context(self, limit: int = 10) -> List[Dict[str, str]]:
        # Return last N messages for context
        return self.messages[-limit:]

class MemoryStore:
    def __init__(self):
        self.sessions: Dict[str, ConversationMemory] = {}

    def get_or_create(self, session_id: str) -> ConversationMemory:
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationMemory(session_id)
        return self.sessions[session_id]

    def delete(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

    def session_count(self) -> int:
        return len(self.sessions)

memory_store = MemoryStore()
