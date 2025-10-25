from pydantic import BaseModel, Field

class GetEmpStatusRequest(BaseModel):
    NationalNumber: str = Field(min_length=1)

class UserOut(BaseModel):
    username: str
    nationalNumber: str
    email: str
    phone: str | None
    isActive: bool

class MetricsOut(BaseModel):
    count: int
    sum: float
    sumAfterTax: float
    average: float
    averageAfterTax: float
    highest: float

class GetEmpStatusResponse(BaseModel):
    user: UserOut
    metrics: MetricsOut
    status: str
    lastUpdatedUtc: str

class ErrorOut(BaseModel):
    error: str
