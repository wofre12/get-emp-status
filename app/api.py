from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime, timezone
from decimal import Decimal
from .schema import GetEmpStatusRequest, GetEmpStatusResponse, ErrorOut, UserOut, MetricsOut
from .data_access import DataAccess
from .validator import validate_token
from .process_status import compute_metrics, status_from_average
from .cache import TTLCache
from .logger import DBLogger
from .settings import settings

router = APIRouter(prefix="/api", tags=["GetEmpStatus"])
_cache = TTLCache(ttl_seconds=settings.CACHE_TTL_SECONDS)

def _cache_key(national: str) -> str:
    return f"empstatus:{national}"

@router.post("/GetEmpStatus", response_model=GetEmpStatusResponse, responses={
    404: {"model": ErrorOut},
    406: {"model": ErrorOut},
    422: {"model": ErrorOut},
    401: {"model": ErrorOut},
})
async def get_emp_status(
    payload: GetEmpStatusRequest,
    data: DataAccess = Depends(lambda: router.data_access),    # type: ignore[attr-defined]
    _: None = Depends(validate_token),
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
    metrics = compute_metrics(month_amounts)
    status_str = status_from_average(Decimal(str(metrics["averageAfterTax"])))

    resp = GetEmpStatusResponse(
        user=UserOut(
            username=user.username,
            nationalNumber=user.national_number,
            email=user.email,
            phone=user.phone,
            isActive=user.is_active
        ),
        metrics=MetricsOut(**{k: float(v) if k != "count" else v for k, v in metrics.items()}),
        status=status_str,
        lastUpdatedUtc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    _cache.set(_cache_key(national), resp)
    logger.log("INFO", "success", {**ctx, "count": metrics["count"], "status": status_str})
    return resp
