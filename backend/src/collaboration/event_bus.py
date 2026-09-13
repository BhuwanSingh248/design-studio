"""Redis Pub/Sub canvas event bus for cross-instance sync."""
class CanvasEventBus:
    async def publish_event(self, channel: str, event_data: dict) -> None:
        pass
