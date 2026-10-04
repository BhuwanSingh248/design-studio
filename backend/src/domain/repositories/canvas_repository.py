from src.domain.models.canvas import CanvasState

class CanvasRepository:
    def __init__(self):
        self._canvases: dict[str, CanvasState] = {}
        
    async def get(self,canvas_id:str) ->CanvasState:
        canvas = self._canvases.get(canvas_id)
        if not canvas:
            raise ValueError(f"Canvas {canvas_id} not found")
        return canvas

    async def save(self,canvas_id:str, canvas:CanvasState) ->None:
        self._canvases[canvas_id] = canvas
    
    async def get_all_canvases(self,workspace_id:str) -> list[CanvasState]:
        return [canvas for canvas in self._canvases.values()]
    