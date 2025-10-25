from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Literal, Optional

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

class EmpInfo(BaseModel):
    """
    View model representing the employee entity for readability.
    (Persistence entity is app.models.User; this is for API/logic.)
    """
    Username: str = Field(..., alias="username")
    NationalNumber: str = Field(..., alias="national_number")
    Email: str = Field(..., alias="email")
    Phone: Optional[str] = Field(None, alias="phone")
    IsActive: bool = Field(..., alias="is_active")

    class Config:
        populate_by_name = True

class FlatGetEmpStatusResponse(BaseModel):
    # Exact success format 
    EmployeeName: str
    NationalNumber: str
    HighestSalary: float
    AverageSalary: float
    Status: Literal["GREEN", "ORANGE", "RED"]
    IsActive: bool
    LastUpdated: str  # "YYYY-MM-DDTHH:MM:SSZ"