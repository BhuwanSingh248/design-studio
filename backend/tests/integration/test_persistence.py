import asyncio
from src.domain.models.canvas import CanvasState
from src.domain.persistence import StatePersistenceManager


def test_persistence_manager():
    mgr = StatePersistenceManager()
    state = CanvasState()
    version = asyncio.run(mgr.save_canvas_snapshot("c1", state))
    assert version == 1

