from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable, Any, Dict, Literal

q2 = Decimal("0.01")

def adjust_by_month(month: int, amount: Decimal) -> Decimal:
    if month == 12:
        return amount * Decimal("1.10")
    if month in (6, 7, 8):
        return amount * Decimal("0.95")
    return amount

def _apply_tax(total: Decimal) -> Decimal:
    # 7% deduction if total > 10,000; round to 2 decimals
    return (total * Decimal("0.93")).quantize(q2, rounding=ROUND_HALF_UP) \
           if total > Decimal("10000") else total.quantize(q2, rounding=ROUND_HALF_UP)

def compute_metrics(month_amounts: Iterable[tuple[int, Decimal]]) -> dict:
    adjusted = [adjust_by_month(m, a) for (m, a) in month_amounts]
    if not adjusted:
        return {
            "count": 0,
            "sum": Decimal("0"),
            "sumAfterTax": Decimal("0"),
            "average": Decimal("0"),
            "averageAfterTax": Decimal("0"),
            "highest": Decimal("0"),
        }

    total = sum(adjusted, start=Decimal("0"))
    highest = max(adjusted)
    total_after_tax = _apply_tax(total)

    # Keep BOTH: pre-tax average and post-tax average
    avg = (total / len(adjusted)).quantize(q2, rounding=ROUND_HALF_UP)
    avg_after_tax = (total_after_tax / len(adjusted)).quantize(q2, rounding=ROUND_HALF_UP)

    return {
        "count": len(adjusted),
        "sum": total.quantize(q2, rounding=ROUND_HALF_UP),
        "sumAfterTax": total_after_tax,              
        "average": avg,                             
        "averageAfterTax": avg_after_tax,             
        "highest": highest.quantize(q2, rounding=ROUND_HALF_UP),
    }

def status_from_average(avg: Decimal) -> str:
    if avg > Decimal("2000"):
        return "GREEN"
    if avg == Decimal("2000"):
        return "ORANGE"
    return "RED"

class ProcessStatus:
    """
    Facade exposing the existing process-status functions as class/static methods.
    Behavior is unchanged; this only satisfies the 'ProcessStatus' class naming.
    """
    @staticmethod
    def adjust_by_month(year: int, month: int, amount: Decimal) -> Decimal:
        return adjust_by_month(year, month, amount)

    @staticmethod
    def status_from_average(avg: Decimal) -> Literal["GREEN", "ORANGE", "RED"]:
        return status_from_average(avg)

    @staticmethod
    def compute_metrics(salaries: list[Dict[str, Any]]) -> Any:
        return compute_metrics(salaries)

    @classmethod
    def compute_for_national_number(cls, national_number: str):
        return compute_for_national_number(national_number)