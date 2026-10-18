"""In-memory canvas repository with workspace ownership enforcement."""

from src.domain.models.canvas import CanvasState


class CanvasRepository:
    def __init__(self):
        self._canvases: dict[tuple[str, str], CanvasState] = {}
        self._canvas_owners: dict[str, str] = {}

    async def get(self, workspace_id: str, canvas_id: str) -> CanvasState:
        owner = self._canvas_owners.get(canvas_id)
        if owner is None:
            raise ValueError(f"Canvas {canvas_id} not found")
        if owner != workspace_id:
            raise PermissionError(
                f"Canvas {canvas_id} does not belong to workspace {workspace_id}."
            )

        canvas = self._canvases.get((workspace_id, canvas_id))
        if canvas is None:
            raise ValueError(f"Canvas {canvas_id} not found")
        return canvas.model_copy(deep=True)

    async def save(
        self,
        workspace_id: str,
        canvas_id: str,
        canvas: CanvasState,
    ) -> None:
        owner = self._canvas_owners.get(canvas_id)
        if owner is not None and owner != workspace_id:
            raise PermissionError(
                f"Canvas {canvas_id} does not belong to workspace {workspace_id}."
            )

        self._canvases[(workspace_id, canvas_id)] = canvas.model_copy(deep=True)
        self._canvas_owners[canvas_id] = workspace_id

    async def get_all_canvases(self, workspace_id: str) -> list[CanvasState]:
        return [
            canvas.model_copy(deep=True)
            for (owner_id, _), canvas in self._canvases.items()
            if owner_id == workspace_id
        ]
