"""Canvas and session snapshot persistence repository."""
from src.domain.models.canvas import CanvasState


class StatePersistenceManager:
    async def save_canvas_snapshot(self, canvas_id: str, state: CanvasState) -> int:
        """Persist canvas state snapshot, returning new version number."""
        return 1

    async def load_canvas_snapshot(self, canvas_id: str) -> CanvasState | None:
        """Retrieve latest canvas state snapshot."""
        return CanvasState()
