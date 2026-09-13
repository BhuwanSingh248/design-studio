"""Operational ordering and Last-Write-Wins conflict resolution."""
class ConflictResolver:
    @staticmethod
    def resolve_edit(incoming_version: int, current_version: int) -> bool:
        return incoming_version >= current_version
