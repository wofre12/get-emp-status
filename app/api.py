from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime, timezone
from decimal import Decimal
from .schema import GetEmpStatusRequest, FlatGetEmpStatusResponse, ErrorOut
from .data_access import DataAccess
from .validator import Validator
from .process_status import ProcessStatus
from .cache import TTLCache
from .logger import DBLogger
from .settings import settings

router = APIRouter(prefix="/api", tags=["GetEmpStatus"])
_cache = TTLCache(ttl_seconds=settings.CACHE_TTL_SECONDS)

def _cache_key(national: str) -> str:
    return f"empstatus:{national}"

@router.post("/GetEmpStatus", response_model=FlatGetEmpStatusResponse, responses={
    404: {"model": ErrorOut},
    406: {"model": ErrorOut},
    422: {"model": ErrorOut},
    401: {"model": ErrorOut},
})
async def get_emp_status(
    payload: GetEmpStatusRequest,
    data: DataAccess = Depends(lambda: router.data_access),    # type: ignore[attr-defined]
    _: None = Depends(Validator.validate_token),
    bustCache: bool = Query(default=False)
):
    national = payload.NationalNumber.strip()
    ctx = {"nationalNumber": national}
    logger: DBLogger = router.db_logger                                 # type: ignore[attr-defined]

    if not bustCache:
        cached = _cache.get(_cache_key(national))
        if cached:
            logger.log("INFO", "cache_hit", ctx)
            return cached

    user = data.get_user_by_national(national)
    if user is None:
        logger.log("WARN", "user_not_found", ctx)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid National Number")
    if not user.is_active:
        logger.log("WARN", "user_inactive", ctx)
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="User is not Active")

    rows = data.get_salaries_for_user(user.id)
    if len(rows) < 3:
        logger.log("WARN", "insufficient_salary_rows", {**ctx, "count": len(rows)})
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="INSUFFICIENT_DATA")

    month_amounts = [(r.month, Decimal(str(r.amount))) for r in rows]
    metrics = ProcessStatus.compute_metrics(month_amounts)
    status_str = ProcessStatus.status_from_average(Decimal(str(metrics["averageAfterTax"])))

    avg = float(metrics.get("averageAfterTax", metrics["average"]))
    last_updated = (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
    resp = {
        "EmployeeName": user.username,
        "NationalNumber": user.national_number,
        "HighestSalary": float(metrics["highest"]),
        "AverageSalary": round(avg, 2),
        "Status": status_str,
        "IsActive": bool(user.is_active),
        "LastUpdated": last_updated,
    }
    _cache.set(_cache_key(national), resp)
    logger.log("INFO", "success", {**ctx, "count": metrics["count"], "status": status_str})
    return resp
