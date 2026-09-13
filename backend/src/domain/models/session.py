"""Chat session and sliding-window context management."""
from enum import Enum
from pydantic import BaseModel, Field


class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ChatMessage(BaseModel):
    role: Role
    content: str
    name: str | None = None


class ChatSession(BaseModel):
    session_id: str
    workspace_id: str
    messages: list[ChatMessage] = Field(default_factory=list)

    def trim_context(self, max_turns: int = 20) -> list[ChatMessage]:
        """Preserve system message and most recent turns."""
        if len(self.messages) <= max_turns:
            return self.messages
        system_msgs = [m for m in self.messages if m.role == Role.SYSTEM]
        recent_turns = [m for m in self.messages if m.role != Role.SYSTEM][-max_turns:]
        return system_msgs + recent_turns
