from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable

def adjust_by_month(month: int, amount: Decimal) -> Decimal:
    if month == 12:
        return amount * Decimal('1.10')
    if month in (6, 7, 8):
        return amount * Decimal('0.95')
    return amount

def compute_metrics(month_amounts: Iterable[tuple[int, Decimal]]) -> dict:
    adjusted = [adjust_by_month(m, a) for (m, a) in month_amounts]
    if not adjusted:
        return {"count": 0, "sum": Decimal('0'), "sumAfterTax": Decimal('0'), "average": Decimal('0'), "highest": Decimal('0')}

    total = sum(adjusted, start=Decimal('0'))
    highest = max(adjusted)
    total_after_tax = total * Decimal('0.93') if total > Decimal('10000') else total
    avg = total_after_tax / Decimal(len(adjusted))
    q2 = Decimal('0.01')

    return {
        "count": len(adjusted),
        "sum": total.quantize(q2, rounding=ROUND_HALF_UP),
        "sumAfterTax": total_after_tax.quantize(q2, rounding=ROUND_HALF_UP),
        "average": avg.quantize(q2, rounding=ROUND_HALF_UP),
        "highest": highest.quantize(q2, rounding=ROUND_HALF_UP),
    }

def status_from_average(avg: Decimal) -> str:
    if avg > Decimal('2000'):
        return "GREEN"
    if avg == Decimal('2000'):
        return "ORANGE"
    return "RED"
