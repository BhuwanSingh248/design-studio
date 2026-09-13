from pydantic import BaseModel

class DesignIssue(BaseModel):
    severity: str
    category: str
    description: str

class DesignReview(BaseModel):
    summary: str
    issues: list[DesignIssue]