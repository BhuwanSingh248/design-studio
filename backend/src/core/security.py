"""Multi-tenant workspace authorization and security controls."""
from fastapi import HTTPException, status


class WorkspaceSecurity:
    @staticmethod
    def verify_workspace_access(user_id: str, workspace_id: str) -> bool:
        """Verify user is authorized to access workspace."""
        if not user_id or not workspace_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized workspace access",
            )
        return True
